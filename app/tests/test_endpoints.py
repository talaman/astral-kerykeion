import httpx
import pytest

BASE_URL = "http://127.0.0.1:8002"

@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        # Before tests, clear cache
        client.delete("/cache/clear")
        yield client
        # After tests, clear cache
        client.delete("/cache/clear")

def test_birth_chart_json_cache(client):
    params = {
        "name": "Ada Lovelace", "year": 1815, "month": 12, "day": 10,
        "hour": 6, "minute": 0, "city": "London", "lng": -0.1278,
        "lat": 51.5074, "tz_str": "Europe/London", "svg": False
    }
    
    # First request should be a MISS, status 200
    res1 = client.get("/charts/birth", params=params)
    assert res1.status_code == 200
    assert "application/json" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/charts/birth", params=params)
    assert res2.status_code == 200

def test_birth_chart_svg_cache(client):
    params = {
        "name": "Ada Lovelace", "year": 1815, "month": 12, "day": 10,
        "hour": 6, "minute": 0, "city": "London", "lng": -0.1278,
        "lat": 51.5074, "tz_str": "Europe/London", "svg": True
    }
    
    # First request should be a MISS, status 200
    res1 = client.get("/charts/birth", params=params)
    assert res1.status_code == 200
    assert "image/svg+xml" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/charts/birth", params=params)
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
    res1 = client.get("/charts/synastry", params=params)
    assert res1.status_code == 200
    assert "application/json" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/charts/synastry", params=params)
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
    res1 = client.get("/charts/synastry", params=params)
    assert res1.status_code == 200
    assert "image/svg+xml" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/charts/synastry", params=params)
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
    res1 = client.get("/charts/transit", params=params)
    assert res1.status_code == 200
    assert "application/json" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/charts/transit", params=params)
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
    res1 = client.get("/charts/transit", params=params)
    assert res1.status_code == 200
    assert "image/svg+xml" in res1.headers["content-type"]
    
    # Second request should be a HIT, status 200
    res2 = client.get("/charts/transit", params=params)
    assert res2.status_code == 200

def test_cache_endpoints(client):
    res = client.get("/cache/info")
    assert res.status_code == 200
    data = res.json()
    assert "cache_items" in data
    # We should have exactly 6 unique requests (JSON/SVG for Birth, Synastry, Transit)
    assert data["cache_items"] == 6

    res = client.delete("/cache/clear")
    assert res.status_code == 200

    res = client.get("/cache/info")
    assert res.json()["cache_items"] == 0
