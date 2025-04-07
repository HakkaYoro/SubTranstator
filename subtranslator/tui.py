import curses

MENU_ITEMS = [
    "Select subtitle file",
    "Choose target language",
    "Censorship Settings",
    "Manage API keys",
    "Fetch available Gemini models",
    "Start translation",
    "Exit"
]

def draw_menu(stdscr, selected_idx, state):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Show selected file if any
    selected_file = state.get('input_file')
    if selected_file:
        import os
        filename = os.path.basename(selected_file)
        stdscr.addstr(0, 2, f"Selected file: {filename}", curses.A_BOLD)

    # Show selected language if any
    target_lang = state.get('target_language')
    if target_lang:
        stdscr.addstr(0, 30, f"Target language: {target_lang}", curses.A_BOLD)

    # Show selected model if any
    model_name = state.get('model_name')
    if model_name:
        stdscr.addstr(0, 60, f"Model: {model_name}", curses.A_BOLD)

    title = "SubTranslator"
    stdscr.addstr(1, w//2 - len(title)//2, title, curses.A_BOLD)

    for idx, item in enumerate(MENU_ITEMS):
        x = w//2 - len(item)//2
        y = 3 + idx
        if idx == selected_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, item)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, item)

    stdscr.refresh()

import os

def select_subtitle_file(stdscr, state):
    input_dir = os.path.join(os.getcwd(), "Input")
    if not os.path.isdir(input_dir):
        os.makedirs(input_dir, exist_ok=True)

    files = [f for f in os.listdir(input_dir) if f.endswith('.srt')]
    if not files:
        stdscr.clear()
        stdscr.addstr(2, 2, "No .srt files found in 'Input/' folder.")
        stdscr.refresh()
        stdscr.getch()
        return

    selected_idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "Select a subtitle file from 'Input/':", curses.A_BOLD)
        for idx, filename in enumerate(files):
            y = 3 + idx
            if idx == selected_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, 4, filename)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, 4, filename)
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(files) - 1:
            selected_idx += 1
        elif key in [curses.KEY_ENTER, ord('\n'), ord(' ')]:
            chosen_file = os.path.join(input_dir, files[selected_idx])
            state['input_file'] = chosen_file
            stdscr.clear()
            stdscr.addstr(2, 2, f"Selected: {files[selected_idx]}")
            stdscr.refresh()
            stdscr.getch()
            break
        elif key == 27:  # ESC
            break

def choose_target_language(stdscr, state):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(2, 2, "Enter the target language (e.g., Spanish, French, Japanese):")
    stdscr.refresh()

    input_win = curses.newwin(1, 40, 4, 2)
    curses.curs_set(1)
    box = ''
    while True:
        input_win.clear()
        input_win.addstr(0, 0, box)
        input_win.refresh()
        ch = stdscr.getch()
        if ch in (curses.KEY_ENTER, ord('\n')):
            if box.strip():
                state['target_language'] = box.strip()
            break
        elif ch == 27:  # ESC
            break
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            box = box[:-1]
        elif 32 <= ch <= 126:
            box += chr(ch)

    curses.curs_set(0)
    curses.noecho()

def toggle_censorship(stdscr, state):
    state['censorship'] = not state.get('censorship', False)
    stdscr.clear()
    status = "enabled" if state['censorship'] else "disabled"
    stdscr.addstr(2, 2, f"NSFW censorship {status}.")
    stdscr.refresh()
    stdscr.getch()

from subtranslator.api_manager import APIKeyManager

import json

def censorship_settings_menu(stdscr, state):
    config_path = os.path.expanduser("~/.config/subtranslator/censor_list.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    # Load or init banned words
    try:
        with open(config_path, "r") as f:
            data = json.load(f)
            words = data.get("words", [])
    except:
        words = []
    state.setdefault('censorship_enabled', False)
    state.setdefault('censorship_mode', 'ai')
    state.setdefault('censorship_level', 'medium')

    menu_items = ["Censorship?", "Mode: AI", "Mode: Local", "Censorship AI Level", "Edit Banned Words", "Back"]
    selected_idx = 0

    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "Censorship Settings", curses.A_BOLD)
        for idx, item in enumerate(menu_items):
            y = 3 + idx
            label = item
            if item.startswith("Censorship?"):
                label = f"Censorship? [{'Yes' if state.get('censorship_enabled', False) else 'No'}]"
            elif item.startswith("Mode: AI"):
                label = f"Mode: AI [{'X' if state.get('censorship_mode')=='ai' else ' '}]"
            elif item.startswith("Mode: Local"):
                label = f"Mode: Local [{'X' if state.get('censorship_mode')=='local' else ' '}]"
            elif item.startswith("Censorship AI Level"):
                label = f"Censorship AI Level: {state.get('censorship_level','medium').capitalize()}"
            elif item.startswith("Edit Banned Words"):
                label = "Edit Banned Words"
            elif item == "Back":
                label = "Back"

            if idx == selected_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, 4, label)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, 4, label)
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(menu_items) - 1:
            selected_idx += 1
        elif key in [curses.KEY_ENTER, ord('\n'), ord(' ')]:
            choice = menu_items[selected_idx]
            if choice.startswith("Censorship?"):
                state['censorship_enabled'] = not state.get('censorship_enabled', False)
            elif choice.startswith("Mode: AI"):
                state['censorship_mode'] = 'ai'
            elif choice.startswith("Mode: Local"):
                # Show warning popup
                stdscr.clear()
                stdscr.addstr(2, 2, "Local filtering lacks context awareness. Proceed? (Y/N)")
                stdscr.refresh()
                c = stdscr.getch()
                if c in (ord('y'), ord('Y')):
                    state['censorship_mode'] = 'local'
                else:
                    continue
            elif choice.startswith("Censorship AI Level"):
                level_options = ["low", "medium", "high"]
                current = level_options.index(state.get('censorship_level', 'medium'))
                next_level = (current + 1) % len(level_options)
                state['censorship_level'] = level_options[next_level]
            elif choice.startswith("Edit Banned Words"):
                edit_banned_words_menu(stdscr, words, config_path)
            elif choice == "Back":
                break
        elif key == 27:  # ESC
            break

def edit_banned_words_menu(stdscr, words, config_path):
    menu_items = ["Add Word", "Remove Word", "Back"]
    selected_idx = 0

    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "Edit Banned Words", curses.A_BOLD)
        for idx, item in enumerate(menu_items):
            y = 3 + idx
            if idx == selected_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, 4, item)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, 4, item)

        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(menu_items) - 1:
            selected_idx += 1
        elif key in [curses.KEY_ENTER, ord('\n'), ord(' ')]:
            choice = menu_items[selected_idx]
            if choice == "Add Word":
                curses.echo()
                stdscr.clear()
                stdscr.addstr(2, 2, "Enter word to censor:")
                stdscr.refresh()
                input_win = curses.newwin(1, 30, 4, 2)
                curses.curs_set(1)
                box = ''
                while True:
                    input_win.clear()
                    input_win.addstr(0, 0, box)
                    input_win.refresh()
                    ch = stdscr.getch()
                    if ch in (curses.KEY_ENTER, ord('\n')):
                        word = box.strip()
                        if word and word not in words:
                            words.append(word)
                            with open(config_path, "w") as f:
                                json.dump({"words": words}, f, indent=2)
                        break
                    elif ch == 27:
                        break
                    elif ch in (curses.KEY_BACKSPACE, 127, 8):
                        box = box[:-1]
                    elif 32 <= ch <= 126:
                        box += chr(ch)
                curses.curs_set(0)
                curses.noecho()
            elif choice == "Remove Word":
                if not words:
                    continue
                idx_rm = 0
                while True:
                    stdscr.clear()
                    stdscr.addstr(1, 2, "Select word to remove:", curses.A_BOLD)
                    for idxw, word in enumerate(words):
                        y = 3 + idxw
                        if idxw == idx_rm:
                            stdscr.attron(curses.color_pair(1))
                            stdscr.addstr(y, 4, word)
                            stdscr.attroff(curses.color_pair(1))
                        else:
                            stdscr.addstr(y, 4, word)
                    stdscr.refresh()
                    ch = stdscr.getch()
                    if ch == curses.KEY_UP and idx_rm > 0:
                        idx_rm -= 1
                    elif ch == curses.KEY_DOWN and idx_rm < len(words) - 1:
                        idx_rm += 1
                    elif ch in [curses.KEY_ENTER, ord('\n'), ord(' ')]:
                        del words[idx_rm]
                        with open(config_path, "w") as f:
                            json.dump({"words": words}, f, indent=2)
                        break
                    elif ch == 27:
                        break
            elif choice == "Back":
                break
        elif key == 27:
            break

def manage_api_keys(stdscr, api_manager):
    menu_items = ["List Keys", "Add Key", "Remove Key", "Back"]
    selected_idx = 0

    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "Manage API Keys", curses.A_BOLD)
        for idx, item in enumerate(menu_items):
            y = 3 + idx
            if idx == selected_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, 4, item)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, 4, item)
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(menu_items) - 1:
            selected_idx += 1
        elif key in [curses.KEY_ENTER, ord('\n'), ord(' ')]:
            choice = menu_items[selected_idx]
            if choice == "Back":
                break
            elif choice == "List Keys":
                list_api_keys(stdscr, api_manager)
            elif choice == "Add Key":
                add_api_key(stdscr, api_manager)
            elif choice == "Remove Key":
                remove_api_key(stdscr, api_manager)
        elif key == 27:  # ESC
            break

def list_api_keys(stdscr, api_manager):
    keys = api_manager.list_keys()
    stdscr.clear()
    stdscr.addstr(1, 2, "API Keys:", curses.A_BOLD)
    for idx, info in enumerate(keys):
        y = 3 + idx
        masked = info['masked']
        valid = info['valid']
        success = info['success']
        fail = info['fail']
        cooldown = info['cooldown_until']
        status = "valid" if valid else "invalid"
        stdscr.addstr(y, 2, f"{idx+1}. {masked} [{status}] S:{success} F:{fail} Cooldown:{cooldown}")
    stdscr.addstr(y+2, 2, "Press any key to return.")
    stdscr.refresh()
    stdscr.getch()

def add_api_key(stdscr, api_manager):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(2, 2, "Enter new API key:")
    stdscr.refresh()
    input_win = curses.newwin(1, 60, 4, 2)
    curses.curs_set(1)
    box = ''
    while True:
        input_win.clear()
        input_win.addstr(0, 0, box)
        input_win.refresh()
        ch = stdscr.getch()
        if ch in (curses.KEY_ENTER, ord('\n')):
            key = box.strip()
            if key:
                success = api_manager.add_key(key)
                stdscr.clear()
                if success:
                    stdscr.addstr(2, 2, "API key added successfully.")
                else:
                    stdscr.addstr(2, 2, "Invalid or duplicate API key.")
                stdscr.refresh()
                stdscr.getch()
            break
        elif ch == 27:  # ESC
            break
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            box = box[:-1]
        elif 32 <= ch <= 126:
            box += chr(ch)
    curses.curs_set(0)
    curses.noecho()

def remove_api_key(stdscr, api_manager):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(2, 2, "Enter key prefix or index to remove:")
    stdscr.refresh()
    input_win = curses.newwin(1, 30, 4, 2)
    curses.curs_set(1)
    box = ''
    while True:
        input_win.clear()
        input_win.addstr(0, 0, box)
        input_win.refresh()
        ch = stdscr.getch()
        if ch in (curses.KEY_ENTER, ord('\n')):
            query = box.strip()
            if query:
                # Try index first
                removed = False
                try:
                    idx = int(query) - 1
                    keys = api_manager.api_keys
                    if 0 <= idx < len(keys):
                        removed = api_manager.remove_key(keys[idx])
                except:
                    removed = api_manager.remove_key(query)
                stdscr.clear()
                if removed:
                    stdscr.addstr(2, 2, "API key removed.")
                else:
                    stdscr.addstr(2, 2, "Key not found.")
                stdscr.refresh()
                stdscr.getch()
            break
        elif ch == 27:  # ESC
            break
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            box = box[:-1]
        elif 32 <= ch <= 126:
            box += chr(ch)
    curses.curs_set(0)
    curses.noecho()

def fetch_gemini_models(stdscr, api_manager, state):
    stdscr.clear()
    stdscr.addstr(2, 2, "Fetching available Gemini models...")
    stdscr.refresh()
    try:
        models = api_manager.fetch_gemini_models()
        model_names = [m.name for m in models]
    except Exception as e:
        stdscr.clear()
        stdscr.addstr(2, 2, f"Error fetching models: {e}")
        stdscr.refresh()
        stdscr.getch()
        return

    if not model_names:
        stdscr.clear()
        stdscr.addstr(2, 2, "No Gemini models found.")
        stdscr.refresh()
        stdscr.getch()
        return

    selected_idx = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(1, 2, "Select a Gemini model:", curses.A_BOLD)
        for idx, name in enumerate(model_names):
            y = 3 + idx
            if y >= h - 1:
                break  # avoid drawing outside screen
            display_name = name
            max_len = w - 6
            if len(display_name) > max_len:
                display_name = display_name[:max_len - 3] + "..."
            if idx == selected_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, 4, display_name)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, 4, display_name)
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(model_names) - 1:
            selected_idx += 1
        elif key in [curses.KEY_ENTER, ord('\n'), ord(' ')]:
            state['model_name'] = model_names[selected_idx]
            stdscr.clear()
            stdscr.addstr(2, 2, f"Selected model: {model_names[selected_idx]}")
            stdscr.refresh()
            stdscr.getch()
            break
        elif key == 27:  # ESC
            break

import pysrt

def start_translation(stdscr, api_manager, state):
    stdscr.clear()

    input_file = state.get('input_file')
    target_lang = state.get('target_language')
    model_name = state.get('model_name')

    if not input_file or not target_lang or not model_name:
        stdscr.addstr(2, 2, "Please select subtitle file, target language, and model first.")
        stdscr.refresh()
        stdscr.getch()
        return

    try:
        subs = pysrt.open(input_file, encoding='utf-8')
    except Exception as e:
        stdscr.addstr(2, 2, f"Error loading subtitles: {e}")
        stdscr.refresh()
        stdscr.getch()
        return

    temp_dir = os.path.join(os.getcwd(), "Temp")
    output_dir = os.path.join(os.getcwd(), "Output")
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    total = len(subs)
    chunks = [subs[i:i+10] for i in range(0, total, 10)]
    part_files = []
    import time
    times = []
    total_chunks = len(chunks)

    for idx, chunk in enumerate(chunks):
        stdscr.clear()

        # Progress bar
        bar_width = 40
        progress = (idx) / total_chunks
        filled = int(bar_width * progress)
        bar = "[" + "#" * filled + "-" * (bar_width - filled) + "]"

        # ETA and debug info
        if times:
            avg_time = sum(times) / len(times)
            eta_seconds = int(avg_time * (total_chunks - idx))
            eta_min = eta_seconds // 60
            eta_sec = eta_seconds % 60
            eta_str = f"{eta_min}m {eta_sec}s"
            last_time = times[-1]
            last_str = f"{last_time:.1f}s"
            avg_str = f"{avg_time:.1f}s"
        else:
            eta_str = "Calculating..."
            last_str = "-"
            avg_str = "-"

        stdscr.addstr(2, 2, f"Translating chunk {idx+1}/{total_chunks}")
        stdscr.addstr(3, 2, bar)
        stdscr.addstr(4, 2, f"ETA: {eta_str}")
        stdscr.addstr(5, 2, f"Chunks timed: {len(times)}")
        stdscr.addstr(6, 2, f"Last chunk: {last_str}")
        stdscr.addstr(7, 2, f"Avg chunk: {avg_str}")
        stdscr.refresh()

        chunk_start = time.time()

        # Renumber chunk subtitles from 1 upwards
        for i, sub in enumerate(chunk, start=1):
            sub.index = i

        if state.get('censorship_enabled'):
            level = state.get('censorship_level', 'medium')
            if level == 'low':
                prompt = (
                    f"Translate the following subtitles into {target_lang}.\n\n"
                    "- Replace only highly offensive or explicit terms with polite equivalents.\n"
                    "- Preserve humor, tone, and mild slang.\n"
                    "- Do NOT include explanations or alternatives.\n"
                    "- Keep the numbering format: [number] translated text.\n"
                    "- Do not output anything else.\n\n"
                )
            elif level == 'medium':
                prompt = (
                    f"Translate the following subtitles into {target_lang}.\n\n"
                    "- Replace explicit, offensive, or suggestive language with polite or neutral terms.\n"
                    "- Maintain overall tone but avoid inappropriate content.\n"
                    "- Do NOT include explanations or alternatives.\n"
                    "- Keep the numbering format: [number] translated text.\n"
                    "- Do not output anything else.\n\n"
                )
            elif level == 'high':
                prompt = (
                    f"Translate the following subtitles into {target_lang}.\n\n"
                    "- Aggressively censor all NSFW, offensive, or suggestive language.\n"
                    "- Replace with family-friendly, polite expressions.\n"
                    "- Maintain timing and formatting.\n"
                    "- Do NOT include explanations or alternatives.\n"
                    "- Keep the numbering format: [number] translated text.\n"
                    "- Do not output anything else.\n\n"
                )
            else:
                prompt = ""
        else:
            prompt = (
                f"Translate the following subtitles into {target_lang}.\n\n"
                "- Provide ONLY ONE natural, idiomatic translation per line.\n"
                "- Do NOT include explanations, alternatives, or comments.\n"
                "- Keep the numbering format: [number] translated text.\n"
                "- If unsure, pick the most neutral, natural-sounding translation.\n"
                "- Do not output anything else.\n\n"
            )
        for sub in chunk:
            prompt += f"[{sub.index}] {sub.text}\n"

        try:
            response = api_manager.call_gemini_api(
                model_name=model_name,
                prompt=prompt
            )
            translated_text = response.text
        except Exception as e:
            stdscr.addstr(4, 2, f"Error: {e}")
            stdscr.refresh()
            stdscr.getch()
            continue

        elapsed = time.time() - chunk_start
        times.append(elapsed)

        # Parse response and update chunk
        for line in translated_text.splitlines():
            if line.strip().startswith("[") and "]" in line:
                try:
                    idx_str = line.split("]")[0][1:]
                    idx_num = int(idx_str)
                    text = line.split("]", 1)[1].strip()
                    for sub in chunk:
                        if sub.index == idx_num:
                            sub.text = text
                            break
                except:
                    continue

        # Save translated chunk to Temp/
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        out_path = os.path.join(temp_dir, f"{base_name}_translated_part{idx+1}.srt")
        chunk.save(out_path, encoding='utf-8')
        part_files.append(out_path)

    # Merge parts into one .srt in Output/
    merged_subs = pysrt.SubRipFile()
    counter = 1
    for part_file in part_files:
        part_subs = pysrt.open(part_file, encoding='utf-8')
        for sub in part_subs:
            sub.index = counter
            merged_subs.append(sub)
            counter += 1

    final_out_path = os.path.join(output_dir, f"{base_name}_translated.srt")
    merged_subs.save(final_out_path, encoding='utf-8')

    # Clean up Temp/ .srt files
    for f in part_files:
        try:
            os.remove(f)
        except:
            pass

    stdscr.clear()
    stdscr.addstr(2, 2, f"Translation complete. Final file saved as:")
    h, w = stdscr.getmaxyx()
    truncated = final_out_path
    max_len = w - 8
    if len(truncated) > max_len:
        truncated = truncated[:max_len - 3] + "..."
    stdscr.addstr(4, 4, truncated)
    stdscr.refresh()
    stdscr.getch()

def main_menu(stdscr, api_manager):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    selected_idx = 0
    state = {}

    while True:
        draw_menu(stdscr, selected_idx, state)
        key = stdscr.getch()

        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(MENU_ITEMS) -1:
            selected_idx += 1
        elif key in [curses.KEY_ENTER, ord('\n'), ord(' ')]:
            label = MENU_ITEMS[selected_idx]
            if label == "Exit":
                break
            elif label == "Select subtitle file":
                select_subtitle_file(stdscr, state)
            elif label == "Choose target language":
                choose_target_language(stdscr, state)
            elif label == "Censorship Settings":
                censorship_settings_menu(stdscr, state)
            elif label == "Manage API keys":
                manage_api_keys(stdscr, api_manager)
            elif label == "Fetch available Gemini models":
                fetch_gemini_models(stdscr, api_manager, state)
            elif label == "Start translation":
                start_translation(stdscr, api_manager, state)
        elif key == 27:  # ESC key
            break

def launch_tui():
    from subtranslator.api_manager import APIKeyManager
    api_manager = APIKeyManager()
    curses.wrapper(main_menu, api_manager)
