"""
Model loading, image preparation and prediction.

This file contains NO Streamlit code, so it can be tested on its own.
The app (app.py) only calls load_image() and predict().
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import numpy as np
from PIL import Image, ImageOps

import config
from utils.preprocessing import apply_preprocessing
from utils.recycling_guidelines import normalize_label


class ModelNotConnectedError(Exception):
    """Raised when the trained model file is missing or empty."""


class ModelLoadError(Exception):
    """Raised when the model file exists but cannot be loaded by Ultralytics."""


@dataclass
class Detection:
    category: str       # e.g. "Plastic"
    confidence: float   # between 0 and 1


@dataclass
class PredictionResult:
    detections: List[Detection]       # sorted from most to least confident
    annotated_image: np.ndarray       # RGB image with the boxes drawn on it

    @property
    def main(self) -> Optional[Detection]:
        """The most confident detection (None if nothing was found)."""
        return self.detections[0] if self.detections else None


# ------------------------------------------------------------------ Model
def find_model_file() -> Optional[Path]:
    """Return the path of the model file, or None if it is not there yet."""
    path = config.MODEL_DIR / config.MODEL_FILENAME
    # A zero-byte/placeholder file is not a trained model.
    return path if path.is_file() and path.stat().st_size > 0 else None


def model_is_available() -> bool:
    return find_model_file() is not None


@lru_cache(maxsize=1)
def load_model(model_path: str):
    """Load the YOLO model once and reuse it (loading is slow)."""
    try:
        from ultralytics import YOLO   # imported here so the app can start without it
    except ImportError as error:
        raise ModelNotConnectedError(
            "The 'ultralytics' library is not installed. "
            "Run: pip install -r requirements.txt"
        ) from error
    try:
        return YOLO(model_path)
    except Exception as error:
        raise ModelLoadError(
            f"Could not load '{Path(model_path).name}'. "
            "Make sure this is the original trained YOLO .pt weights file "
            "and that the installed PyTorch/Ultralytics versions support it. "
            f"Details: {type(error).__name__}: {error}"
        ) from error


# ------------------------------------------------------------------ Image
def load_image(uploaded_file) -> Image.Image:
    """Open an uploaded file as an RGB image, fixing phone-camera rotation."""
    image = Image.open(uploaded_file)
    image = ImageOps.exif_transpose(image)
    return image.convert("RGB")


def prepare_image(image: Image.Image) -> np.ndarray:
    """
    Convert to a NumPy array and apply the custom steps from utils/preprocessing.py.
    Resizing and 0-1 scaling are done by YOLO itself, so they are NOT done here.
    """
    array = np.array(image.convert("RGB"))
    return apply_preprocessing(array)


# ------------------------------------------------------------------ Prediction
def predict(image: Image.Image) -> PredictionResult:
    """Detect the waste items in an image."""
    model_path = find_model_file()
    if model_path is None:
        raise ModelNotConnectedError(
            "The classification model has not been connected yet."
        )
    model = load_model(str(model_path))

    rgb = prepare_image(image)
    # Ultralytics expects NumPy images in BGR order (OpenCV style), so flip RGB -> BGR.
    bgr = rgb[:, :, ::-1]
    result = model.predict(
        bgr,
        conf=config.DETECTION_CONFIDENCE,
        iou=config.IOU_THRESHOLD,
        imgsz=config.IMAGE_SIZE,
        verbose=False,
    )[0]

    detections = []
    for box in result.boxes:
        raw_name = model.names[int(box.cls)]   # class name stored inside the model
        category = config.CLASS_NAME_OVERRIDES.get(raw_name, normalize_label(raw_name))
        detections.append(Detection(category, float(box.conf)))
    detections.sort(key=lambda d: d.confidence, reverse=True)

    annotated_rgb = result.plot()[:, :, ::-1]   # plot() returns BGR, flip back to RGB
    return PredictionResult(detections, np.ascontiguousarray(annotated_rgb))
