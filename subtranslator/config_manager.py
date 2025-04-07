import os
import json
import tempfile
import shutil

CONFIG_DIR = os.path.expanduser("~/.config/subtranslator")
KEYS_FILE = os.path.join(CONFIG_DIR, "keys.json")
LOG_FILE = os.path.join(CONFIG_DIR, "subtranslator.log")

# Encryption toggle (stub for now)
ENCRYPTION_ENABLED = False

def ensure_config():
    """Ensure config directory and keys file exist with correct permissions."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "w") as f:
            json.dump({"api_keys": []}, f, indent=2)
        os.chmod(KEYS_FILE, 0o600)
    else:
        # Enforce permissions
        os.chmod(KEYS_FILE, 0o600)

def atomic_write_json(path, data):
    """Atomically write JSON data to a file."""
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name)
    try:
        with os.fdopen(fd, 'w') as tmp_file:
            json.dump(data, tmp_file, indent=2)
        os.replace(tmp_path, path)
        os.chmod(path, 0o600)
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise

def load_keys_data():
    ensure_config()
    with open(KEYS_FILE, "r") as f:
        data = json.load(f)
    return data

def save_keys_data(data):
    ensure_config()
    atomic_write_json(KEYS_FILE, data)

def get_keys_file():
    ensure_config()
    return KEYS_FILE

def get_log_file():
    ensure_config()
    return LOG_FILE
