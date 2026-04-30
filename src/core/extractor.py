import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path


_FFMPEG_USER_DIR = Path.home() / ".videoscribe" / "ffmpeg"
_FFMPEG_WINDOWS_DOWNLOAD_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def _bundled_ffmpeg_binary() -> Path:
    base = Path(__file__).parent.parent.parent / "resources" / "ffmpeg"
    if sys.platform.startswith("win"):
        return base / "win" / "ffmpeg.exe"
    if sys.platform == "darwin":
        return base / "mac" / "ffmpeg"
    return base / "linux" / "ffmpeg"


def _installed_ffmpeg_binary() -> Path:
    if sys.platform.startswith("win"):
        return _FFMPEG_USER_DIR / "win" / "ffmpeg.exe"
    if sys.platform == "darwin":
        return _FFMPEG_USER_DIR / "mac" / "ffmpeg"
    return _FFMPEG_USER_DIR / "linux" / "ffmpeg"


def _ffmpeg_binary() -> str:
    bundled = _bundled_ffmpeg_binary()
    if bundled.exists():
        return str(bundled)

    installed = _installed_ffmpeg_binary()
    if installed.exists():
        return str(installed)

    return "ffmpeg"  # fall back to system PATH


def _download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, open(destination, "wb") as file_obj:
        shutil.copyfileobj(response, file_obj)


def _extract_windows_ffmpeg(archive_path: Path, install_dir: Path) -> Path:
    install_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.namelist():
            lower_name = member.lower()
            if lower_name.endswith("/bin/ffmpeg.exe") or lower_name.endswith("/bin/ffprobe.exe"):
                target = install_dir / Path(member).name
                target.write_bytes(archive.read(member))

    ffmpeg_path = install_dir / "ffmpeg.exe"
    if not ffmpeg_path.exists():
        raise RuntimeError("FFmpeg download completed, but ffmpeg.exe was not found in the archive.")
    return ffmpeg_path


def download_ffmpeg_windows(install_dir: Path | None = None) -> str:
    if not sys.platform.startswith("win"):
        raise RuntimeError("Automatic FFmpeg installation is only available on Windows.")

    target_dir = Path(install_dir) if install_dir is not None else (_FFMPEG_USER_DIR / "win")
    archive_path = target_dir.parent / "ffmpeg-download.zip"
    try:
        _download_file(_FFMPEG_WINDOWS_DOWNLOAD_URL, archive_path)
        ffmpeg_path = _extract_windows_ffmpeg(archive_path, target_dir)
        return str(ffmpeg_path)
    finally:
        try:
            archive_path.unlink(missing_ok=True)
        except OSError:
            pass


def ffmpeg_install_guide() -> str:
    if sys.platform.startswith("win"):
        return (
            "FFmpeg is required but was not found.\n\n"
            "You can install it automatically during first launch in ViScriber, or do it manually:\n"
            "1. Open ViScriber and use the first-run FFmpeg installer\n"
            "2. Or download a build from https://www.gyan.dev/ffmpeg/builds/\n"
            "3. Extract it and add the ffmpeg 'bin' folder to PATH\n"
            "4. Reopen ViScriber"
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
