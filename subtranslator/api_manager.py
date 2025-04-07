import os
import time
import datetime
import google.generativeai as genai
from subtranslator.config_manager import load_keys_data, save_keys_data

class APIKeyManager:
    def __init__(self):
        self.current_index = 0
        self.api_keys = []
        self.key_meta = {}  # key: metadata dict
        self.load_keys()

    def load_keys(self):
        data = load_keys_data()
        self.api_keys = data.get("api_keys", [])
        self.key_meta = data.get("key_meta", {})
        # Initialize metadata
        for key in self.api_keys:
            if key not in self.key_meta:
                self.key_meta[key] = {
                    "success": 0,
                    "fail": 0,
                    "last_used": None,
                    "cooldown_until": None,
                    "valid": None
                }

    def save_keys(self):
        data = {
            "api_keys": self.api_keys,
            "key_meta": self.key_meta
        }
        save_keys_data(data)

    def mask_key(self, key):
        if len(key) < 10:
            return key
        return key[:6] + "*****" + key[-4:]

    def list_keys(self):
        return [
            {
                "masked": self.mask_key(k),
                "valid": self.key_meta.get(k, {}).get("valid"),
                "success": self.key_meta.get(k, {}).get("success", 0),
                "fail": self.key_meta.get(k, {}).get("fail", 0),
                "last_used": self.key_meta.get(k, {}).get("last_used"),
                "cooldown_until": self.key_meta.get(k, {}).get("cooldown_until")
            }
            for k in self.api_keys
        ]

    def validate_key(self, key):
        try:
            genai.configure(api_key=key)
            models = genai.list_models()
            # If any models returned, key is valid
            if models:
                return True
            return False
        except Exception as e:
            msg = str(e).lower()
            if "permission" in msg or "unauthorized" in msg or "invalid" in msg:
                return False
            # Network error, quota, or other: accept optimistically
            return True

    def add_key(self, key):
        if key in self.api_keys:
            return False
        if not self.validate_key(key):
            return False
        self.api_keys.append(key)
        self.key_meta[key] = {
            "success": 0,
            "fail": 0,
            "last_used": None,
            "cooldown_until": None,
            "valid": True
        }
        self.save_keys()
        return True

    def remove_key(self, key_or_prefix):
        to_remove = None
        for k in self.api_keys:
            if k == key_or_prefix or k.startswith(key_or_prefix):
                to_remove = k
                break
        if to_remove:
            self.api_keys.remove(to_remove)
            self.key_meta.pop(to_remove, None)
            self.save_keys()
            return True
        return False

    def get_next_key(self):
        if not self.api_keys:
            raise RuntimeError("No API keys configured.")
        start_idx = self.current_index
        while True:
            key = self.api_keys[self.current_index]
            meta = self.key_meta.get(key, {})
            cooldown_until = meta.get("cooldown_until")
            now = datetime.datetime.utcnow().timestamp()
            if not cooldown_until or now > cooldown_until:
                self.current_index = (self.current_index + 1) % len(self.api_keys)
                return key
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            if self.current_index == start_idx:
                raise RuntimeError("All API keys are in cooldown.")

    def record_success(self, key):
        meta = self.key_meta.get(key, {})
        meta["success"] = meta.get("success", 0) + 1
        meta["last_used"] = datetime.datetime.utcnow().isoformat()
        meta["cooldown_until"] = None
        self.key_meta[key] = meta
        self.save_keys()

    def record_failure(self, key, error_type=None):
        meta = self.key_meta.get(key, {})
        meta["fail"] = meta.get("fail", 0) + 1
        meta["last_used"] = datetime.datetime.utcnow().isoformat()
        # If rate limit or auth error, cooldown 1 hour
        if error_type in ("quota", "auth"):
            meta["cooldown_until"] = datetime.datetime.utcnow().timestamp() + 3600
        self.key_meta[key] = meta
        self.save_keys()

    def call_gemini_api(self, model_name, prompt, safety_settings=None, max_retries=None):
        """
        Call Gemini API with key rotation and exponential backoff.
        """
        if not self.api_keys:
            raise RuntimeError("No API keys configured.")

        retries = 0
        max_retries = max_retries or (3 * len(self.api_keys))
        delay = 1

        for attempt in range(max_retries):
            key = self.get_next_key()
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    safety_settings=safety_settings or [],
                )
                self.record_success(key)
                return response
            except Exception as e:
                err_msg = str(e).lower()
                if "quota" in err_msg:
                    self.record_failure(key, "quota")
                elif "auth" in err_msg:
                    self.record_failure(key, "auth")
                else:
                    self.record_failure(key, "network")
                print(f"[API] Error with key {self.mask_key(key)}: {e}")
                time.sleep(delay)
                delay = min(delay * 2, 30)

        raise RuntimeError("All API keys failed after retries.")

    def fetch_gemini_models(self):
        """
        Fetch available Gemini models using the first valid key.
        """
        if not self.api_keys:
            raise RuntimeError("No API keys configured.")

        for key in self.api_keys:
            try:
                genai.configure(api_key=key)
                models = genai.list_models()
                gemini_models = [m for m in models if "gemini" in m.name]
                return gemini_models
            except Exception:
                continue

        raise RuntimeError("Failed to fetch models with all API keys.")
