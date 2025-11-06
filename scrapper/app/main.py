from __future__ import annotations

from typing import List, Dict, Optional

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .model import generate_caption
from .utils import collect_image_urls, download_image


app = FastAPI(title="URL Image Captioner")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    url: Optional[str] = Query(default=None, description="Page URL to scan"),
    limit: int = Query(default=10, ge=1, le=50, description="Max images to caption"),
):
    if not url:
        return templates.TemplateResponse(
            "index.html", {"request": request, "results": None}
        )

    image_urls = collect_image_urls(url, max_images=limit)
    results: List[Dict[str, str]] = []
    for img_url in image_urls:
        img = download_image(img_url)
        if img is None:
            continue
        caption = generate_caption(img)
        results.append({"url": img_url, "caption": caption})

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "results": results, "input_url": url, "limit": limit},
    )


@app.get("/api/caption")
async def api_caption(
    url: str = Query(..., description="Page URL to scan"),
    limit: int = Query(default=10, ge=1, le=50, description="Max images to caption"),
):
    image_urls = collect_image_urls(url, max_images=limit)
    items: List[Dict[str, str]] = []
    for img_url in image_urls:
        img = download_image(img_url)
        if img is None:
            continue
        caption = generate_caption(img)
        items.append({"url": img_url, "caption": caption})
    return {"count": len(items), "items": items}


