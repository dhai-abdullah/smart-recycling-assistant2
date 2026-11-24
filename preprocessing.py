"""
Custom preprocessing steps (empty for now).

This is the place for the extra image steps chosen after the experiments
(for example noise reduction). Every step is a small function that
receives an image and returns an image.

The image is a NumPy array in RGB order, shape (height, width, 3), dtype uint8.

DO NOT add these here (YOLO already does them automatically):
  - resizing to 640x640
  - dividing the pixel values by 255
Doing them twice makes the predictions worse.

ONLY add a step if the model was trained with it or if tests showed that it
improves the results. A step the model never saw during training can hurt.

How to add a step
-----------------
1. Write the function:

       import cv2

       def gaussian_blur(image):
           return cv2.GaussianBlur(image, (3, 3), 0)

2. Add it to the PIPELINE list below:

       PIPELINE = [gaussian_blur]

   Steps run from first to last. Restart the app after changing this file.
"""
import numpy as np

# Steps applied to every uploaded image, in order. Empty = no extra processing.
PIPELINE = []


def apply_preprocessing(image: np.ndarray) -> np.ndarray:
    """Run every step in PIPELINE. With an empty PIPELINE the image is unchanged."""
    for step in PIPELINE:
        image = step(image)
    return image
