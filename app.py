"""
Smart Recycling Assistant - Streamlit interface.

Everything the user does happens in ONE column, all boxes have the same width:
    title + description
    upload box        <- the picture stays INSIDE this box (before and after detection)
    [Detect Waste]
    result box        <- detected category + confidence
    "What to do" box  <- recycling guidelines

Model work is in utils/prediction.py, the picture helpers in utils/hero.py,
custom preprocessing steps in utils/preprocessing.py, recycling text in
utils/recycling_guidelines.py.  Run with:  streamlit run app.py
"""
import html
from collections import Counter
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

import config
from utils.hero import find_hero_image, hero_data_uri, picture_data_uri
from utils.prediction import ModelNotConnectedError, load_image, predict
from utils.recycling_guidelines import get_guidelines

st.set_page_config(page_title="Smart Recycling Assistant", page_icon="♻️", layout="wide")


# ------------------------------------------------------------------ Helpers
def load_css() -> None:
    """Apply the stylesheet from assets/style.css."""
    css = (config.BASE_DIR / "assets" / "style.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def cached_hero_uri(path: str, modified_time: float) -> str:
    """Prepare the hero picture once (not on every click). A new file means a new cache entry."""
    return hero_data_uri(Path(path))


def inject_hero_image() -> None:
    """
    Make the hero picture available to the CSS as the variable --hero-url.
    The CSS paints it behind the top section (see assets/style.css).
    With no image in assets/, nothing is painted.
    """
    image_path = find_hero_image()
    if image_path is None:
        return
    image_uri = cached_hero_uri(str(image_path), image_path.stat().st_mtime)
    st.markdown(f'<style>:root {{ --hero-url: url("{image_uri}"); }}</style>', unsafe_allow_html=True)


# ------------------------------------------------------------------ Page parts
def render_header() -> None:
    """Slim bar at the top of the page with the brand name."""
    st.markdown(
        '<div class="site-header">'
        '<div class="brand"><span class="brand-icon">♻️</span>Smart Recycling Assistant</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_title_block() -> None:
    """Title + short description. The HTML has no indentation on purpose (Markdown would treat it as code)."""
    title = html.escape(config.HERO_TITLE)
    description = html.escape(config.HERO_DESCRIPTION)
    st.markdown(
        f'<div class="hero-title">{title}</div><p class="hero-description">{description}</p>',
        unsafe_allow_html=True,
    )


def show_picture_in_upload_box(picture: Image.Image) -> None:
    """
    Put a picture INSIDE the upload box. The box keeps its size: the picture is only
    its background (see "has picture" rules below). This emits a small <style> block.
    """
    uri = picture_data_uri(picture)
    box = '.stApp .st-key-top [data-testid="stFileUploaderDropzone"]'
    st.markdown(
        "<style>"
        f'{box} {{ background: #FFFFFF url("{uri}") center / contain no-repeat !important; '
        "justify-content: flex-end !important; }"
        f'{box}::before {{ content: none !important; }}'
        '.stApp .st-key-top [data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }'
        "</style>",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------ Result boxes
def render_result_box(result) -> None:
    """Box with the detected category and the confidence."""
    main = result.main
    percent = main.confidence * 100
    counts = Counter(d.category for d in result.detections)
    summary = ", ".join(f"{name} ×{n}" for name, n in counts.most_common())
    extra = ""
    if len(result.detections) > 1:
        extra = f'<div class="result-extra">Detected {len(result.detections)} items: {html.escape(summary)}</div>'
    st.markdown(
        '<div class="result-box">'
        '<div class="result-label">Detected category</div>'
        f'<div class="result-category">{html.escape(main.category)}</div>'
        f'<div class="confidence-row"><span>Confidence</span><b>{percent:.1f}%</b></div>'
        f'<div class="confidence-bar"><div style="width:{percent:.1f}%"></div></div>'
        f"{extra}"
        "</div>",
        unsafe_allow_html=True,
    )


def render_todo_box(result) -> None:
    """Box with the recycling guidelines ("What to do") for the detected categories."""
    categories = list(dict.fromkeys(d.category for d in result.detections))   # best confidence first
    parts = ['<div class="todo-box"><div class="todo-title">What to do</div>']
    for category in categories:
        steps = get_guidelines(category)
        if len(categories) > 1:
            parts.append(f'<div class="todo-category">{html.escape(category)}</div>')
        if steps is None:
            parts.append("<p>No recycling guidelines are available for this category yet.</p>")
        else:
            parts.append("<ul>" + "".join(f"<li>{html.escape(s)}</li>" for s in steps) + "</ul>")
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_results(result) -> None:
    if result.main is None:
        st.warning("No waste item was detected. Please try a clearer image with the item in view.")
        return
    render_result_box(result)
    if result.main.confidence < config.LOW_CONFIDENCE_THRESHOLD:
        st.warning("Low confidence. Please upload a clearer image for better results.")
    render_todo_box(result)


# ------------------------------------------------------------------ Upload flow
def saved_result_for(file_key: str):
    """The detection result saved for this exact file (None if there is none yet)."""
    saved = st.session_state.get("detection")
    return saved["result"] if saved and saved["key"] == file_key else None


def run_detection(uploaded) -> None:
    """Everything that happens after a file is uploaded."""
    try:
        image = load_image(uploaded)
    except Exception:
        st.error("This file could not be read as an image. Please upload a JPG or PNG file.")
        return

    file_key = f"{uploaded.name}:{uploaded.size}"
    result = saved_result_for(file_key)

    if st.button("Detect Waste", key="detect_btn"):
        try:
            with st.spinner("Detecting..."):
                result = predict(image)
            st.session_state["detection"] = {"key": file_key, "result": result}
        except ModelNotConnectedError as error:
            show_picture_in_upload_box(image)
            st.info(
                f"🌱 {error}\n\n"
                "Add the trained model file to the `model/` folder and restart the app. "
                "See README.md for the exact steps."
            )
            return

    if result is None:
        show_picture_in_upload_box(image)                       # just the uploaded photo
        return
    show_picture_in_upload_box(Image.fromarray(np.asarray(result.annotated_image)))   # photo + boxes
    render_results(result)


def render_top_section() -> None:
    """One column: title, upload box, button, result boxes. The tree picture is painted behind (CSS)."""
    with st.container(key="top"):
        left, _right = st.columns([45, 55], gap="small")
        with left:
            render_title_block()
            uploaded = st.file_uploader(
                "Upload an image", type=config.ALLOWED_IMAGE_TYPES, label_visibility="collapsed"
            )
            if uploaded is None:
                st.session_state.pop("detection", None)         # forget the old result
                return
            run_detection(uploaded)


# ------------------------------------------------------------------ Page
def main() -> None:
    load_css()
    inject_hero_image()
    render_header()
    render_top_section()


main()
