"""Paths and user configuration.

On Windows everything lives under %APPDATA%\\TinyLearnersMedia (config, tokens,
database) and %LOCALAPPDATA%\\TinyLearnersMedia\\cache (downloaded and
optimized video files). Override the root with the TLM_HOME env var.
"""

from __future__ import annotations

import os
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

APP_NAME = "TinyLearnersMedia"

CONFIG_TEMPLATE = """\
# Tiny Learners Media - configuration
# Fill in the credentials from your own Google Cloud and TikTok developer apps.
# See README.md -> "One-time platform setup".

[google]
# OAuth client of type "Desktop app" (Google Cloud Console -> APIs & Services -> Credentials)
client_id = ""
client_secret = ""

[tiktok]
# TikTok for Developers -> your app -> Credentials (app platform: Desktop)
client_key = ""
client_secret = ""
# Must match a redirect URI registered on the TikTok app exactly.
redirect_uri = "http://localhost:3455/callback/"
# "inbox" = video lands in your TikTok app inbox as a draft, you tap Post (works before audit).
# "direct" = posts straight to your profile (needs the video.publish scope; private-only until audited).
default_mode = "inbox"
# Optional: URL prefixes you verified in the TikTok developer portal. Videos already hosted
# under one of these prefixes are pulled by TikTok's servers instead of uploaded from this PC.
pull_from_url_prefixes = []

[defaults]
youtube_privacy = "private"        # private | unlisted | public
made_for_kids = true               # COPPA: Tiny Learners content is made for kids
contains_synthetic_media = true    # YouTube "altered or synthetic content" disclosure
tiktok_ai_generated = true         # TikTok AI-generated content label
youtube_category_id = "27"         # 27 = Education
"""


def _base_dirs() -> tuple[Path, Path]:
    override = os.environ.get("TLM_HOME")
    if override:
        root = Path(override)
        return root, root / "cache"
    if sys.platform == "win32":
        roaming = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        local = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return roaming / APP_NAME, local / APP_NAME / "cache"
    root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_NAME
    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / APP_NAME
    return root, cache


@dataclass
class Paths:
    home: Path
    cache: Path

    @property
    def config_file(self) -> Path:
        return self.home / "config.toml"

    @property
    def tokens_file(self) -> Path:
        return self.home / "tokens.json"

    @property
    def db_file(self) -> Path:
        return self.home / "posts.db"

    @property
    def log_file(self) -> Path:
        return self.home / "tlm.log"

    @property
    def browser_profile(self) -> Path:
        return self.home / "browser-profile"


def paths() -> Paths:
    home, cache = _base_dirs()
    home.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    return Paths(home, cache)


@dataclass
class Config:
    google: dict = field(default_factory=dict)
    tiktok: dict = field(default_factory=dict)
    defaults: dict = field(default_factory=dict)

    def default(self, key: str, fallback=None):
        return self.defaults.get(key, fallback)


def ensure_config_file() -> Path:
    p = paths().config_file
    if not p.exists():
        p.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    return p


def load_config() -> Config:
    p = ensure_config_file()
    data = tomllib.loads(p.read_text(encoding="utf-8"))
    template = tomllib.loads(CONFIG_TEMPLATE)
    merged = {}
    for section in ("google", "tiktok", "defaults"):
        merged[section] = {**template.get(section, {}), **data.get(section, {})}
    return Config(**merged)
