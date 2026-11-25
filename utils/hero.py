"""
Helpers for the hero picture at the top of the page.
No Streamlit code here, so it is easy to test.
"""
import base64
import io
from pathlib import Path
from typing import Optional

from PIL import Image

import config

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def find_hero_image() -> Optional[Path]:
    """Return the hero picture from assets/, or None if there is no image there."""
    if not config.ASSETS_DIR.exists():
        return None
    images = sorted(
        p for p in config.ASSETS_DIR.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS
    )
    for image in images:                       # a file called "hero.*" wins
        if image.stem.lower() == "hero":
            return image
    return images[0] if images else None


def hero_data_uri(path: Path) -> str:
    """
    Read the picture and return it as a 'data:' text that can be placed inside HTML.
    The picture is only shrunk if it is wider than HERO_MAX_WIDTH_PX, and saved at
    high JPEG quality, so it stays sharp.
    """
    image = Image.open(path).convert("RGB")
    if image.width > config.HERO_MAX_WIDTH_PX:
        new_height = round(image.height * config.HERO_MAX_WIDTH_PX / image.width)
        image = image.resize((config.HERO_MAX_WIDTH_PX, new_height), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=92, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def picture_data_uri(image: Image.Image, max_side: int = 900) -> str:
    """
    Turn any picture (PIL image) into a 'data:' text for CSS/HTML.
    Big photos are shrunk to max_side pixels first, so the page stays fast.
    """
    picture = image.convert("RGB")
    picture.thumbnail((max_side, max_side))
    buffer = io.BytesIO()
    picture.save(buffer, format="JPEG", quality=85)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"
