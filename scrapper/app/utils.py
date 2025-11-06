from __future__ import annotations

from io import BytesIO
from typing import List, Optional, Set
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from PIL import Image


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 CaptionBot/1.0"
    )
}


def _is_probable_image_url(url: str) -> bool:
    lower = url.lower()
    return any(
        lower.endswith(ext)
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
    )


def collect_image_urls(page_url: str, max_images: int = 20) -> List[str]:
    resp = requests.get(page_url, headers=DEFAULT_HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results: List[str] = []
    seen: Set[str] = set()

    for img in soup.find_all("img"):
        src = (img.get("src") or "").strip()
        if not src:
            srcset = (img.get("srcset") or "").strip()
            if srcset:
                # pick the last (usually largest) candidate from srcset
                parts = [p.strip().split(" ")[0] for p in srcset.split(",") if p.strip()]
                if parts:
                    src = parts[-1]

        if not src or src.startswith("data:") or src.startswith("blob:"):
            continue

        abs_url = urljoin(page_url, src)
        if abs_url in seen:
            continue
        seen.add(abs_url)
        results.append(abs_url)
        if len(results) >= max_images:
            break

    return results


def download_image(image_url: str, min_bytes: int = 1024) -> Optional[Image.Image]:
    try:
        r = requests.get(image_url, headers=DEFAULT_HEADERS, timeout=20, stream=True)
        r.raise_for_status()
        content_type = (r.headers.get("Content-Type") or "").lower()
        if "image" not in content_type and not _is_probable_image_url(image_url):
            return None
        content = r.content
        if len(content) < min_bytes:
            return None
        return Image.open(BytesIO(content)).convert("RGB")
    except Exception:
        return None


