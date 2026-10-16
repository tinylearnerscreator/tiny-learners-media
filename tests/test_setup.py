import json

import pytest


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("TLM_HOME", str(tmp_path / "home"))
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    (tmp_path / "Downloads").mkdir()
    return tmp_path


def test_set_value_keeps_comments_and_types():
    from tlmedia import setup_wizard as sw
    from tlmedia.config import load_config, paths
    sw.set_value("google", "client_id", 'abc"123')
    sw.set_value("tiktok", "default_mode", "direct")
    sw.set_value("defaults", "made_for_kids", sw._coerce("false"))
    sw.set_value("tiktok", "pull_from_url_prefixes", sw._coerce('["https://v.example.com/"]'))
    cfg = load_config()
    assert cfg.google["client_id"] == 'abc"123'
    assert cfg.tiktok["default_mode"] == "direct"
    assert cfg.defaults["made_for_kids"] is False
    assert cfg.tiktok["pull_from_url_prefixes"] == ["https://v.example.com/"]
    assert "# Tiny Learners Media - configuration" in paths().config_file.read_text()
    assert sw.show_config()["google"]["client_secret"] == ""


def test_import_google_json_from_downloads(home):
    from tlmedia import setup_wizard as sw
    from tlmedia.config import load_config
    (home / "Downloads" / "client_secret_1-abc.apps.googleusercontent.com.json").write_text(
        json.dumps({"installed": {"client_id": "1-abc.apps.googleusercontent.com",
                                  "client_secret": "GOCSPX-secret", "project_id": "tlm"}}))
    out = sw.import_google_json()
    assert out["project_id"] == "tlm"
    assert load_config().google["client_secret"] == "GOCSPX-secret"
    assert sw.show_config()["google"]["client_secret"] == "****cret"


def test_import_google_rejects_web_client(home):
    from tlmedia import setup_wizard as sw
    f = home / "Downloads" / "client_secret_web.json"
    f.write_text(json.dumps({"web": {"client_id": "x", "client_secret": "y"}}))
    with pytest.raises(ValueError, match="Desktop app"):
        sw.import_google_json(f)
