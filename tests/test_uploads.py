import hashlib
import os

import httpx
import pytest

from tlmedia import tiktok, youtube
from tlmedia.auth import pkce_pair
from tlmedia.sources import classify, drive_file_id

MB = 1_000_000


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)


# -- TikTok chunk planning ------------------------------------------------------------
@pytest.mark.parametrize("size", [4 * MB, 50 * MB, 64 * MB, 64 * MB + 1, 100 * MB + 123,
                                  999 * MB, 4 * 1024**3])
def test_tiktok_chunk_plan_follows_rules(size):
    chunk, count = tiktok.plan_chunks(size)
    ranges = tiktok.chunk_ranges(size, chunk, count)
    assert 1 <= count <= 1000
    assert ranges[0][0] == 0 and ranges[-1][1] == size - 1
    for (_, e1), (s2, _) in zip(ranges, ranges[1:]):
        assert s2 == e1 + 1  # contiguous, sequential
    if count > 1:
        assert 5 * 1024 * 1024 <= chunk <= 64 * MB
        for s, e in ranges[:-1]:
            assert e - s + 1 == chunk
        assert ranges[-1][1] - ranges[-1][0] + 1 <= 128 * MB
    assert count == size // chunk


def test_tiktok_upload_retries_and_sends_ranges(tmp_path):
    f = tmp_path / "v.mp4"
    f.write_bytes(os.urandom(70 * MB // 10))  # 7 MB, uploaded as 1 chunk
    seen, fail_once = [], {"n": 1}

    def handler(req: httpx.Request):
        if fail_once["n"]:
            fail_once["n"] -= 1
            return httpx.Response(503)
        seen.append((req.headers["content-range"], len(req.content), req.headers["content-type"]))
        return httpx.Response(201)

    size = f.stat().st_size
    chunk, count = tiktok.plan_chunks(size)
    with httpx.Client(transport=httpx.MockTransport(handler)) as c:
        tiktok.upload_file("https://upload.example/x", f, chunk, count, client=c)
    assert seen == [(f"bytes 0-{size - 1}/{size}", size, "video/mp4")]


def test_tiktok_post_info_forces_allowed_privacy():
    info = tiktok.build_post_info({"tiktok_privacy": "PUBLIC_TO_EVERYONE", "title": "Hi"},
                                  {"privacy_level_options": ["SELF_ONLY"]})
    assert info["privacy_level"] == "SELF_ONLY" and info["is_aigc"] is True


# -- YouTube resumable upload --------------------------------------------------------
class FakeYouTube:
    """Minimal resumable-upload server. Can drop the connection after N chunks."""

    def __init__(self, drop_after=None):
        self.data = bytearray()
        self.size = None
        self.drop_after = drop_after
        self.puts = 0
        self.init_body = None

    def __call__(self, req: httpx.Request):
        if req.method == "POST":
            self.size = int(req.headers["x-upload-content-length"])
            self.init_body = req.content
            return httpx.Response(200, headers={"location": "https://upload.example/session/1"})
        cr = req.headers["content-range"]
        if cr.startswith("bytes */"):
            return self._state()
        self.puts += 1
        if self.drop_after is not None and self.puts > self.drop_after:
            self.drop_after = None
            raise httpx.ConnectError("wifi dropped")
        start = int(cr.split()[1].split("-")[0])
        assert start == len(self.data), "client must resume at the server's offset"
        self.data += req.content
        return self._state()

    def _state(self):
        if self.size is not None and len(self.data) == self.size:
            return httpx.Response(200, json={"id": "vid123", "status": {"privacyStatus": "private"}})
        headers = {"range": f"bytes=0-{len(self.data) - 1}"} if self.data else {}
        return httpx.Response(308, headers=headers)


def test_youtube_upload_survives_connection_drop(tmp_path):
    f = tmp_path / "ep.mp4"
    payload = os.urandom(1_300_000)
    f.write_bytes(payload)
    server = FakeYouTube(drop_after=2)
    saved = {}
    with httpx.Client(transport=httpx.MockTransport(server)) as c:
        video = youtube.upload(f, {"title": "Ep <1>", "tags": ["abc", "kids songs"]}, lambda: "tok",
                               None, saved.update, chunk_size=256 * 1024, client=c)
    assert video["id"] == "vid123"
    assert hashlib.sha256(server.data).digest() == hashlib.sha256(payload).digest()
    assert b"Ep \xe2\x80\xb91\xe2\x80\xba" in server.init_body  # angle brackets replaced


def test_youtube_upload_resumes_from_saved_session(tmp_path):
    f = tmp_path / "ep.mp4"
    payload = os.urandom(900_000)
    f.write_bytes(payload)
    server = FakeYouTube()
    server.size = len(payload)
    server.data += payload[:512 * 1024]  # pretend a previous run sent 2 chunks
    with httpx.Client(transport=httpx.MockTransport(server)) as c:
        video = youtube.upload(f, {"title": "x"}, lambda: "tok",
                               {"session": "https://upload.example/session/1", "size": len(payload)},
                               lambda s: None, chunk_size=256 * 1024, client=c)
    assert video["id"] == "vid123"
    assert server.init_body is None  # no new session was started
    assert bytes(server.data) == payload


def test_youtube_body_scheduling_and_disclosures():
    body = youtube.build_body({"title": "t", "youtube_privacy": "public",
                               "publish_at": "2026-10-18T13:00:00Z"})
    assert body["status"]["privacyStatus"] == "private"
    assert body["status"]["publishAt"] == "2026-10-18T13:00:00Z"
    assert body["status"]["selfDeclaredMadeForKids"] is True
    assert body["status"]["containsSyntheticMedia"] is True


# -- misc ---------------------------------------------------------------------------
def test_drive_links():
    fid = "1AbCdEfGhIjKlMnOpQrStUvWxYz"
    for link in (f"https://drive.google.com/file/d/{fid}/view?usp=sharing",
                 f"https://drive.google.com/open?id={fid}",
                 f"https://drive.google.com/uc?export=download&id={fid}",
                 f"drive:{fid}"):
        assert drive_file_id(link) == fid
        assert classify(link) == "drive"
    assert classify(r"G:\My Drive\Tiny Learners\ep12.mp4") == "local"
    assert classify("https://cdn.example.com/v.mp4") == "url"


def test_tiktok_pkce_is_hex():
    verifier, challenge = pkce_pair(hex_challenge=True)
    assert 43 <= len(verifier) <= 128
    assert challenge == hashlib.sha256(verifier.encode()).hexdigest()
