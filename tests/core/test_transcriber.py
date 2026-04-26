import os
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
import pytest
from src.core.transcriber import transcribe_file, TranscriptionResult


def _make_seg(start, end, text):
    return SimpleNamespace(start=start, end=end, text=text)


@patch("src.core.transcriber.cleanup_chunks")
@patch("src.core.transcriber.split_audio", return_value=["/tmp/chunk_000.wav"])
@patch("src.core.transcriber.extract_audio")
@patch("src.core.transcriber.WhisperModel")
def test_transcribe_file_returns_result(mock_model_cls, mock_extract, mock_split, mock_cleanup, tmp_path):
    segs = [_make_seg(0.0, 1.0, "Hello world")]
    mock_info = SimpleNamespace(language="en", language_probability=0.99)
    mock_model = MagicMock()
    mock_model.transcribe.return_value = (iter(segs), mock_info)
    mock_model_cls.return_value = mock_model

    video = tmp_path / "test.mp4"
    video.write_text("fake")
    result = transcribe_file(
        video_path=str(video),
        output_dir=str(tmp_path),
        language=None,
        model_size="small",
        device="cpu",
        chunk_minutes=5,
        formats=["txt"],
    )
    assert isinstance(result, TranscriptionResult)
    assert result.success is True
    assert any(f.endswith(".txt") for f in result.output_files)


@patch("src.core.transcriber.cleanup_chunks")
@patch("src.core.transcriber.split_audio", return_value=["/tmp/c0.wav", "/tmp/c1.wav"])
@patch("src.core.transcriber.extract_audio")
@patch("src.core.transcriber.WhisperModel")
def test_srt_timestamps_offset_by_chunk(mock_model_cls, mock_extract, mock_split, mock_cleanup, tmp_path):
    chunk0_segs = [_make_seg(0.0, 2.0, "First")]
    chunk1_segs = [_make_seg(0.0, 2.0, "Second")]
    mock_info = SimpleNamespace(language="en", language_probability=0.99)
    mock_model = MagicMock()
    mock_model.transcribe.side_effect = [
        (iter(chunk0_segs), mock_info),
        (iter(chunk1_segs), mock_info),
    ]
    mock_model_cls.return_value = mock_model

    video = tmp_path / "test.mp4"
    video.write_text("fake")
    result = transcribe_file(
        video_path=str(video),
        output_dir=str(tmp_path),
        language=None,
        model_size="small",
        device="cpu",
        chunk_minutes=5,
        formats=["srt"],
    )
    srt_path = [f for f in result.output_files if f.endswith(".srt")][0]
    content = open(srt_path, encoding="utf-8").read()
    # Second segment should be offset by 5 minutes (300 seconds)
    assert "00:05:00,000 --> 00:05:02,000" in content


@patch("src.core.transcriber.cleanup_chunks")
@patch("src.core.transcriber.split_audio", return_value=["/tmp/chunk_000.wav"])
@patch("src.core.transcriber.extract_audio", side_effect=RuntimeError("ffmpeg not found"))
@patch("src.core.transcriber.WhisperModel")
def test_transcribe_file_returns_failure_on_extract_error(mock_model_cls, mock_extract, mock_split, mock_cleanup, tmp_path):
    video = tmp_path / "test.mp4"
    video.write_text("fake")
    result = transcribe_file(
        video_path=str(video),
        output_dir=str(tmp_path),
        formats=["txt"],
    )
    assert result.success is False
    assert "ffmpeg not found" in result.error


def test_progress_callback_called(tmp_path):
    with (patch("src.core.transcriber.extract_audio"),
          patch("src.core.transcriber.split_audio", return_value=["/tmp/chunk_000.wav"]),
          patch("src.core.transcriber.cleanup_chunks"),
          patch("src.core.transcriber.WhisperModel") as mock_model_cls):
        mock_model = MagicMock()
        mock_info = SimpleNamespace(language="en", language_probability=0.99)
        mock_model.transcribe.return_value = (iter([]), mock_info)
        mock_model_cls.return_value = mock_model

        steps = []
        video = tmp_path / "test.mp4"
        video.write_text("fake")
        transcribe_file(
            video_path=str(video),
            output_dir=str(tmp_path),
            formats=["txt"],
            progress_callback=lambda step, pct: steps.append(step),
        )
        assert len(steps) >= 3
        assert steps[0] == "Extracting audio"
        assert steps[-1] == "Done"
