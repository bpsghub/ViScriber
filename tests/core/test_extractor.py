import os
import sys
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from src.core.extractor import (
    _ffmpeg_binary,
    extract_audio,
    split_audio,
    cleanup_chunks,
    is_ffmpeg_available,
)


def test_ffmpeg_binary_returns_path():
    path = _ffmpeg_binary()
    assert isinstance(path, str)
    assert len(path) > 0


@patch("src.core.extractor.subprocess.run")
@patch("src.core.extractor._ffmpeg_binary", return_value="ffmpeg")
def test_is_ffmpeg_available_true(mock_bin, mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    assert is_ffmpeg_available() is True


@patch("src.core.extractor.subprocess.run", side_effect=FileNotFoundError())
@patch("src.core.extractor._ffmpeg_binary", return_value="ffmpeg")
def test_is_ffmpeg_available_false_when_missing(mock_bin, mock_run):
    assert is_ffmpeg_available() is False


@patch("src.core.extractor.Path.exists", return_value=False)
def test_ffmpeg_binary_platform_win(mock_exists, monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    path = _ffmpeg_binary()
    assert path == "ffmpeg"  # falls back to system PATH when bundled doesn't exist


@patch("src.core.extractor.Path.exists", return_value=False)
def test_ffmpeg_binary_platform_mac(mock_exists, monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    path = _ffmpeg_binary()
    assert path == "ffmpeg"  # falls back to system PATH when bundled doesn't exist


@patch("src.core.extractor.Path.exists", return_value=False)
def test_ffmpeg_binary_platform_linux(mock_exists, monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    path = _ffmpeg_binary()
    assert path == "ffmpeg"  # falls back to system PATH when bundled doesn't exist


@patch("src.core.extractor.subprocess.run")
@patch("src.core.extractor._ffmpeg_binary", return_value="ffmpeg")
def test_extract_audio_calls_ffmpeg(mock_bin, mock_run):
    mock_run.side_effect = [MagicMock(returncode=0), MagicMock(returncode=0)]
    extract_audio("/input/video.mp4", "/output/audio.wav")
    called_args = mock_run.call_args[0][0]
    assert "ffmpeg" in called_args[0]
    assert "/input/video.mp4" in called_args
    assert "/output/audio.wav" in called_args
    assert "-ar" in called_args
    assert "16000" in called_args


@patch("src.core.extractor.subprocess.run")
@patch("src.core.extractor._ffmpeg_binary", return_value="ffmpeg")
@patch("src.core.extractor.os.listdir", return_value=["chunk_000.wav", "chunk_001.wav"])
def test_split_audio_returns_sorted_chunks(mock_listdir, mock_bin, mock_run, tmp_path):
    mock_run.side_effect = [MagicMock(returncode=0), MagicMock(returncode=0)]
    chunks = split_audio("/audio/file.wav", str(tmp_path / "chunks"), 300)
    assert len(chunks) == 2
    assert chunks[0].endswith("chunk_000.wav")
    assert chunks[1].endswith("chunk_001.wav")


@patch("src.core.extractor.subprocess.run")
@patch("src.core.extractor._ffmpeg_binary", return_value="ffmpeg")
@patch("src.core.extractor.os.listdir", return_value=[])
def test_split_audio_raises_when_no_chunks(mock_listdir, mock_bin, mock_run, tmp_path):
    mock_run.side_effect = [MagicMock(returncode=0), MagicMock(returncode=0)]
    with pytest.raises(RuntimeError, match="no chunks"):
        split_audio("/audio/file.wav", str(tmp_path / "chunks"), 300)


def test_cleanup_chunks_removes_dir(tmp_path):
    chunk_dir = tmp_path / "chunks"
    chunk_dir.mkdir()
    (chunk_dir / "chunk_000.wav").write_text("data")
    cleanup_chunks(str(chunk_dir))
    assert not chunk_dir.exists()


def test_cleanup_chunks_noop_if_missing(tmp_path):
    cleanup_chunks(str(tmp_path / "nonexistent"))  # should not raise


@patch("src.core.extractor.subprocess.run")
@patch("src.core.extractor._ffmpeg_binary", return_value="ffmpeg")
def test_extract_audio_raises_runtime_error_on_failure(mock_bin, mock_run):
    error = subprocess.CalledProcessError(1, "ffmpeg")
    error.stderr = b"no such file or directory"
    mock_run.side_effect = [MagicMock(returncode=0), error]
    with pytest.raises(RuntimeError, match="no such file or directory"):
        extract_audio("/input/video.mp4", "/output/audio.wav")


@patch("src.core.extractor.subprocess.run")
@patch("src.core.extractor._ffmpeg_binary", return_value="ffmpeg")
def test_split_audio_raises_runtime_error_with_stderr(mock_bin, mock_run):
    error = subprocess.CalledProcessError(1, "ffmpeg")
    error.stderr = b"Invalid data found when processing input\nsome other line\nchunking error msg"
    mock_run.side_effect = [MagicMock(returncode=0), error]
    with pytest.raises(RuntimeError, match="chunking error msg"):
        split_audio("/audio/file.wav", "/tmp/chunks", 300)


@patch("src.core.extractor.subprocess.run", side_effect=FileNotFoundError())
def test_extract_audio_raises_runtime_error_when_ffmpeg_missing(mock_run):
    with pytest.raises(RuntimeError, match="FFmpeg is required"):
        extract_audio("/input/video.mp4", "/output/audio.wav")
