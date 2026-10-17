import shutil
import subprocess

import httpx
import pytest

needs_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")


@pytest.fixture(autouse=True)
def tlm_home(tmp_path, monkeypatch):
    monkeypatch.setenv("TLM_HOME", str(tmp_path / "home"))


@needs_ffmpeg
def test_tiktok_gradient_long_form(tmp_path):
    from tlmedia import media
    v = tmp_path / "main.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    "testsrc2=size=1280x720:rate=24:duration=2", "-f", "lavfi", "-i",
                    "sine=duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-shortest", str(v)], check=True)
    out, info, _ = media.optimize(v, "tiktok", "gradient")
    assert (info["width"], info["height"]) == (1080, 1920)
    assert info["audio_codec"] == "aac" and abs(info["duration_s"] - 2) < 0.3
    # gradient and blur versions are cached separately
    out2, _, _ = media.optimize(v, "tiktok", "vertical")
    assert out2 != out


def test_set_privacy_keeps_kids_flag(monkeypatch):
    from tlmedia import youtube
    monkeypatch.setattr(youtube, "video_status", lambda vid, tok: {"status": {
        "privacyStatus": "private", "selfDeclaredMadeForKids": True, "madeForKids": True,
        "uploadStatus": "processed", "publishAt": "2099-01-01T00:00:00Z"}})
    sent = {}

    def fake_put(url, params, json, headers, timeout):
        sent.update(json)
        return httpx.Response(200, json={"status": {"privacyStatus": json["status"]["privacyStatus"]}},
                              request=httpx.Request("PUT", url))
    monkeypatch.setattr(youtube.httpx, "put", fake_put)
    assert youtube.set_privacy("abc", "public", "tok") == {"video_id": "abc", "privacy": "public"}
    assert sent["status"] == {"privacyStatus": "public", "selfDeclaredMadeForKids": True}


def test_set_privacy_reports_locked_upload(monkeypatch):
    from tlmedia import youtube
    monkeypatch.setattr(youtube, "video_status", lambda vid, tok: {"status": {"privacyStatus": "private"}})
    monkeypatch.setattr(youtube.httpx, "put", lambda url, **k: httpx.Response(
        200, json={"status": {"privacyStatus": "private"}}, request=httpx.Request("PUT", url)))
    with pytest.raises(youtube.YouTubeError, match="Studio"):
        youtube.set_privacy("abc", "public", "tok")


def test_find_playlist_by_title(monkeypatch):
    from tlmedia import youtube
    monkeypatch.setattr(youtube, "list_playlists", lambda tok: [
        {"id": "PL1", "title": "Animal Friends"}, {"id": "PL2", "title": "Space for Little Ones"}])
    assert youtube.find_playlist("space for little ones ", "t") == "PL2"
    assert youtube.find_playlist("Dinosaurs", "t") is None


def test_cli_draft_and_visibility_commands_exist(capsys):
    from tlmedia.cli import main
    for cmd in (["draft", "--help"], ["approve", "--help"], ["wait", "--help"],
                ["visibility", "--help"]):
        with pytest.raises(SystemExit):
            main(cmd)
    assert "private" in capsys.readouterr().out
