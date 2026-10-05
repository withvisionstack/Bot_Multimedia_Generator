import asyncio
import httpx
from pathlib import Path
from .config import (MAGIC_HOUR_API_KEY, VIDEO_MODEL,
                     VIDEO_RESOLUTION, VIDEO_SECONDS)

_client = None

def _get_client():
    global _client
    if _client is None:
        from magic_hour import Client
        _client = Client(token=MAGIC_HOUR_API_KEY)
    return _client

def _create_sync(image_path: str, prompt: str) -> str:
    c = _get_client()
    file_path = c.v1.files.upload_file(image_path)
    res = c.v1.image_to_video.create(
        style={"prompt": prompt},
        assets={"image_file_path": file_path},
        end_seconds=VIDEO_SECONDS,
        name="telegram-bot",
        model=VIDEO_MODEL,
        resolution=VIDEO_RESOLUTION,
        audio=True,
    )
    return res.id

def _status_sync(job_id: str) -> dict:
    p = _get_client().v1.video_projects.get(id=job_id)
    urls = [d.url for d in (getattr(p, "downloads", None) or [])]
    return {"status": p.status, "urls": urls}

async def create_job(image_path: str, prompt: str) -> str:
    return await asyncio.to_thread(_create_sync, image_path, prompt)

async def get_status(job_id: str) -> dict:
    return await asyncio.to_thread(_status_sync, job_id)

async def download_to_file(url: str, dest: Path) -> Path:
    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as c:
        async with c.stream("GET", url) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                async for chunk in r.aiter_bytes(1024 * 256):
                    f.write(chunk)
    return dest