# Chatterbox: Deployment & Usage Guide

Welcome to Chatterbox! This guide will walk you through deploying the self-hosted AI backend and setting up the Python client for global dictation.

## Prerequisites

- **Backend:** A server or computer with Docker and Docker Compose installed (e.g., CasaOS).
- **Frontend:** A computer with Python 3.8+ installed and a working microphone.

---

## Step 1: Deploy the Backend (Server)

The backend consists of Faster-Whisper (for audio transcription) and Ollama (for text correction).

### Option A: CPU-Only (Default / CasaOS)

Perfect for older hardware like a 2015 MacBook Pro running CasaOS.

1. Copy the `docker-compose.yml` file to your server.
   - _CasaOS Users:_ You can click the "+" icon in the CasaOS dashboard, select "Install a customized app", and paste the contents of `docker-compose.yml` into the import window.
2. Run the following command in your terminal:
   ```bash
   docker-compose up -d
   ```
3. **Wait a few minutes.** The Ollama container will automatically download the `qwen2.5:0.5b` micro-model in the background.

### Option B: Nvidia GPU (Ngl i haven't tested this yet lol)

If your server has an Nvidia GPU and the Nvidia Container Toolkit installed:

1. Copy the `docker-compose-gpu.yml` file to your server.
2. Run:
   ```bash
   docker-compose -f docker-compose-gpu.yml up -d
   ```

---

## Step 2: Setup the Frontend Client (Your Computer)

This is the computer where you will actually be typing and speaking.

1. **Download the client files:**
   Ensure you have `chatterbox_client.py`, `config.json`, and `requirements.txt` in the same folder.

2. **Install System Audio Dependencies (If needed):**
   The `PyAudio` library requires system-level audio headers.
   - **Windows:** Usually installs fine via pip.
   - **macOS:** `brew install portaudio`
   - **Linux (Ubuntu/Debian):** `sudo apt-get install portaudio19-dev python3-pyaudio`

3. **Install Python Dependencies:**
   Open your terminal/command prompt in the folder containing the files and run:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure `config.json`:**
   Open `config.json` in a text editor.
   - If your backend is running on a _different_ computer (e.g., a CasaOS server), change `localhost` to your server's local IP address (e.g., `192.168.1.100`).
     ```json
     "whisper_api_url": "http://192.168.1.100:8000/v1/audio/transcriptions",
     "ollama_api_url": "http://192.168.1.100:11434/api/generate"
     ```
   - _(Optional)_ If you want to use Gemini with Search Grounding instead of local Ollama, set `"use_gemini_search_grounding": true` and paste your API key into `"gemini_api_key"`.

---

## Step 3: Usage

1. **Run the script:**

   ```bash
   python chatterbox_client.py
   ```

   _Note for macOS/Linux users:_ The `keyboard` library requires root privileges to listen to global hotkeys. You may need to run it with `sudo`:

   ```bash
   sudo python3 chatterbox_client.py
   ```

2. **Dictate:**
   - Click into any application where you want to type (Word, Chrome, Discord, etc.).
   - **Press** Ctrl + Alt + Space once to start. (or your configured hotkey). The black and gold pill will appear and show your text in real-time.
   - Speak your sentence (e.g., "Um, hey guys, ah, I'll be there in like five minutes.").
     **Finish:**
   - Press Ctrl + Alt + Space again to stop. Chatterbox will automatically polish your grammar and paste the text for you..

3. **Magic:**
   The script will transcribe your audio, fix the grammar, remove the filler words, and automatically type the corrected text ("Hey guys, I'll be there in five minutes.") directly into your active window!
"# ChatterBox-STT" 
