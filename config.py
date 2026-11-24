"""
Project settings - the one place to change numbers and file names.
No other file needs to be edited for normal tuning.
"""
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ---------------------------------------------------------------- Model files
MODEL_DIR = BASE_DIR / "model"
MODEL_FILENAME = "best.pt"      # put your trained YOLOv8 weights in model/ with this name

# ---------------------------------------------------------------- Detection
IMAGE_SIZE = 640                # same size used during training (imgsz=640)
DETECTION_CONFIDENCE = 0.25     # boxes below this are not shown at all
IOU_THRESHOLD = 0.45            # removes duplicate boxes on the same object

# Below this confidence the app shows the "Low confidence" warning.
LOW_CONFIDENCE_THRESHOLD = 0.50

# ---------------------------------------------------------------- Class names
# The class names are read automatically from the trained model, so the
# order of the classes never has to be typed by hand.
# Only fill this in if the model uses a name the app should show differently:
#   CLASS_NAME_OVERRIDES = {"bio": "Biodegradable", "cardboard_box": "Cardboard"}
CLASS_NAME_OVERRIDES = {}

# ---------------------------------------------------------------- Interface
ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png"]

# ---------------------------------------------------------------- Hero section
# The big picture at the top. Put ANY image (jpg / png / webp) in the assets/
# folder. A file named "hero" (hero.jpg, hero.png ...) is used first; if there
# is none, the first image found in assets/ is used.
ASSETS_DIR = BASE_DIR / "assets"
HERO_MAX_WIDTH_PX = 1600        # bigger pictures are shrunk to this width (keeps the page fast)

HERO_TITLE = "Save The Planet"  # big title, left side
# Short text under the title (what the website does)
HERO_DESCRIPTION = (
    "Not sure how to recycle it? Upload a photo, and our AI will identify "
    "the waste type (biodegradable, cardboard, glass, metal, paper or plastic) "
    "and provide recycling guidance."
)
