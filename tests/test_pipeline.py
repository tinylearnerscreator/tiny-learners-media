import asyncio
import shutil
import subprocess
from datetime import timedelta

import pytest

needs_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")


@pytest.fixture(autouse=True)
def tlm_home(tmp_path, monkeypatch):
    monkeypatch.setenv("TLM_HOME", str(tmp_path / "home"))
    return tmp_path


def make_video(path, w=640, h=360, fps=30, seconds=2):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-f", "lavfi", "-i", f"testsrc2=size={w}x{h}:rate={fps}:duration={seconds}",
                    "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                    str(path)], check=True)
    return path


@needs_ffmpeg
def test_probe_and_untouched_when_valid(tmp_path):
    from tlmedia import media
    v = make_video(tmp_path / "ok.mp4")
    out, info, notes = media.optimize(v, "youtube")
    assert out == v and "untouched" in notes[0]
    assert info["orientation"] == "horizontal" and info["audio_codec"] == "aac"


@needs_ffmpeg
def test_tiktok_vertical_and_fps_fix(tmp_path):
    from tlmedia import media
    v = make_video(tmp_path / "wide.mp4")
    out, info, _ = media.optimize(v, "tiktok", "vertical")
    assert (info["width"], info["height"]) == (1080, 1920)
    assert info["video_codec"] == "h264" and info["pix_fmt"] == "yuv420p"

    fast = make_video(tmp_path / "fast.mp4", w=1080, h=1920, fps=120, seconds=1)
    assert not media.check(media.probe(fast), "tiktok")["ok"]
    out, info, notes = media.optimize(fast, "tiktok")
    assert info["fps"] == 60 and "re-encoded" in notes[0]


@needs_ffmpeg
def test_draft_approve_upload_flow(tmp_path, monkeypatch):
    from tlmedia import jobs, youtube
    v = make_video(tmp_path / "ep.mp4")
    monkeypatch.setattr(jobs, "google_token", lambda cfg: "tok")
    calls = []

    def fake_upload(path, opts, token, resume, save, progress):
        calls.append((path, opts))
        progress(1.0, "done")
        return {"id": "abc", "status": {"privacyStatus": "private"}}
    monkeypatch.setattr(youtube, "upload", fake_upload)

    d = jobs.create_draft(str(v), ["youtube", "tiktok"], {"title": "Counting to 10"},
                          "2099-01-01T09:00:00Z")
    assert "nothing has been uploaded" in d["preview"]
    assert "YouTube-native schedule" in d["preview"]
    s = jobs.store()
    assert jobs.run_due() == 0  # drafts are never picked up before approval
    assert not calls

    jobs.approve(d["group_id"])
    jobs.run_due()
    rows = {r["platform"]: r for r in s.group(d["group_id"])}
    assert rows["youtube"]["status"] == "done"
    assert rows["youtube"]["result"]["url"] == "https://youtu.be/abc"
    assert calls[0][1]["publish_at"] == "2099-01-01T09:00:00Z"
    # TikTok waits for its scheduled time
    assert rows["tiktok"]["status"] == "queued" and rows["tiktok"]["run_after"].startswith("2099")


def test_lease_prevents_double_claim():
    from tlmedia import jobs
    from tlmedia.store import iso, now
    s = jobs.store()
    pid = s.create("g1", "youtube", "x.mp4", {}, None)
    s.approve_group("g1")
    assert s.claim("worker-a")["id"] == pid
    assert s.claim("worker-b") is None
    s.update(pid, lease_until=iso(now() - timedelta(minutes=1)))  # worker-a died
    assert s.claim("worker-b")["id"] == pid


def test_past_schedule_rejected():
    from tlmedia import jobs
    with pytest.raises(ValueError):
        jobs.parse_when("2001-01-01T00:00:00Z")


def test_mcp_tools_registered():
    from tlmedia.server import mcp
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert {"draft_post", "approve_post", "post_status", "inspect_video",
            "open_in_tiktok_studio", "list_drive_videos"} <= names
