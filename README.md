# ViScriber

Transcribe any video file locally using Whisper — no Python, no ffmpeg, no cloud upload required.

## Download

| Platform | Installer |
|----------|-----------|
| Windows | Download `VideoTranscriber-Setup.exe` from [Releases](../../releases) |
| macOS | Download `VideoTranscriber.dmg` from [Releases](../../releases) |
| Linux | Download `VideoTranscriber-x86_64.AppImage` from [Releases](../../releases) and `chmod +x` it |

No Python or ffmpeg installation needed — everything is bundled.

---

## Features

- Drag-and-drop video files (`.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`)
- Transcribes locally using [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — fully offline, no data leaves your machine
- Outputs `.txt` transcript and `.srt` subtitle files
- Optional AI summary via Claude, OpenAI, or local Ollama
- First launch downloads your chosen Whisper model (~75 MB–1.5 GB depending on quality)
- Dark mode UI, cross-platform (Windows / macOS / Linux)

---

## Dev Setup

```bash
git clone https://github.com/bpsghub/ViScriber.git
cd ViScriber
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
python -m src.main
```

Run tests:
```bash
python -m pytest tests/ -v
```

Build standalone executable:
```bash
pyinstaller videotranscriber.spec
```
