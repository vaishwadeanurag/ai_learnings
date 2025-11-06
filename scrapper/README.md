# URL Image Captioner (FastAPI)

A tiny FastAPI app that:
- Accepts a URL
- Scrapes images from the page
- Generates image captions locally using a lightweight model

## Quickstart

1) Activate your environment (you mentioned pyenv local `sandbox-scrapper` already exists):

```bash
pyenv local sandbox-scrapper
```

2) Install dependencies:

```bash
pip install -r requirements.txt
```

3) Run the server:

```bash
uvicorn app.main:app --reload
```

4) Open the app:

- Visit `http://127.0.0.1:8000/`
- Enter a page URL and click Generate

The first run will download the model weights.

## API

- HTML form: `GET /` (query params: `url`, optional `limit`)
- JSON API: `GET /api/caption?url=...&limit=10`

## Model Choices (Local, Lightweight)

Default: `nlpconnect/vit-gpt2-image-captioning` — small and CPU-friendly, good trade-off between size and quality.

Alternatives:
- `Salesforce/blip-image-captioning-base` — higher quality, larger.
- `ydshieh/vit-gpt2-coco-en` — similar family to the default.

Select a model by setting env var before starting the server:

```bash
export CAPTION_MODEL_ID=Salesforce/blip-image-captioning-base
uvicorn app.main:app --reload
```

## Notes
- Runs on CPU by default. On Apple Silicon, it will use Metal (MPS) if available; on NVIDIA it uses CUDA if available.
- The scraper only pulls `<img>` sources and handles `srcset` (largest candidate). Data/blob URLs are skipped.
- Use `limit` to avoid long waits on pages with many images.

## License
MIT


