from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]


CONFIG_DIR = Path.home() / ".config" / "zibi"
CONFIG_PATH = CONFIG_DIR / "config.toml"


@dataclass(frozen=True)
class Config:
    max_history_entries: int = 500
    auto_save_history: bool = True
    deduplicate_consecutive: bool = True
    share_service: str = "paste.rs"


DEFAULT_CONFIG = Config()


def _coerce_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def _coerce_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def load_config() -> Config:
    # BUG FIX: read the live share_service setting, while accepting the legacy key.
    ensure_config()
    try:
        data = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_CONFIG

    share_service = str(
        data.get("share_service", data.get("default_share_service", DEFAULT_CONFIG.share_service))
    ).strip()
    if share_service not in {"termbin", "paste.rs"}:
        share_service = DEFAULT_CONFIG.share_service

    config = Config(
        max_history_entries=_coerce_int(data.get("max_history_entries"), DEFAULT_CONFIG.max_history_entries),
        auto_save_history=_coerce_bool(data.get("auto_save_history"), DEFAULT_CONFIG.auto_save_history),
        deduplicate_consecutive=_coerce_bool(
            data.get("deduplicate_consecutive"),
            DEFAULT_CONFIG.deduplicate_consecutive,
        ),
        share_service=share_service,
    )
    if "share_service" not in data and "default_share_service" in data:
        save_config(config)
    return config


def save_config(config: Config) -> None:
    # BUG FIX: persist the selected uploader under the documented share_service key.
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        "\n".join(
            [
                f"max_history_entries = {config.max_history_entries}",
                f"auto_save_history = {str(config.auto_save_history).lower()}",
                f"deduplicate_consecutive = {str(config.deduplicate_consecutive).lower()}",
                f'share_service = "{config.share_service}"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def ensure_config() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
