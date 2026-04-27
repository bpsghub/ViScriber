import json
import os
import stat
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


def _config_path() -> Path:
    return Path.home() / ".videoscribe" / "config.json"


@dataclass
class Config:
    default_language: Optional[str] = None
    default_model: str = "small"
    default_device: str = "cpu"
    ai_provider: str = "none"
    api_key: str = ""
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    output_formats: list = field(default_factory=lambda: ["txt"])
    last_output_dir: str = ""
    custom_ai_prompt: str = "Please summarize the following transcript concisely."


def load_config() -> Config:
    path = _config_path()
    if not path.exists():
        return Config()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return Config(**{k: v for k, v in data.items() if k in Config.__dataclass_fields__})
    except Exception:
        return Config()


def save_config(cfg: Config) -> None:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(cfg), f, indent=2)
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
