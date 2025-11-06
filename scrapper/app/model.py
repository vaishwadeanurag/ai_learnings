import os
from functools import lru_cache
from typing import Tuple

from PIL import Image


def _pipeline_device_arg():
    """
    Select a device argument for transformers.pipeline:
    - -1 for CPU
    - 0 for first CUDA GPU
    - "mps" for Apple Silicon GPU (Metal)
    """
    try:
        import torch  # local import to avoid hard dep at import time
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
        if hasattr(torch, "cuda") and torch.cuda.is_available():
            return 0
    except Exception:
        pass
    return -1


DEFAULT_MODEL_ID = os.getenv(
    "CAPTION_MODEL_ID", "nlpconnect/vit-gpt2-image-captioning"
)


@lru_cache(maxsize=1)
def _get_pipe(model_id: str = DEFAULT_MODEL_ID):
    from transformers import pipeline  # imported lazily to speed cold import

    device = _pipeline_device_arg()
    pipe = pipeline(
        task="image-to-text",
        model=model_id,
        device=device,
    )
    return pipe


def generate_caption(image: Image.Image, max_new_tokens: int = 32) -> str:
    """Generate a caption for a PIL image using the configured pipeline."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    pipe = _get_pipe()
    outputs = pipe(image, max_new_tokens=max_new_tokens)
    text = outputs[0].get("generated_text", "").strip()
    return text


