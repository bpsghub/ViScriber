from types import SimpleNamespace
from src.core.output_writer import write_txt, write_srt, _format_srt_time


def _seg(start, end, text):
    return SimpleNamespace(start=start, end=end, text=text)


def test_format_srt_time_zero():
    assert _format_srt_time(0.0) == "00:00:00,000"


def test_format_srt_time_one_hour():
    assert _format_srt_time(3661.5) == "01:01:01,500"


def test_format_srt_time_milliseconds():
    assert _format_srt_time(2.123) == "00:00:02,123"


def test_format_srt_time_ms_rollover():
    # 2.9999 rounds to 3000 ms total → 00:00:03,000, not 00:00:02,1000
    assert _format_srt_time(2.9999) == "00:00:03,000"


def test_write_txt_creates_file(tmp_path):
    out = tmp_path / "out.txt"
    segs = [_seg(0, 1, "Hello"), _seg(1, 2, " world")]
    write_txt(segs, str(out))
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines == ["Hello", "world"]


def test_write_txt_skips_empty_segments(tmp_path):
    out = tmp_path / "out.txt"
    segs = [_seg(0, 1, "Hello"), _seg(1, 2, "  "), _seg(2, 3, "World")]
    write_txt(segs, str(out))
    lines = out.read_text(encoding="utf-8").splitlines()
    assert "" not in lines
    assert len(lines) == 2


def test_write_srt_creates_valid_srt(tmp_path):
    out = tmp_path / "out.srt"
    segs = [_seg(0.0, 1.5, "First line"), _seg(1.5, 3.0, "Second line")]
    write_srt(segs, str(out))
    content = out.read_text(encoding="utf-8")
    assert "1\n00:00:00,000 --> 00:00:01,500\nFirst line" in content
    assert "2\n00:00:01,500 --> 00:00:03,000\nSecond line" in content


def test_write_srt_skips_empty_segments(tmp_path):
    out = tmp_path / "out.srt"
    segs = [_seg(0, 1, "Hello"), _seg(1, 2, "  ")]
    write_srt(segs, str(out))
    content = out.read_text(encoding="utf-8")
    assert "1\n" in content
    assert "2\n" not in content
