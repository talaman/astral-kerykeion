"""Reusable helpers for chart generation and subject creation."""

import logging
import os
import shutil
import uuid
from pathlib import Path

from kerykeion import AstrologicalSubjectFactory
from kerykeion.charts.chart_drawer import ChartDrawer

logger = logging.getLogger(__name__)

BASE_OUTPUT_DIR = "./temp/output"
CSS_PATH = "./themes/astral.css"


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


def generate_svg(chart_data, prefix: str = "chart", chart_language: str = "ES") -> str:
    """Draw a chart to SVG, embed CSS, and return the SVG string.

    Handles temp-directory creation and cleanup internally.
    """
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
    temp_dir = os.path.join(BASE_OUTPUT_DIR, uuid.uuid4().hex)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        chart = ChartDrawer(chart_data=chart_data, chart_language=chart_language)
        filename = f"{prefix}_{uuid.uuid4().hex}"
        chart.save_svg(output_path=Path(temp_dir), filename=filename)

        svg_path = os.path.join(temp_dir, f"{filename}.svg")
        if not os.path.exists(svg_path):
            raise RuntimeError("SVG generation failed: no file created")

        with open(svg_path, "r", encoding="utf-8") as f:
            svg_text = f.read()

        return embed_css_in_svg(svg_text)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
