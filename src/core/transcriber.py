import os
import tempfile
from dataclasses import dataclass, field
from typing import Callable, Optional
from types import SimpleNamespace

from faster_whisper import WhisperModel

from .extractor import extract_audio, split_audio, cleanup_chunks
from .output_writer import write_txt, write_srt


@dataclass
class TranscriptionResult:
    video_path: str
    output_files: list = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None


def _offset_segments(segments, offset_seconds: float):
    return [
        SimpleNamespace(
            start=seg.start + offset_seconds,
            end=seg.end + offset_seconds,
            text=seg.text,
        )
        for seg in segments
    ]


def transcribe_file(
    video_path: str,
    output_dir: str,
    language: Optional[str] = None,
    model_size: str = "small",
    device: str = "cpu",
    chunk_minutes: int = 5,
    formats: Optional[list] = None,
    progress_callback: Optional[Callable] = None,
) -> TranscriptionResult:
    if formats is None:
        formats = ["txt"]

    os.makedirs(output_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(video_path))[0]
    chunk_seconds = chunk_minutes * 60

    def cb(step, pct=0):
        if progress_callback:
            progress_callback(step, pct)

    try:
        with tempfile.TemporaryDirectory() as tmp:
            wav_path = os.path.join(tmp, f"{stem}.wav")
            chunk_dir = os.path.join(tmp, "chunks")

            cb("Extracting audio", 0)
            extract_audio(video_path, wav_path)

            cb("Splitting audio", 10)
            chunks = split_audio(wav_path, chunk_dir, chunk_seconds)

            cb("Loading model", 15)
            device_order = [device]
            if device == "cuda":
                device_order.append("cpu")

            model = None
            for dev in device_order:
                try:
                    model = WhisperModel(model_size, device=dev, compute_type="int8")
                    break
                except Exception:
                    if dev == "cuda":
                        continue
                    raise

            all_segments = []
            for i, chunk in enumerate(chunks):
                pct = 15 + int((i / len(chunks)) * 72)
                cb(f"Transcribing chunk {i + 1}/{len(chunks)}", pct)
                segs, _ = model.transcribe(chunk, language=language, beam_size=5)
                all_segments.extend(_offset_segments(list(segs), i * chunk_seconds))

            cb("Writing output", 90)
            output_files = []
            if "txt" in formats:
                path = os.path.join(output_dir, f"{stem}.txt")
                write_txt(all_segments, path)
                output_files.append(path)
            if "srt" in formats:
                path = os.path.join(output_dir, f"{stem}.srt")
                write_srt(all_segments, path)
                output_files.append(path)

            cleanup_chunks(chunk_dir)
            cb("Done", 100)
            return TranscriptionResult(video_path=video_path, output_files=output_files, success=True)

    except Exception as exc:
        return TranscriptionResult(video_path=video_path, success=False, error=str(exc))
