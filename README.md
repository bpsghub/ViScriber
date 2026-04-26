# ViScriber

Transcribe any video file locally using Whisper — no cloud upload required.

## Quick Start (For Most Users)

1. Open the GitHub Releases page: [https://github.com/bpsghub/ViScriber/releases](https://github.com/bpsghub/ViScriber/releases)
2. Download the file for your OS:
	- Windows: `VideoTranscriber-Setup.exe`
	- macOS: `VideoTranscriber.dmg`
	- Linux: `VideoTranscriber-x86_64.AppImage`
3. Install or run it:
	- Windows: run the setup file and complete the installer
	- macOS: open the DMG and drag the app to Applications
	- Linux: make AppImage executable (`chmod +x VideoTranscriber-x86_64.AppImage`) then run it

No Python installation needed. FFmpeg is included in official release builds when available. If FFmpeg is missing, the app shows setup instructions and asks you to install it.

If the Releases page has no downloadable files yet, use the steps in [Developer Setup](#developer-setup) to run from source.

---

## First Launch (What To Expect)

On first launch, ViScriber asks you to download a Whisper model.

- This is required for offline transcription.
- The model is downloaded once and cached locally.
- Download size depends on the selected model:
  - tiny: ~75 MB (fastest, lower accuracy)
  - base: ~140 MB
  - small: ~250 MB (recommended)
  - medium: ~770 MB
  - large: ~1.5 GB (slow on CPU, best accuracy)

You need an internet connection for this first model download only.

---

## How To Use ViScriber

1. Open ViScriber.
2. Drag and drop one or more video files, or use the file picker.
3. Choose output type (`.txt`, `.srt`, or both).
4. Click Start.
5. Wait for processing to finish.
6. Use the Open/Open Folder buttons to view results.

Output files are written next to your input video by default.

---

## If Something Does Not Work

### FFmpeg not found

If ViScriber shows "FFmpeg Not Found":

- Windows: install FFmpeg from https://www.gyan.dev/ffmpeg/builds/, then add FFmpeg `bin` to your PATH and restart ViScriber.
- macOS: run `brew install ffmpeg`, then restart ViScriber.
- Linux: install FFmpeg from your distro package manager and ensure `ffmpeg` is in PATH.

### Slow transcription

- Use a smaller model (`small`, `base`, or `tiny`).
- Process fewer files at a time.
- Close other heavy apps while transcribing.

---

## Features

- Drag-and-drop video files (`.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`)
- Transcribes locally using [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — fully offline, no data leaves your machine
- Outputs `.txt` transcript and `.srt` subtitle files
- Optional AI summary via Claude, OpenAI, or local Ollama
- First launch downloads your chosen Whisper model (~75 MB–1.5 GB depending on quality)
- Dark mode UI, cross-platform (Windows / macOS / Linux)

---

## Developer Setup

FFmpeg note for developers: FFmpeg is required for audio extraction. If it is not bundled in your local build, install FFmpeg on your system and ensure the `ffmpeg` command is available in PATH.

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

## Publishing Releases (Maintainers)

This repository has GitHub Actions automation in [.github/workflows/build.yml](.github/workflows/build.yml).

### Option 1: Tag Push (recommended)

Create and push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This triggers cross-platform builds and creates a GitHub Release with attached assets.

### Option 2: Manual Run

In GitHub:

1. Open Actions.
2. Open Build & Release.
3. Click Run workflow.
4. Enter an existing tag (for example `v1.0.0`).

The workflow builds Windows installer, macOS DMG, and Linux AppImage, then publishes them on the Releases page.
