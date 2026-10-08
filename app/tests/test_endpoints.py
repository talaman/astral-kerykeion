import os
from xml.etree import ElementTree

os.environ["ENABLE_ADMIN_ENDPOINTS"] = "true"

from fastapi.testclient import TestClient
import main as chart_api
from main import app
import pytest
from kerykeion.settings.config_constants import DEFAULT_ACTIVE_ASPECTS, PREDICTIVE_ACTIVE_ASPECTS

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        # Before tests, clear cache
        client.delete("/cache/clear")
        yield client
        # After tests, clear cache
        client.delete("/cache/clear")


def test_healthz(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_birth_chart_json_cache(client):
    params = {
        "name": "Ada Lovelace", "year": 1815, "month": 12, "day": 10,
        "hour": 6, "minute": 0, "city": "London", "lng": -0.1278,
        "lat": 51.5074, "tz_str": "Europe/London", "svg": False
    }
    
    # First request should be a MISS, status 200
    res1 = client.get("/gen/birth", params=params)
    assert res1.status_code == 200
    assert "application/json" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/birth", params=params)
    assert res2.status_code == 200

def test_birth_chart_svg_cache(client):
    params = {
        "name": "Ada Lovelace", "year": 1815, "month": 12, "day": 10,
        "hour": 6, "minute": 0, "city": "London", "lng": -0.1278,
        "lat": 51.5074, "tz_str": "Europe/London", "svg": True
    }
    
    # First request should be a MISS, status 200
    res1 = client.get("/gen/birth", params=params)
    assert res1.status_code == 200
    assert "image/svg+xml" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/birth", params=params)
    assert res2.status_code == 200

def test_synastry_chart_json_cache(client):
    params = {
        "name1": "Romeo", "year1": 1990, "month1": 1, "day1": 1, 
        "hour1": 12, "minute1": 0, "city1": "London", "lng1": -0.1278, 
        "lat1": 51.5074, "tz_str1": "Europe/London", "nation1": "UK",
        "name2": "Juliet", "year2": 1995, "month2": 2, "day2": 14, 
        "hour2": 12, "minute2": 0, "city2": "Paris", "lng2": 2.3522, 
        "lat2": 48.8566, "tz_str2": "Europe/Paris", "nation2": "FR",
        "svg": False
    }

    # First request should be a MISS, status 200
    res1 = client.get("/gen/synastry", params=params)
    assert res1.status_code == 200
    assert "application/json" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/synastry", params=params)
    assert res2.status_code == 200

def test_synastry_chart_svg_cache(client):
    params = {
        "name1": "Romeo", "year1": 1990, "month1": 1, "day1": 1, 
        "hour1": 12, "minute1": 0, "city1": "London", "lng1": -0.1278, 
        "lat1": 51.5074, "tz_str1": "Europe/London", "nation1": "UK",
        "name2": "Juliet", "year2": 1995, "month2": 2, "day2": 14, 
        "hour2": 12, "minute2": 0, "city2": "Paris", "lng2": 2.3522, 
        "lat2": 48.8566, "tz_str2": "Europe/Paris", "nation2": "FR",
        "svg": True
    }

    # First request should be a MISS, status 200
    res1 = client.get("/gen/synastry", params=params)
    assert res1.status_code == 200
    assert "image/svg+xml" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/synastry", params=params)
    assert res2.status_code == 200

def test_transit_chart_json_cache(client):
    params = {
        "name": "Romeo", "year": 1990, "month": 1, "day": 1,
        "hour": 12, "minute": 0, "city": "London", "lng": -0.1278,
        "lat": 51.5074, "tz_str": "Europe/London", "nation": "UK",
        "t_year": 2024, "t_month": 1, "t_day": 1, "t_hour": 12,
        "t_minute": 0, "t_city": "Paris", "t_lng": 2.3522,
        "t_lat": 48.8566, "t_tz_str": "Europe/Paris", "t_nation": "France",
        "svg": False
    }

    # First request should be a MISS, status 200
    res1 = client.get("/gen/transit", params=params)
    assert res1.status_code == 200
    assert "application/json" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/transit", params=params)
    assert res2.status_code == 200

def test_transit_chart_svg_cache(client):
    params = {
        "name": "Romeo", "year": 1990, "month": 1, "day": 1,
        "hour": 12, "minute": 0, "city": "London", "lng": -0.1278,
        "lat": 51.5074, "tz_str": "Europe/London", "nation": "UK",
        "t_year": 2024, "t_month": 1, "t_day": 1, "t_hour": 12,
        "t_minute": 0, "t_city": "Paris", "t_lng": 2.3522,
        "t_lat": 48.8566, "t_tz_str": "Europe/Paris", "t_nation": "France",
        "svg": True
    }

    # First request should be a MISS, status 200
    res1 = client.get("/gen/transit", params=params)
    assert res1.status_code == 200
    assert "image/svg+xml" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/transit", params=params)
    assert res2.status_code == 200

def test_solar_return_chart_json_cache(client):
    params = {
        "name": "Ada Lovelace", "year": 1815, "month": 12, "day": 10,
        "hour": 6, "minute": 0, "city": "London", "lng": -0.1278,
        "lat": 51.5074, "tz_str": "Europe/London", "nation": "UK",
        "return_year": 2024, "svg": False
    }

    # First request should be a MISS, status 200
    res1 = client.get("/gen/solar-return", params=params)
    assert res1.status_code == 200
    assert "application/json" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/solar-return", params=params)
    assert res2.status_code == 200

def test_solar_return_chart_svg_cache(client):
    params = {
        "name": "Ada Lovelace", "year": 1815, "month": 12, "day": 10,
        "hour": 6, "minute": 0, "city": "London", "lng": -0.1278,
        "lat": 51.5074, "tz_str": "Europe/London", "nation": "UK",
        "return_year": 2024, "svg": True
    }

    # First request should be a MISS, status 200
    res1 = client.get("/gen/solar-return", params=params)
    assert res1.status_code == 200
    assert "image/svg+xml" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/solar-return", params=params)
    assert res2.status_code == 200

def test_lunar_return_chart_json_cache(client):
    params = {
        "name": "Ada Lovelace", "year": 1815, "month": 12, "day": 10,
        "hour": 6, "minute": 0, "city": "London", "lng": -0.1278,
        "lat": 51.5074, "tz_str": "Europe/London", "nation": "UK",
        "return_year": 2024, "return_month": 1, "return_day": 1, "svg": False
    }

    # First request should be a MISS, status 200
    res1 = client.get("/gen/lunar-return", params=params)
    assert res1.status_code == 200
    assert "application/json" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/lunar-return", params=params)
    assert res2.status_code == 200

def test_lunar_return_chart_svg_cache(client):
    params = {
        "name": "Ada Lovelace", "year": 1815, "month": 12, "day": 10,
        "hour": 6, "minute": 0, "city": "London", "lng": -0.1278,
        "lat": 51.5074, "tz_str": "Europe/London", "nation": "UK",
        "return_year": 2024, "return_month": 1, "return_day": 1, "svg": True
    }

    # First request should be a MISS, status 200
    res1 = client.get("/gen/lunar-return", params=params)
    assert res1.status_code == 200
    assert "image/svg+xml" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/lunar-return", params=params)
    assert res2.status_code == 200

def test_composite_chart_json_cache(client):
    params = {
        "name1": "Romeo", "year1": 1990, "month1": 1, "day1": 1,
        "hour1": 12, "minute1": 0, "city1": "London", "lng1": -0.1278,
        "lat1": 51.5074, "tz_str1": "Europe/London", "nation1": "UK",
        "name2": "Juliet", "year2": 1995, "month2": 2, "day2": 14,
        "hour2": 12, "minute2": 0, "city2": "Paris", "lng2": 2.3522,
        "lat2": 48.8566, "tz_str2": "Europe/Paris", "nation2": "FR",
        "svg": False
    }

    # First request should be a MISS, status 200
    res1 = client.get("/gen/composite", params=params)
    assert res1.status_code == 200
    assert "application/json" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/composite", params=params)
    assert res2.status_code == 200

def test_composite_chart_svg_cache(client):
    params = {
        "name1": "Romeo", "year1": 1990, "month1": 1, "day1": 1,
        "hour1": 12, "minute1": 0, "city1": "London", "lng1": -0.1278,
        "lat1": 51.5074, "tz_str1": "Europe/London", "nation1": "UK",
        "name2": "Juliet", "year2": 1995, "month2": 2, "day2": 14,
        "hour2": 12, "minute2": 0, "city2": "Paris", "lng2": 2.3522,
        "lat2": 48.8566, "tz_str2": "Europe/Paris", "nation2": "FR",
        "svg": True
    }

    # First request should be a MISS, status 200
    res1 = client.get("/gen/composite", params=params)
    assert res1.status_code == 200
    assert "image/svg+xml" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/gen/composite", params=params)
    assert res2.status_code == 200

def test_cache_endpoints(client):
    res = client.delete("/cache/clear")
    assert res.status_code == 200

    res = client.get("/cache/info")
    assert res.status_code == 200
    data = res.json()
    assert "cache_items" in data
    assert data["cache_items"] == 0

    params = {
        "name1": "Romeo", "year1": 1990, "month1": 1, "day1": 1,
        "hour1": 12, "minute1": 0, "city1": "London", "lng1": -0.1278,
        "lat1": 51.5074, "tz_str1": "Europe/London", "nation1": "UK",
        "name2": "Juliet", "year2": 1995, "month2": 2, "day2": 14,
        "hour2": 12, "minute2": 0, "city2": "Paris", "lng2": 2.3522,
        "lat2": 48.8566, "tz_str2": "Europe/Paris", "nation2": "FR",
        "svg": False
    }

    res = client.get("/gen/composite", params=params)
    assert res.status_code == 200

    res = client.get("/gen/composite", params=params)
    assert res.status_code == 200

    res = client.get("/cache/info")
    assert res.status_code == 200
    data = res.json()
    assert "cache_items" in data
    assert data["cache_items"] == 1
    res = client.delete("/cache/clear")
    assert res.status_code == 200

    res = client.get("/cache/info")
    assert res.json()["cache_items"] == 0


def test_cache_details_hidden_by_default(client):
    res = client.get("/cache/info")
    assert res.status_code == 200
    data = res.json()
    assert "cached_keys" not in data
    assert "access_order" not in data


@pytest.mark.parametrize("chart_type", [
    "birth", "synastry", "transit", "solar-return", "lunar-return", "composite",
])
def test_v6_json_and_svg_use_same_aspects(client, monkeypatch, chart_type):
    natal_params = {
        "name": "Ada Lovelace", "year": 1815, "month": 12, "day": 10,
        "hour": 6, "minute": 0, "city": "London", "nation": "UK",
        "lng": -0.1278, "lat": 51.5074, "tz_str": "Europe/London",
    }
    partner_params = {
        **natal_params, "name": "Partner", "year": 1995, "month": 2, "day": 14,
    }
    params = natal_params.copy()
    if chart_type in {"synastry", "composite"}:
        params = {f"{key}1": value for key, value in natal_params.items()}
        params.update({f"{key}2": value for key, value in partner_params.items()})
    elif chart_type == "transit":
        params.update({
            f"t_{key}": value for key, value in partner_params.items() if key != "name"
        })
    elif chart_type in {"solar-return", "lunar-return"}:
        params["return_year"] = 2024
        if chart_type == "lunar-return":
            params.update(return_month=1, return_day=1)

    client.delete("/cache/clear")
    json_response = client.get(f"/gen/{chart_type}", params=params)
    assert json_response.status_code == 200

    rendered_charts = []
    original_generate_svg = chart_api.generate_svg

    def capture_chart(chart_data, **kwargs):
        rendered_charts.append(chart_data)
        return original_generate_svg(chart_data, **kwargs)

    monkeypatch.setattr(chart_api, "generate_svg", capture_chart)
    svg_response = client.get(f"/gen/{chart_type}", params={**params, "svg": True})
    assert svg_response.status_code == 200
    svg_root = ElementTree.fromstring(svg_response.text)
    assert svg_root.tag == "{http://www.w3.org/2000/svg}svg"
    svg_attributes = " ".join(
        value for element in svg_root.iter() for value in element.attrib.values()
    )
    for sign_index in range(12):
        assert f"var(--kerykeion-modern-zodiac-bg-{sign_index})" in svg_attributes
        assert (
            f"--kerykeion-modern-zodiac-bg-{sign_index}: "
            f"var(--kerykeion-chart-color-zodiac-bg-{sign_index});"
        ) in svg_response.text
    assert "--kerykeion-modern-zodiac-bg-opacity: 1;" in svg_response.text
    assert "--kerykeion-color-primary: #65cc8a;" in svg_response.text
    assert "--kerykeion-color-warning: #947000;" in svg_response.text
    assert '[*|node="ZodiacBackgrounds"] {' in svg_response.text
    for sign_index in (0, 4, 8):
        assert f"--kerykeion-chart-color-zodiac-icon-{sign_index}: #7c190d;" in svg_response.text
    for sign_index in (3, 7, 11):
        assert f"--kerykeion-chart-color-zodiac-icon-{sign_index}: #c9edff;" in svg_response.text
    for sign_index in (2, 6, 10):
        assert f"--kerykeion-chart-color-zodiac-icon-{sign_index}: #185c34;" in svg_response.text
    for sign_index in (1, 5, 9):
        assert f"--kerykeion-chart-color-zodiac-icon-{sign_index}: #ffe08a;" in svg_response.text
    assert len(rendered_charts) == 1
    chart_data = rendered_charts[0]
    assert json_response.json()["aspects"] == [aspect.model_dump() for aspect in chart_data.aspects]
    expected_aspects = (
        PREDICTIVE_ACTIVE_ASPECTS
        if chart_type in {"transit", "solar-return", "lunar-return"}
        else DEFAULT_ACTIVE_ASPECTS
    )
    assert chart_data.active_aspects == expected_aspects
    assert len(chart_data.active_points) == 14


def test_cache_endpoints_disabled_when_admin_is_off(client, monkeypatch):
    monkeypatch.setenv("ENABLE_ADMIN_ENDPOINTS", "false")

    res = client.get("/cache/info")
    assert res.status_code == 404

    res = client.delete("/cache/clear")
    assert res.status_code == 404

    res = client.put("/cache/config", params={"max_items": 10})
    assert res.status_code == 404

    monkeypatch.setenv("ENABLE_ADMIN_ENDPOINTS", "true")
