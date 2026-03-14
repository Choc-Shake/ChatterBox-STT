# Chatterbox Speech To Text

Chatterbox is a lightweight, ultra-premium desktop voice assistant that perfectly integrates local Speech-to-Text inference with local LLM-based grammar polishing. 

Built with **PyQt6** using a completely custom, purely absolute-positioned UI engine, Chatterbox guarantees a flawless center-anchored elastic expansion regardless of your Windows DPI scaling. It mimics high-end web CSS flexbox transitions (`cubic-bezier` physics) natively on your desktop.

## ✨ Features

- **Invisible & Unobtrusive:** Operates entirely in the system tray. Press `Ctrl+Space` to summon the minimalist 64x64px "Ready" pill interface.
- **Smart Voice Activity Detection (VAD):** The pill dynamically springs out when it detects your voice (`RMS > 500`), illuminating an animated audio waveform.
- **Auto-Silence Collapse:** Stop talking for ~1 second, and the UI elastically shrinks back down to the circular dormant state without losing your context. Complete silence for 5+ seconds triggers an auto-abort to stay out of your way.
- **Interactive Hover Menu:** Hovering over the golden active button smoothly slides out a Red Cancel button. The main button icon transitions from "Active" to "Pause". 
- **Pause & Resume:** Click the golden button mid-dictation to instantly pause and unpause the transcription listener.
- **Zero-Friction Typist:** When you finish dictating (either by pressing `Ctrl+Space` or clicking), Chatterbox sends the audio to Faster-Whisper, cleans up your "um"s and "ah"s utilizing a local Ollama model (`qwen2.5:0.5b`), and automatically types the polished output string directly into whatever application you had focused!

## 🚀 Setup

### 1. The Backend (Server)
Chatterbox connects to a self-hosted AI suite (Whisper for STT, Ollama for cleaning text).

1. Copy `docker-compose.yml` to your Linux/CasaOS server.
2. Run `docker-compose up -d`.
3. The server will pull the required images and model files.

### 2. The Frontend (Your PC)
1. Install Python 3.10+
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: PyAudio may require C++ build tools on Windows).*
3. Run the application:
   ```bash
   python chatterbox_client.py
   ```
4. Right-click the solid gold circle in your system tray to open the **Settings Menu**. Here, you can configure your server's IP address, change the hotkey, or edit the AI's internal polishing system prompts.

## 📦 Packaging (Windows .exe)
If you want to compile the Python script into a blazing fast, single, portable `.exe` file without needing a terminal open:

```bash
pyinstaller chatterbox.spec
```
The resulting executable will be available inside the `dist/` folder.

## 🎨 Design System
Chatterbox uses a strict Glassmorphism-inspired aesthetic:
- **Background:** Matte Black (`#0A0A0A`)
- **Accent/Text:** Gold (`#D4AF37`)
- **Outlines:** Subtle Dark Gold sub-pixel blends (`#33290D`)
- **Gradients & Shadows:** Heavy, smooth 100px blur radius drop shadows to provide a "floating" Z-axis depth array.
