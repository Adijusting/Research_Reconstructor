"""
vision.py
---------
Handles:
  1. Extraction of embedded charts/figures from research-paper PDFs.
  2. PIL-based image optimization (downscaling + re-compression) BEFORE any
     payload is sent to the Groq Vision API.
  3. Calling a Groq-hosted vision model (multimodal) to analyze each chart
     and return a structured description.

Historical bottlenecks resolved here (do not "simplify" these away):
  - Early iterations sent raw, full-resolution PDF-extracted images straight
    to a vision API (originally Gemini) and were rate-limited almost
    immediately because of massive token payloads. The PIL compression
    buffer below is mandatory, not optional.
  - Long-running generation calls were previously killed by Windows with a
    `wsarecv` socket abort. The Groq client below is constructed with a
    custom httpx.Client(timeout=180.0) to force the OS to hold the socket
    open until generation completes.
"""

import os
import io
import base64
import logging
from typing import List, Dict, Optional

import fitz  # PyMuPDF
import httpx
from PIL import Image
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# NOTE: Groq rotates/deprecates its model lineup frequently. Check
# https://console.groq.com/docs/vision for the current production-ready
# vision-capable model before relying on this default.
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
GROQ_TIMEOUT_SECONDS = float(os.getenv("GROQ_TIMEOUT_SECONDS", "180"))

# --- Compression targets ---
# Downscaling to this max dimension + re-encoding to JPEG at this quality
# reliably keeps chart images well under vision-model token limits while
# still being legible enough for the vision model to analyze accurately.
MAX_DIMENSION_PX = 1024
JPEG_QUALITY = 75


def _build_groq_client() -> Groq:
    """
    Builds the Groq client with a custom httpx.Client timeout.

    CRITICAL: Without the explicit httpx.Client(timeout=180.0) here, long
    generations on Windows can trigger a `wsarecv` socket-abort error
    because the OS default socket timeout is too aggressive for slow
    multimodal generations.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set. Populate your .env file first.")

    http_client = httpx.Client(timeout=GROQ_TIMEOUT_SECONDS)
    return Groq(api_key=GROQ_API_KEY, http_client=http_client)


client = _build_groq_client()


# ---------------------------------------------------------------------------
# PDF -> raw chart images
# ---------------------------------------------------------------------------
def extract_images_from_pdf(pdf_path: str) -> List[Image.Image]:
    """
    Pulls every embedded raster image (chart, figure, diagram) out of a PDF
    using PyMuPDF and returns them as in-memory PIL Image objects.
    """
    images: List[Image.Image] = []

    with fitz.open(pdf_path) as doc:
        for page_index in range(len(doc)):
            page = doc[page_index]
            image_list = page.get_images(full=True)

            for img_info in image_list:
                xref = img_info[0]
                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    images.append(pil_image)
                except Exception as exc:
                    logger.warning(
                        "Failed to extract image (xref=%s, page=%s): %s",
                        xref, page_index, exc,
                    )

    logger.info("Extracted %d image(s) from %s", len(images), pdf_path)
    return images


# ---------------------------------------------------------------------------
# Compression buffer (MANDATORY step)
# ---------------------------------------------------------------------------
def compress_image(image: Image.Image) -> bytes:
    """
    Downscales an image to MAX_DIMENSION_PX on its longest side and
    re-encodes it as a JPEG at JPEG_QUALITY.

    This step is what prevents API rate-limit blocks caused by oversized
    multimodal payloads. Do not skip or bypass this function when sending
    images to the Groq Vision API.
    """
    working_image = image.copy()
    working_image.thumbnail((MAX_DIMENSION_PX, MAX_DIMENSION_PX), Image.LANCZOS)

    buffer = io.BytesIO()
    working_image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return buffer.getvalue()


def _image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


# ---------------------------------------------------------------------------
# Groq vision chart analysis
# ---------------------------------------------------------------------------
def analyze_chart(image: Image.Image, context_hint: str = "") -> Optional[Dict]:
    """
    Sends a single (already-compressed) chart image to the configured Groq
    vision model for analysis.

    Returns a dict like:
        {"description": "...", "key_insight": "..."}
    or None if the API call fails / the model declines to analyze the image
    (e.g., because it isn't actually a chart).

    NOTE: Callers (e.g., the docx compiler) must NOT assume this always
    returns a dict. See Section 5 of the master context: the compiler
    previously crashed on skipped images. This function may legitimately
    return a plain fallback string wrapped in a dict, or None.
    """
    try:
        compressed_bytes = compress_image(image)
        b64_image = _image_to_base64(compressed_bytes)

        prompt = (
            "You are analyzing a chart or figure extracted from an academic "
            "research paper. Describe what the chart shows and state the "
            "single most important quantitative insight. If this image is "
            "not actually a meaningful chart/figure (e.g., it's a logo, "
            "icon, or decorative graphic), respond with exactly: SKIP."
        )
        if context_hint:
            prompt += f"\n\nSurrounding paper context: {context_hint}"

        response = client.chat.completions.create(
            model=GROQ_VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=400,
        )

        content = response.choices[0].message.content.strip()

        if content.upper() == "SKIP" or not content:
            logger.info("Vision model marked an image as non-chart / skippable.")
            return {"skipped": True, "description": "Image skipped (not a meaningful chart)."}

        return {"skipped": False, "description": content}

    except Exception as exc:
        logger.error("Groq vision analysis failed: %s", exc)
        # Return a graceful fallback dict rather than raising, so downstream
        # consumers (docx compiler) never receive a bare string here.
        return {"skipped": True, "description": "Chart analysis unavailable due to an API error."}


def analyze_charts_from_pdf(pdf_path: str, context_hint: str = "") -> List[Dict]:
    """
    Full convenience pipeline: extract all chart images from a PDF, compress
    each one, and run Groq vision analysis on each.
    """
    images = extract_images_from_pdf(pdf_path)
    results = []

    for idx, image in enumerate(images):
        logger.info("Analyzing chart %d/%d...", idx + 1, len(images))
        result = analyze_chart(image, context_hint=context_hint)
        results.append(result)

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python vision.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    analyses = analyze_charts_from_pdf(pdf_path)
    for i, analysis in enumerate(analyses):
        print(f"\n--- Chart {i + 1} ---")
        print(analysis["description"])