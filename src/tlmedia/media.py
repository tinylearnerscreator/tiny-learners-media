"""ffprobe inspection, per-platform checks, and quality-preserving optimization.

Philosophy: never re-encode unless a platform requires it. When we must, use
high-quality settings (x264 CRF 18, slow preset, AAC 192k, faststart) so the
platform's own transcode starts from a near-lossless master.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

from .config import paths

YOUTUBE_MAX_BYTES = 256 * 1024**3          # 256 GB
TIKTOK_MAX_BYTES = 4 * 1024**3             # 4 GB
TIKTOK_CODECS = {"h264", "hevc", "vp8", "vp9"}
TIKTOK_CONTAINERS = {"mp4", "mov", "webm"}
YOUTUBE_CODECS = {"h264", "hevc", "vp9", "av1", "mpeg4", "prores", "dnxhd", "mpeg2video"}

_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW


def _tool(name: str) -> str:
    # Claude Desktop may start us with a stale PATH; setup records ffmpeg's folder here.
    folder = os.environ.get("TLM_FFMPEG_DIR")
    found = shutil.which(name, path=folder) if folder else None
    found = found or shutil.which(name)
    if not found:
        raise RuntimeError(f"{name} not found on PATH. Install ffmpeg (setup.ps1 does this via winget).")
    return found


def have_ffmpeg() -> bool:
    try:
        return bool(_tool("ffmpeg") and _tool("ffprobe"))
    except RuntimeError:
        return False


def probe(path: Path) -> dict:
    out = subprocess.run(
        [_tool("ffprobe"), "-v", "error", "-print_format", "json", "-show_format", "-show_streams",
         str(path)], capture_output=True, text=True, check=True, creationflags=_NO_WINDOW)
    data = json.loads(out.stdout)
    v = next((s for s in data["streams"] if s.get("codec_type") == "video"), None)
    a = next((s for s in data["streams"] if s.get("codec_type") == "audio"), None)
    if not v:
        raise ValueError(f"No video stream in {path}")
    w, h = int(v["width"]), int(v["height"])
    rot = _rotation(v)
    if rot in (90, 270):
        w, h = h, w
    fps = _fps(v.get("avg_frame_rate") or v.get("r_frame_rate") or "0/1")
    fmt = data["format"]
    return {
        "path": str(path),
        "size_bytes": int(fmt.get("size") or path.stat().st_size),
        "size_mb": round(int(fmt.get("size") or path.stat().st_size) / 1e6, 1),
        "duration_s": round(float(fmt.get("duration") or v.get("duration") or 0), 2),
        "container": fmt.get("format_name", ""),
        "video_codec": v.get("codec_name"),
        "width": w, "height": h, "fps": round(fps, 3),
        "pix_fmt": v.get("pix_fmt"),
        "video_bitrate_kbps": round(int(v.get("bit_rate") or fmt.get("bit_rate") or 0) / 1000),
        "audio_codec": a.get("codec_name") if a else None,
        "audio_sample_rate": int(a["sample_rate"]) if a and a.get("sample_rate") else None,
        "orientation": "vertical" if h > w else "horizontal" if w > h else "square",
    }


def _rotation(stream: dict) -> int:
    rot = stream.get("tags", {}).get("rotate")
    for sd in stream.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = sd["rotation"]
    try:
        return abs(int(float(rot or 0))) % 360
    except ValueError:
        return 0


def _fps(rate: str) -> float:
    num, _, den = rate.partition("/")
    try:
        return float(num) / float(den or 1)
    except (ValueError, ZeroDivisionError):
        return 0.0


def _containers(info: dict) -> set[str]:
    return set(info["container"].split(","))


def check(info: dict, platform: str, max_duration_s: int | None = None) -> dict:
    """Return {'ok': bool, 'must_fix': [...], 'warnings': [...]} for a platform."""
    must, warn = [], []
    long_side = max(info["width"], info["height"])
    short_side = min(info["width"], info["height"])
    if platform == "youtube":
        if info["size_bytes"] > YOUTUBE_MAX_BYTES:
            must.append("larger than YouTube's 256 GB limit")
        if info["video_codec"] not in YOUTUBE_CODECS:
            must.append(f"video codec {info['video_codec']} is not a YouTube-friendly codec")
        if short_side < 720:
            warn.append(f"{info['width']}x{info['height']} is below HD; YouTube will show it as SD")
        if info["duration_s"] > 15 * 60:
            warn.append("over 15 minutes: the channel must be phone-verified")
        if info["orientation"] == "vertical" and info["duration_s"] <= 180:
            warn.append("vertical and <= 3 min: YouTube will classify it as a Short")
        if not info["audio_codec"]:
            warn.append("no audio track")
    elif platform == "tiktok":
        if info["size_bytes"] > TIKTOK_MAX_BYTES:
            must.append("larger than TikTok's 4 GB limit")
        if info["video_codec"] not in TIKTOK_CODECS:
            must.append(f"video codec {info['video_codec']} not accepted by TikTok")
        if not (_containers(info) & TIKTOK_CONTAINERS):
            must.append(f"container {info['container']} not accepted (mp4/mov/webm)")
        if info["fps"] > 60:
            must.append(f"{info['fps']} fps is above TikTok's 60 fps limit")
        if info["fps"] and info["fps"] < 23:
            warn.append(f"{info['fps']} fps is below TikTok's 23 fps minimum")
        if short_side < 360 or long_side > 4096:
            must.append(f"{info['width']}x{info['height']} outside TikTok's 360-4096 px range")
        if info["pix_fmt"] not in ("yuv420p", "yuvj420p", None):
            must.append(f"pixel format {info['pix_fmt']} may fail on phones; needs yuv420p")
        if max_duration_s and info["duration_s"] > max_duration_s:
            must.append(f"{info['duration_s']:.0f}s is longer than this account's "
                        f"{max_duration_s}s TikTok limit")
        if info["orientation"] != "vertical":
            warn.append("not vertical: TikTok will letterbox it. Use tiktok_format='vertical' "
                        "for a full-screen 9:16 version with a blurred background")
        if not info["audio_codec"]:
            warn.append("no audio track")
    return {"ok": not must, "must_fix": must, "warnings": warn}


def optimize(src: Path, platform: str, tiktok_format: str = "auto",
             max_duration_s: int | None = None,
             progress: Callable[[float, str], None] | None = None) -> tuple[Path, dict, list[str]]:
    """Return (file_to_upload, its_probe, notes). Re-encodes only if needed."""
    info = probe(src)
    result = check(info, platform, max_duration_s)
    vertical = platform == "tiktok" and tiktok_format == "vertical" and info["orientation"] != "vertical"
    if result["ok"] and not vertical:
        return src, info, ["original file uploaded untouched"]

    if max_duration_s and info["duration_s"] > max_duration_s:
        raise ValueError(result["must_fix"][-1] + ". Trim the video or post it to YouTube only.")

    key = hashlib.sha1(f"{src.resolve()}|{src.stat().st_size}|{src.stat().st_mtime}|"
                       f"{platform}|{vertical}".encode()).hexdigest()[:12]
    dest = paths().cache / "optimized" / f"{src.stem}.{platform}.{key}.mp4"
    dest.parent.mkdir(parents=True, exist_ok=True)
    notes = [f"re-encoded for {platform}: " + ("; ".join(result["must_fix"]) or "made 9:16 vertical")]
    if dest.exists():
        return dest, probe(dest), notes + ["(reused cached optimized copy)"]

    vf = []
    fc = None
    if vertical:
        fc = ("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
              "gblur=sigma=30,eq=brightness=-0.08[bg];"
              "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
              "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]")
    else:
        if max(info["width"], info["height"]) > 4096:  # downscale long side to 4K
            vf.append("scale='if(gt(iw,ih),3840,-2)':'if(gt(iw,ih),-2,3840)'")
        elif min(info["width"], info["height"]) < 360:  # upscale short side to 720
            vf.append("scale='if(gt(iw,ih),-2,720)':'if(gt(iw,ih),720,-2)'")
        if info["fps"] > 60:
            vf.append("fps=60")
        vf.append("format=yuv420p")

    cmd = [_tool("ffmpeg"), "-y", "-hide_banner", "-loglevel", "error", "-progress", "pipe:1",
           "-i", str(src)]
    if fc:
        cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "0:a?"]
    else:
        cmd += ["-map", "0:v:0", "-map", "0:a?", "-vf", ",".join(vf)]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart"]
    tmp = dest.with_suffix(".part.mp4")
    cmd.append(str(tmp))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            creationflags=_NO_WINDOW)
    total_us = max(info["duration_s"], 0.01) * 1_000_000
    for line in proc.stdout:
        if line.startswith("out_time_us=") and progress:
            try:
                progress(min(int(line.split("=")[1]) / total_us, 1.0), "optimizing video")
            except ValueError:
                pass
    err = proc.stderr.read()
    if proc.wait() != 0:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg failed: {err.strip()[-800:]}")
    tmp.replace(dest)
    return dest, probe(dest), notes
