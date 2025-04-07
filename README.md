# 🎬 SubTranslator: AI-Powered Subtitle Localization

**SubTranslator** is a Python CLI and TUI tool for translating `.srt` subtitle files using Google’s Gemini AI models.

---

## ✨ Features

- 🖥️ **Text-based UI** with arrow-key navigation
- 🌐 **Multi-language support** (ISO 639-1 codes)
- 🔄 **API key rotation** to avoid rate limits
- ⚠️ **NSFW censorship toggle**
- 🤖 **Fetch & select Gemini models** dynamically
- ✂️ **Chunked translation** with automatic splitting
- 📝 **Merges parts** into a single output file
- 🔐 **Secure API key storage** (planned)
- 📊 **Real-time progress display**

---

## 💻 Installation

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### Recommended (Linux)

```bash
./start.sh
```

### Windows

```bash
python -m subtranslator.main
```

### MacOS

```bash
python3 -m subtranslator.main
```

- Use the TUI to select input file, target language, censorship, API keys, and model.
- Start translation from the menu.

---

## 🔑 API Keys

- Store your Google AI Studio API keys in `~/.config/subtranslator/keys.json`.
- Manage keys via the TUI.
- **Do NOT commit your API keys.**

---

## ⚡ Gemini Model Requirement

- For **uncensored translation**, you **must use the `gemini-2.0-flash-exp` model**.
- Other models may apply stricter content filters and block NSFW content.

---

## 📂 Folder Structure

- `Input/` — Place your original `.srt` files here.
- `Temp/` — Temporary chunk files during translation (auto-cleaned).
- `Output/` — Final merged translated `.srt` files.

---

## 🛠️ To-Do

- 🔐 **Encrypt API keys at rest**
- 🗝️ **Passphrase-protected key storage**
- 🧪 **Batch mode CLI**
- 🧹 **Better error handling and retries**
- 🌍 **Localization for other languages**
- 🧩 **Plugin system for other AI providers**
- 🧰 **Unit tests and CI integration**

---

## 📄 License

MIT License

---

## 🤝 Contributing

Pull requests welcome! Please follow PEP-8 and include docstrings.
