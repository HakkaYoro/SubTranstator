import pysrt
from subtranslator.api_manager import APIKeyManager

def load_subtitles(file_path):
    try:
        subs = pysrt.open(file_path, encoding='utf-8')
        return subs
    except Exception as e:
        raise RuntimeError(f"Failed to load subtitles: {e}")

def validate_subtitles(subs):
    # Basic validation: check numbering and timestamps
    for sub in subs:
        if not sub.text or not sub.start or not sub.end:
            raise ValueError(f"Invalid subtitle entry: {sub.index}")
    return True

def batch_subtitles(subs, max_chars=2000, context_size=2):
    """
    Yield batches of subtitle entries as text chunks with context.
    """
    batch = []
    batch_len = 0
    for idx, sub in enumerate(subs):
        # Include previous context_size entries
        context = ''
        for offset in range(context_size, 0, -1):
            if idx - offset >= 0:
                context += subs[idx - offset].text + ' '
        entry_text = context + sub.text

        if batch_len + len(entry_text) > max_chars and batch:
            yield batch
            batch = []
            batch_len = 0

        batch.append((idx, entry_text))
        batch_len += len(entry_text)

    if batch:
        yield batch

def translate_subtitles(subs, target_lang, api_manager: APIKeyManager, model_name, censorship=False, safety_settings=None, progress_callback=None):
    """
    Translate subtitles in batches, update subs in place.
    """
    total = len(subs)
    batch_num = 0

    for batch in batch_subtitles(subs):
        batch_num += 1
        prompt = f"Translate the following subtitles into {target_lang}, preserving meaning and adapting idioms naturally:\n\n"
        for idx, text in batch:
            prompt += f"[{idx}] {text}\n"

        # Add censorship instructions if enabled
        if censorship:
            prompt += "\nCensor any NSFW or offensive content by replacing it with '####'."

        try:
            response = api_manager.call_gemini_api(
                model_name=model_name,
                prompt=prompt,
                safety_settings=safety_settings
            )
            translated_text = response.text
        except Exception as e:
            print(f"Batch {batch_num} translation failed: {e}")
            continue

        # Parse response and update subtitles
        # Assumes response returns lines like: [idx] translated text
        for line in translated_text.splitlines():
            if line.strip().startswith("[") and "]" in line:
                try:
                    idx_str = line.split("]")[0][1:]
                    idx = int(idx_str)
                    text = line.split("]", 1)[1].strip()
                    subs[idx].text = text
                except Exception:
                    continue

        if progress_callback:
            progress_callback(min(batch[-1][0]+1, total), total)

def save_translated_subs(subs, original_path, target_lang):
    base, ext = os.path.splitext(original_path)
    out_path = f"{base}_{target_lang}{ext}"
    subs.save(out_path, encoding='utf-8')
    return out_path
