import os
import sys
import shutil
import subprocess
from pathlib import Path


def _ffmpeg_binary() -> str:
    base = Path(__file__).parent.parent.parent / "resources" / "ffmpeg"
    if sys.platform.startswith("win"):
        candidate = base / "win" / "ffmpeg.exe"
    elif sys.platform == "darwin":
        candidate = base / "mac" / "ffmpeg"
    else:
        candidate = base / "linux" / "ffmpeg"
    if candidate.exists():
        return str(candidate)
    return "ffmpeg"  # fall back to system PATH


def ffmpeg_install_guide() -> str:
    if sys.platform.startswith("win"):
        return (
            "FFmpeg is required but was not found.\n\n"
            "Install FFmpeg for Windows, then restart this app:\n"
            "1. Download a build from https://www.gyan.dev/ffmpeg/builds/\n"
            "2. Extract it and add the ffmpeg 'bin' folder to PATH\n"
            "3. Reopen Video Transcriber"
        )
    if sys.platform == "darwin":
        return (
            "FFmpeg is required but was not found.\n\n"
            "Install FFmpeg, then restart this app:\n"
            "brew install ffmpeg"
        )
    return (
        "FFmpeg is required but was not found.\n\n"
        "Install FFmpeg and ensure the 'ffmpeg' command is in PATH, then restart this app."
    )


def is_ffmpeg_available() -> bool:
    try:
        result = subprocess.run(
            [_ffmpeg_binary(), "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except (FileNotFoundError, OSError):
        return False
    return result.returncode == 0


def extract_audio(video_path: str, output_wav: str) -> None:
    if not is_ffmpeg_available():
        raise RuntimeError(ffmpeg_install_guide())
    try:
        subprocess.run(
            [_ffmpeg_binary(), "-y", "-i", video_path,
             "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
             output_wav],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        lines = e.stderr.decode("utf-8", errors="replace").strip().splitlines()
        raise RuntimeError(lines[-1] if lines else "unknown ffmpeg error") from e


def split_audio(wav_path: str, chunk_dir: str, chunk_seconds: int) -> list:
    os.makedirs(chunk_dir, exist_ok=True)
    pattern = os.path.join(chunk_dir, "chunk_%03d.wav")
    if not is_ffmpeg_available():
        raise RuntimeError(ffmpeg_install_guide())
    try:
        subprocess.run(
            [_ffmpeg_binary(), "-y", "-i", wav_path,
             "-f", "segment", "-segment_time", str(chunk_seconds),
             "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
             pattern],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        lines = e.stderr.decode("utf-8", errors="replace").strip().splitlines()
        raise RuntimeError(lines[-1] if lines else "unknown ffmpeg error") from e

    chunks = sorted(
        os.path.join(chunk_dir, f)
        for f in os.listdir(chunk_dir)
        if f.startswith("chunk_") and f.endswith(".wav")
    )
    if not chunks:
        raise RuntimeError("no chunks were generated")
    return chunks


def cleanup_chunks(chunk_dir: str) -> None:
    if os.path.exists(chunk_dir):
        shutil.rmtree(chunk_dir, ignore_errors=True)
