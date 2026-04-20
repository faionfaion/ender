"""Image generation via OpenAI gpt-image-1 — vertical Roblox style."""

from __future__ import annotations

import base64
import logging
import os
from io import BytesIO
from pathlib import Path

from PIL import Image

from pipeline.config import (
    CHARACTER_VISUALS,
    IMAGE_HEIGHT,
    IMAGE_MODEL,
    IMAGE_STYLE,
    IMAGE_WIDTH,
    IMAGES_DIR,
)

logger = logging.getLogger(__name__)


def generate_image(
    prompt: str,
    slug: str,
    character: str = "ender",
    quality: str = "auto",
) -> Path | None:
    """Generate a vertical Roblox-style image and save as PNG.

    Args:
        prompt: Scene description. If starts with the IMAGE_STYLE prefix,
                it's assumed to be a fully-built prompt and is used as-is.
        slug: Article slug for filename.
        character: Character preset ("ender" or "faion-ender").
        quality: gpt-image-1 quality — "auto" (~$0.063), "low" (~$0.016), "high" (~$0.25).
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        logger.warning("No OPENAI_API_KEY, skipping image generation")
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        # If the prompt already starts with the style prefix (pre-built by the
        # prompt editor), use it as-is. Otherwise, wrap it with style + character.
        if prompt.lstrip().startswith(IMAGE_STYLE.split("\n")[0][:40]):
            full_prompt = prompt
        else:
            char_desc = CHARACTER_VISUALS.get(character, CHARACTER_VISUALS["ender"])
            full_prompt = (
                f"{IMAGE_STYLE}\n\n"
                f"Character: {char_desc}\n\n"
                f"Scene: {prompt}\n\n"
                f"Vertical composition (portrait orientation). "
                f"The character should be prominently featured in the scene."
            )

        logger.info("Generating image for %s (character=%s, quality=%s)", slug, character, quality)

        size: str = f"{IMAGE_WIDTH}x{IMAGE_HEIGHT}"
        response = client.images.generate(
            model=IMAGE_MODEL,
            prompt=full_prompt,
            n=1,
            size=size,  # type: ignore[arg-type]
            quality=quality,  # type: ignore[arg-type]
        )

        # Decode image
        if response.data and response.data[0].b64_json:
            img_data = base64.b64decode(response.data[0].b64_json)
        elif response.data and response.data[0].url:
            import httpx
            resp = httpx.get(response.data[0].url, timeout=30)
            img_data = resp.content
        else:
            logger.error("No image data in response")
            return None

        # Process and save
        img = Image.open(BytesIO(img_data))

        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        dest = IMAGES_DIR / f"{slug}.png"
        img.save(str(dest), "PNG", optimize=True)
        logger.info("Image saved: %s (%dx%d)", dest, img.width, img.height)

        return dest

    except Exception as e:
        logger.error("Image generation failed: %s", e)
        return None
