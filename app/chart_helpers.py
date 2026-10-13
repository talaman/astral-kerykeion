"""Reusable helpers for chart generation and subject creation."""

import base64
import logging
import os
import shutil
import uuid
from pathlib import Path
from xml.etree import ElementTree

from kerykeion import AstrologicalSubjectFactory, ChartDrawer

logger = logging.getLogger(__name__)

BASE_OUTPUT_DIR = os.getenv("CHART_OUTPUT_DIR", "/tmp/astral-kerykeion/output")
CSS_PATH = "./themes/astral.css"
LOGO_PATH = Path(__file__).resolve().parent / "assets" / "astralguru-logo.svg"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"

ElementTree.register_namespace("", SVG_NAMESPACE)
ElementTree.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def create_subject(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    city: str,
    nation: str,
    lng: float,
    lat: float,
    tz_str: str,
):
    """Create an AstrologicalSubject from birth data (offline)."""
    return AstrologicalSubjectFactory.from_birth_data(
        name, year, month, day, hour, minute,
        city, nation,
        lng=lng, lat=lat, tz_str=tz_str, online=False,
    )


def embed_css_in_svg(svg_text: str, css_path: str = CSS_PATH) -> str:
    """Read *css_path* and inject it into *svg_text*."""
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
    except FileNotFoundError:
        return svg_text

    if "</style>" in svg_text:
        return svg_text.replace("</style>", f"\n{css_content}\n</style>")

    if "<svg" in svg_text:
        svg_start = svg_text.find("<svg")
        if svg_start != -1:
            svg_tag_end = svg_text.find(">", svg_start)
            if svg_tag_end != -1:
                style_tag = (
                    f'\n<style type="text/css">\n<![CDATA[\n{css_content}\n]]>\n</style>\n'
                )
                return svg_text[: svg_tag_end + 1] + style_tag + svg_text[svg_tag_end + 1 :]

    return svg_text


def embed_logo_in_svg(svg_text: str, chart_type: str = "chart") -> str:
    """Embed a full-color logo stamp aligned with the chart's lower content."""
    root = ElementTree.fromstring(svg_text)
    origin_x, origin_y, width, height = map(float, root.attrib["viewBox"].split())
    short_side = min(width, height)
    wide_chart = chart_type in {"synastry", "transit", "solar_return", "lunar_return"}
    size_ratio = 0.34 if wide_chart else 0.18
    size = short_side * size_ratio
    margin = short_side * (0.08 if wide_chart else 0.02)
    bottom_margin = short_side * 0.06
    logo_data = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    ElementTree.SubElement(root, f"{{{SVG_NAMESPACE}}}image", {
        "id": "astralguru-logo-stamp",
        "x": f"{origin_x + width - size - margin:g}",
        "y": f"{origin_y + height - size - bottom_margin:g}",
        "width": f"{size:g}",
        "height": f"{size:g}",
        "preserveAspectRatio": "xMidYMid meet",
        "pointer-events": "none",
        "href": f"data:image/svg+xml;base64,{logo_data}",
        "{http://www.w3.org/1999/xlink}href": f"data:image/svg+xml;base64,{logo_data}",
    })
    return ElementTree.tostring(root, encoding="unicode")


def generate_svg(chart_data, prefix: str = "chart", chart_language: str = "ES") -> str:
    """Draw a chart to SVG, embed CSS and branding, and return the SVG string.

    Handles temp-directory creation and cleanup internally.
    """
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
    temp_dir = os.path.join(BASE_OUTPUT_DIR, uuid.uuid4().hex)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        chart = ChartDrawer(chart_data=chart_data, chart_language=chart_language, style="modern")
        filename = f"{prefix}_{uuid.uuid4().hex}"
        chart.save_svg(output_path=Path(temp_dir), filename=filename)

        svg_path = os.path.join(temp_dir, f"{filename}.svg")
        if not os.path.exists(svg_path):
            raise RuntimeError("SVG generation failed: no file created")

        with open(svg_path, "r", encoding="utf-8") as f:
            svg_text = f.read()

        return embed_logo_in_svg(embed_css_in_svg(svg_text), chart_type=prefix)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
