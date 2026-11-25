# Smart Recycling Assistant

A Streamlit application that uses a trained Ultralytics YOLO model to detect waste items and display recycling guidance.

## Project structure

```text
smart-recycling-assistant/
├── app.py
├── config.py
├── requirements.txt
├── packages.txt
├── runtime.txt
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── style.css
│   └── hero.jpg
├── model/
│   └── best (3).pt
└── utils/
    ├── __init__.py
    ├── hero.py
    ├── prediction.py
    ├── preprocessing.py
    └── recycling_guidelines.py
```

## Required model file

The application expects the **original trained YOLO weights** at:

```text
model/best (3).pt
```

The file must contain the actual trained weights. An empty file or a Git LFS pointer is not a usable model. The current repository copy was found to be an empty placeholder, so detection will not work until the original `.pt` file is uploaded to this exact path.

If the original model has a different filename, either rename it to `best (3).pt` or update `MODEL_FILENAME` in `config.py` to match it exactly.

## Run locally

Use Python 3.11, then run:

```bash
python -m venv .venv
```

Activate the environment and install dependencies:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Select this repository and the `main` branch (or the branch you want to deploy).
2. Set the main file path to `app.py`.
3. Ensure the original model weights are committed at `model/best (3).pt`.
4. Deploy.

The app reports a clear error if the model file is missing, empty, or cannot be loaded.
