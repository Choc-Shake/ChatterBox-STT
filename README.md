# Chatterbox Voice To Text

Chatterbox is a lightweight, desktop voice-transcribing tool that integrates local LLM-based grammar polishing. 

## ✨ Features

- **Invisible & Unobtrusive:** Operates entirely in the system tray. Press `Ctrl+Space` to summon the minimalist 64x64px "Ready" pill interface.
- **Smart Voice Activity Detection (VAD):** The pill dynamically springs out when it detects your voice (`RMS > 500`), illuminating an animated audio waveform.
- **Auto-Silence Collapse:** Stop talking for ~1 second, and the UI elastically shrinks back down to the circular dormant state without losing your context. Complete silence for 5+ seconds triggers an auto-abort to stay out of your way.
- **Interactive Hover Menu:** Hovering over the golden active button smoothly slides out a Red Cancel button. The main button icon transitions from "Active" to "Pause". 
- **Pause & Resume:** Click the golden button mid-dictation to instantly pause and unpause the transcription listener.
- **Zero-Friction Typist:** When you finish dictating (either by pressing `Ctrl+Space` or clicking), Chatterbox sends the audio to Faster-Whisper, cleans up your "um"s and "ah"s utilizing a local Ollama model which you can configure (`qwen2.5:0.5b` by default), and automatically types the polished output string directly into whatever application you had focused!

## 🚀 Setup

### 1. The Backend (Server)
Chatterbox connects to a self-hosted AI suite (Whisper for STT, Ollama for cleaning text).

   If hosting this on a Server:
1. Copy `docker-compose.yml` to your Linux server.
2. Run `docker-compose up -d`.
3. The server will pull the required images and model files.

### 2. The Frontend (Your PC)
1. Install Python 3.10+
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: PyAudio may require C++ build tools on Windows).*
3. Run the application (working on creating an easy-to-use .exe):
   ```bash
   python chatterbox_client.py
   ```
4. Right-click the solid gold circle in your system tray to open the **Settings Menu**. Here, you can configure your server's IP address, change the hotkey, or edit the AI's internal polishing system prompts.
