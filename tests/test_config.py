import json
from pathlib import Path
from src.config import Config, load_config, save_config


def test_load_config_returns_defaults_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr("src.config._config_path", lambda: tmp_path / ".videoscribe" / "config.json")
    cfg = load_config()
    assert cfg.default_language is None
    assert cfg.default_model == "small"
    assert cfg.default_device == "cpu"
    assert cfg.ai_provider == "none"
    assert cfg.output_formats == ["txt"]


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    config_path = tmp_path / ".videoscribe" / "config.json"
    monkeypatch.setattr("src.config._config_path", lambda: config_path)
    cfg = Config(
        default_language="en",
        default_model="medium",
        default_device="cuda",
        ai_provider="claude",
        api_key="sk-test",
        ollama_url="http://localhost:11434",
        output_formats=["txt", "srt"],
        last_output_dir="/some/dir",
        custom_ai_prompt="Summarize this transcript.",
    )
    save_config(cfg)
    assert config_path.exists()
    loaded = load_config()
    assert loaded.default_language == "en"
    assert loaded.default_model == "medium"
    assert loaded.ai_provider == "claude"
    assert loaded.api_key == "sk-test"
    assert loaded.output_formats == ["txt", "srt"]


def test_save_config_creates_parent_dir(tmp_path, monkeypatch):
    config_path = tmp_path / "deep" / "nested" / "config.json"
    monkeypatch.setattr("src.config._config_path", lambda: config_path)
    save_config(Config())
    assert config_path.exists()
