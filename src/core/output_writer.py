def _format_srt_time(seconds: float) -> str:
    total_ms = round(seconds * 1000)
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_txt(segments, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        for seg in segments:
            text = seg.text.strip()
            if text:
                f.write(text + "\n")


def write_srt(segments, output_path: str) -> None:
    counter = 1
    with open(output_path, "w", encoding="utf-8") as f:
        for seg in segments:
            text = seg.text.strip()
            if not text:
                continue
            f.write(f"{counter}\n")
            f.write(f"{_format_srt_time(seg.start)} --> {_format_srt_time(seg.end)}\n")
            f.write(text + "\n\n")
            counter += 1
