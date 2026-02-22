from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from kerykeion import AspectsFactory, to_context
from kerykeion.planetary_return_factory import PlanetaryReturnFactory
from kerykeion.composite_subject_factory import CompositeSubjectFactory
from kerykeion.chart_data_factory import ChartDataFactory

import json
import logging

from cache_service import CacheService
from chart_helpers import create_subject, generate_svg

# ---------------------------------------------------------------------------
# App & middleware
# ---------------------------------------------------------------------------

openapi_tags = [
    {
        "name": "General",
        "description": "Health check and root endpoint.",
    },
    {
        "name": "Cache",
        "description": "Inspect and manage the in-memory response cache.",
    },
    {
        "name": "Charts",
        "description": "Natal, synastry, transit, return, and composite chart endpoints.",
    },
]

app = FastAPI(openapi_tags=openapi_tags)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = CacheService()

# ---------------------------------------------------------------------------
# Shared response builder
# ---------------------------------------------------------------------------


def _cached_response(cache_key: str, svg: bool) -> Response | None:
    """Return a cached Response or None."""
    hit = cache.get(cache_key)
    if hit is None:
        return None
    media = "image/svg+xml" if svg else "application/json"
    return Response(content=hit["content"], media_type=media)


def _json_response(data: dict, cache_key: str) -> Response:
    """Serialise *data* to JSON, cache it, and return a Response."""
    content = json.dumps(data, indent=2)
    cache.put(cache_key, content, "application/json")
    return Response(content=content, media_type="application/json")


def _svg_response(chart_data, prefix: str, cache_key: str) -> Response:
    """Generate an SVG from *chart_data*, cache it, and return a Response."""
    try:
        svg_text = generate_svg(chart_data, prefix=prefix)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVG generation failed: {e}")
    cache.put(cache_key, svg_text, "image/svg+xml")
    return Response(content=svg_text, media_type="image/svg+xml")


# ---------------------------------------------------------------------------
# Cache management endpoints
# ---------------------------------------------------------------------------


@app.get("/", tags=["General"])
async def root():
    return {"message": "Hello World"}


@app.get("/cache/info", tags=["Cache"])
async def cache_info():
    return cache.info()


@app.delete("/cache/clear", tags=["Cache"])
async def clear_cache():
    cache.clear()
    return {"message": "Cache cleared successfully"}


@app.put("/cache/config", tags=["Cache"])
async def update_cache_config(max_items: int = None, max_size_mb: float = None):
    return cache.update_config(max_items, max_size_mb)


# ---------------------------------------------------------------------------
# /gen  &  /gen/birth
# ---------------------------------------------------------------------------


@app.get("/gen/birth", response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}}, tags=["Charts"])
@app.get("/gen", response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}}, tags=["Charts"])
async def get_chart(
    name: str = Query(..., description="Name of the subject", json_schema_extra={"example": "Ada Lovelace"}),
    year: int = Query(..., description="Year of birth", json_schema_extra={"example": 1815}),
    month: int = Query(..., description="Month of birth", json_schema_extra={"example": 12}),
    day: int = Query(..., description="Day of birth", json_schema_extra={"example": 10}),
    hour: int = Query(..., description="Hour of birth", json_schema_extra={"example": 6}),
    minute: int = Query(..., description="Minute of birth", json_schema_extra={"example": 0}),
    city: str = Query(..., description="City of birth", json_schema_extra={"example": "London"}),
    lng: float = Query(..., description="Longitude of birth location", json_schema_extra={"example": -0.1278}),
    lat: float = Query(..., description="Latitude of birth location", json_schema_extra={"example": 51.5074}),
    tz_str: str = Query(..., description="Timezone string of birth location", json_schema_extra={"example": "Europe/London"}),
    nation: str = Query(" ", description="nation of birth", json_schema_extra={"example": "United Kingdom"}),
    svg: bool = Query(False, description="Return SVG image if true, else return JSON"),
):
    cache_key = cache.make_key({
        "name": name, "year": year, "month": month, "day": day,
        "hour": hour, "minute": minute, "city": city, "lng": lng,
        "lat": lat, "tz_str": tz_str, "nation": nation, "svg": svg,
    })

    cached = _cached_response(cache_key, svg)
    if cached:
        return cached

    subject = create_subject(name, year, month, day, hour, minute, city, nation, lng, lat, tz_str)
    aspects_data = AspectsFactory.single_chart_aspects(subject)
    context_text = to_context(subject)

    subject_dict = subject.model_dump()
    subject_dict["aspects"] = [a.model_dump() for a in aspects_data.aspects]
    subject_dict["context"] = context_text

    if not svg:
        return _json_response(subject_dict, cache_key)

    chart_data = ChartDataFactory.create_natal_chart_data(subject)
    return _svg_response(chart_data, "birth", cache_key)


# ---------------------------------------------------------------------------
# /gen/synastry
# ---------------------------------------------------------------------------


@app.get("/gen/synastry", response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}}, tags=["Charts"])
async def get_synastry_chart(
    name1: str = Query(..., description="Name of the first subject", json_schema_extra={"example": "Romeo"}),
    year1: int = Query(..., description="Year of birth", json_schema_extra={"example": 1990}),
    month1: int = Query(..., description="Month of birth", json_schema_extra={"example": 1}),
    day1: int = Query(..., description="Day of birth", json_schema_extra={"example": 1}),
    hour1: int = Query(..., description="Hour of birth", json_schema_extra={"example": 12}),
    minute1: int = Query(..., description="Minute of birth", json_schema_extra={"example": 0}),
    city1: str = Query(..., description="City of birth", json_schema_extra={"example": "London"}),
    lng1: float = Query(..., description="Longitude of birth location", json_schema_extra={"example": -0.1278}),
    lat1: float = Query(..., description="Latitude of birth location", json_schema_extra={"example": 51.5074}),
    tz_str1: str = Query(..., description="Timezone string of birth location", json_schema_extra={"example": "Europe/London"}),
    nation1: str = Query(" ", description="Nation of birth", json_schema_extra={"example": "United Kingdom"}),
    name2: str = Query(..., description="Name of the second subject", json_schema_extra={"example": "Juliet"}),
    year2: int = Query(..., description="Year of birth", json_schema_extra={"example": 1995}),
    month2: int = Query(..., description="Month of birth", json_schema_extra={"example": 2}),
    day2: int = Query(..., description="Day of birth", json_schema_extra={"example": 14}),
    hour2: int = Query(..., description="Hour of birth", json_schema_extra={"example": 12}),
    minute2: int = Query(..., description="Minute of birth", json_schema_extra={"example": 0}),
    city2: str = Query(..., description="City of birth", json_schema_extra={"example": "Paris"}),
    lng2: float = Query(..., description="Longitude of birth location", json_schema_extra={"example": 2.3522}),
    lat2: float = Query(..., description="Latitude of birth location", json_schema_extra={"example": 48.8566}),
    tz_str2: str = Query(..., description="Timezone string of birth location", json_schema_extra={"example": "Europe/Paris"}),
    nation2: str = Query(" ", description="Nation of birth", json_schema_extra={"example": "France"}),
    svg: bool = Query(False, description="Return SVG image if true, else return JSON"),
):
    cache_key = cache.make_key({
        "name1": name1, "year1": year1, "month1": month1, "day1": day1,
        "hour1": hour1, "minute1": minute1, "city1": city1, "lng1": lng1,
        "lat1": lat1, "tz_str1": tz_str1, "nation1": nation1,
        "name2": name2, "year2": year2, "month2": month2, "day2": day2,
        "hour2": hour2, "minute2": minute2, "city2": city2, "lng2": lng2,
        "lat2": lat2, "tz_str2": tz_str2, "nation2": nation2,
        "svg": svg, "type": "synastry",
    })

    cached = _cached_response(cache_key, svg)
    if cached:
        return cached

    subject1 = create_subject(name1, year1, month1, day1, hour1, minute1, city1, nation1, lng1, lat1, tz_str1)
    subject2 = create_subject(name2, year2, month2, day2, hour2, minute2, city2, nation2, lng2, lat2, tz_str2)

    aspects_data = AspectsFactory.synastry_aspects(subject1, subject2)
    context_text = (
        f"--- Synastry Context ---\n\n"
        f"# {name1}'s Chart\n{to_context(subject1)}\n\n"
        f"# {name2}'s Chart\n{to_context(subject2)}"
    )

    response_data = {
        "subject1": subject1.model_dump(),
        "subject2": subject2.model_dump(),
        "aspects": [a.model_dump() for a in aspects_data.aspects],
        "context": context_text,
    }

    if not svg:
        return _json_response(response_data, cache_key)

    chart_data = ChartDataFactory.create_synastry_chart_data(subject1, subject2)
    return _svg_response(chart_data, "synastry", cache_key)


# ---------------------------------------------------------------------------
# /gen/transit
# ---------------------------------------------------------------------------


@app.get("/gen/transit", response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}}, tags=["Charts"])
async def get_transit_chart(
    name: str = Query(..., description="Name of the subject", json_schema_extra={"example": "Romeo"}),
    year: int = Query(..., description="Year of birth", json_schema_extra={"example": 1990}),
    month: int = Query(..., description="Month of birth", json_schema_extra={"example": 1}),
    day: int = Query(..., description="Day of birth", json_schema_extra={"example": 1}),
    hour: int = Query(..., description="Hour of birth", json_schema_extra={"example": 12}),
    minute: int = Query(..., description="Minute of birth", json_schema_extra={"example": 0}),
    city: str = Query(..., description="City of birth", json_schema_extra={"example": "London"}),
    lng: float = Query(..., description="Longitude of birth location", json_schema_extra={"example": -0.1278}),
    lat: float = Query(..., description="Latitude of birth location", json_schema_extra={"example": 51.5074}),
    tz_str: str = Query(..., description="Timezone string of birth location", json_schema_extra={"example": "Europe/London"}),
    nation: str = Query(" ", description="Nation of birth", json_schema_extra={"example": "United Kingdom"}),
    t_year: int = Query(..., description="Year of transit", json_schema_extra={"example": 2024}),
    t_month: int = Query(..., description="Month of transit", json_schema_extra={"example": 1}),
    t_day: int = Query(..., description="Day of transit", json_schema_extra={"example": 1}),
    t_hour: int = Query(..., description="Hour of transit", json_schema_extra={"example": 12}),
    t_minute: int = Query(..., description="Minute of transit", json_schema_extra={"example": 0}),
    t_city: str = Query(..., description="City of transit", json_schema_extra={"example": "Paris"}),
    t_lng: float = Query(..., description="Longitude of transit location", json_schema_extra={"example": 2.3522}),
    t_lat: float = Query(..., description="Latitude of transit location", json_schema_extra={"example": 48.8566}),
    t_tz_str: str = Query(..., description="Timezone string of transit location", json_schema_extra={"example": "Europe/Paris"}),
    t_nation: str = Query(" ", description="Nation of transit", json_schema_extra={"example": "France"}),
    svg: bool = Query(False, description="Return SVG image if true, else return JSON"),
):
    cache_key = cache.make_key({
        "name": name, "year": year, "month": month, "day": day,
        "hour": hour, "minute": minute, "city": city, "lng": lng,
        "lat": lat, "tz_str": tz_str, "nation": nation,
        "t_year": t_year, "t_month": t_month, "t_day": t_day,
        "t_hour": t_hour, "t_minute": t_minute, "t_city": t_city, "t_lng": t_lng,
        "t_lat": t_lat, "t_tz_str": t_tz_str, "t_nation": t_nation,
        "svg": svg, "type": "transit",
    })

    cached = _cached_response(cache_key, svg)
    if cached:
        return cached

    natal_subject = create_subject(name, year, month, day, hour, minute, city, nation, lng, lat, tz_str)
    transit_subject = create_subject("Transit", t_year, t_month, t_day, t_hour, t_minute, t_city, t_nation, t_lng, t_lat, t_tz_str)

    aspects_data = AspectsFactory.synastry_aspects(natal_subject, transit_subject)
    context_text = (
        f"--- Transit Context ---\n\n"
        f"# {name}'s Natal Chart\n{to_context(natal_subject)}\n\n"
        f"# Transit Sky Chart\n{to_context(transit_subject)}"
    )

    response_data = {
        "natal": natal_subject.model_dump(),
        "transit": transit_subject.model_dump(),
        "aspects": [a.model_dump() for a in aspects_data.aspects],
        "context": context_text,
    }

    if not svg:
        return _json_response(response_data, cache_key)

    chart_data = ChartDataFactory.create_transit_chart_data(natal_subject, transit_subject)
    return _svg_response(chart_data, "transit", cache_key)


# ---------------------------------------------------------------------------
# /gen/solar-return
# ---------------------------------------------------------------------------


@app.get("/gen/solar-return", response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}}, tags=["Charts"])
async def get_solar_return_chart(
    name: str = Query(..., description="Name of the subject", json_schema_extra={"example": "Ada Lovelace"}),
    year: int = Query(..., description="Year of birth", json_schema_extra={"example": 1815}),
    month: int = Query(..., description="Month of birth", json_schema_extra={"example": 12}),
    day: int = Query(..., description="Day of birth", json_schema_extra={"example": 10}),
    hour: int = Query(..., description="Hour of birth", json_schema_extra={"example": 6}),
    minute: int = Query(..., description="Minute of birth", json_schema_extra={"example": 0}),
    city: str = Query(..., description="City of birth", json_schema_extra={"example": "London"}),
    lng: float = Query(..., description="Longitude of birth location", json_schema_extra={"example": -0.1278}),
    lat: float = Query(..., description="Latitude of birth location", json_schema_extra={"example": 51.5074}),
    tz_str: str = Query(..., description="Timezone string of birth location", json_schema_extra={"example": "Europe/London"}),
    nation: str = Query(" ", description="Nation of birth", json_schema_extra={"example": "United Kingdom"}),
    return_year: int = Query(..., description="Year for the solar return", json_schema_extra={"example": 2024}),
    svg: bool = Query(False, description="Return SVG image if true, else return JSON"),
):
    cache_key = cache.make_key({
        "name": name, "year": year, "month": month, "day": day,
        "hour": hour, "minute": minute, "city": city, "lng": lng,
        "lat": lat, "tz_str": tz_str, "nation": nation,
        "return_year": return_year, "svg": svg, "type": "solar_return",
    })

    cached = _cached_response(cache_key, svg)
    if cached:
        return cached

    natal_subject = create_subject(name, year, month, day, hour, minute, city, nation, lng, lat, tz_str)

    return_factory = PlanetaryReturnFactory(natal_subject, lng=lng, lat=lat, tz_str=tz_str, online=False)
    solar_return_subject = return_factory.next_return_from_date(return_year, 1, 1, return_type="Solar")

    aspects_data = AspectsFactory.synastry_aspects(natal_subject, solar_return_subject)
    context_text = (
        f"--- Solar Return Context ({return_year}) ---\n\n"
        f"# Natal Chart\n{to_context(natal_subject)}\n\n"
        f"# Solar Return Chart\n{to_context(solar_return_subject)}"
    )

    response_data = {
        "natal": natal_subject.model_dump(),
        "solar_return": solar_return_subject.model_dump(),
        "aspects": [a.model_dump() for a in aspects_data.aspects],
        "context": context_text,
    }

    if not svg:
        return _json_response(response_data, cache_key)

    try:
        chart_data = ChartDataFactory.create_return_chart_data(natal_subject, solar_return_subject)
        return _svg_response(chart_data, "solar_return", cache_key)
    except Exception as e:
        logger.exception("Solar return calculation failed")
        raise HTTPException(status_code=500, detail=f"Solar return generation failed: {e}")


# ---------------------------------------------------------------------------
# /gen/lunar-return
# ---------------------------------------------------------------------------


@app.get("/gen/lunar-return", response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}}, tags=["Charts"])
async def get_lunar_return_chart(
    name: str = Query(..., description="Name of the subject", json_schema_extra={"example": "Ada Lovelace"}),
    year: int = Query(..., description="Year of birth", json_schema_extra={"example": 1815}),
    month: int = Query(..., description="Month of birth", json_schema_extra={"example": 12}),
    day: int = Query(..., description="Day of birth", json_schema_extra={"example": 10}),
    hour: int = Query(..., description="Hour of birth", json_schema_extra={"example": 6}),
    minute: int = Query(..., description="Minute of birth", json_schema_extra={"example": 0}),
    city: str = Query(..., description="City of birth", json_schema_extra={"example": "London"}),
    lng: float = Query(..., description="Longitude of birth location", json_schema_extra={"example": -0.1278}),
    lat: float = Query(..., description="Latitude of birth location", json_schema_extra={"example": 51.5074}),
    tz_str: str = Query(..., description="Timezone string of birth location", json_schema_extra={"example": "Europe/London"}),
    nation: str = Query(" ", description="Nation of birth", json_schema_extra={"example": "United Kingdom"}),
    return_year: int = Query(..., description="Target year for the return search", json_schema_extra={"example": 2024}),
    return_month: int = Query(..., description="Target month for the return search", json_schema_extra={"example": 1}),
    return_day: int = Query(..., description="Target day for the return search", json_schema_extra={"example": 1}),
    svg: bool = Query(False, description="Return SVG image if true, else return JSON"),
):
    cache_key = cache.make_key({
        "name": name, "year": year, "month": month, "day": day,
        "hour": hour, "minute": minute, "city": city, "lng": lng,
        "lat": lat, "tz_str": tz_str, "nation": nation,
        "return_year": return_year, "return_month": return_month,
        "return_day": return_day, "svg": svg, "type": "lunar_return",
    })

    cached = _cached_response(cache_key, svg)
    if cached:
        return cached

    natal_subject = create_subject(name, year, month, day, hour, minute, city, nation, lng, lat, tz_str)

    return_factory = PlanetaryReturnFactory(natal_subject, lng=lng, lat=lat, tz_str=tz_str, online=False)
    lunar_return_subject = return_factory.next_return_from_date(return_year, return_month, return_day, return_type="Lunar")

    aspects_data = AspectsFactory.synastry_aspects(natal_subject, lunar_return_subject)
    context_text = (
        f"--- Lunar Return Context (Search from {return_year}-{return_month}-{return_day}) ---\n\n"
        f"# Natal Chart\n{to_context(natal_subject)}\n\n"
        f"# Lunar Return Chart\n{to_context(lunar_return_subject)}"
    )

    response_data = {
        "natal": natal_subject.model_dump(),
        "lunar_return": lunar_return_subject.model_dump(),
        "aspects": [a.model_dump() for a in aspects_data.aspects],
        "context": context_text,
    }

    if not svg:
        return _json_response(response_data, cache_key)

    try:
        chart_data = ChartDataFactory.create_return_chart_data(natal_subject, lunar_return_subject)
        return _svg_response(chart_data, "lunar_return", cache_key)
    except Exception as e:
        logger.exception("Lunar return calculation failed")
        raise HTTPException(status_code=500, detail=f"Lunar return generation failed: {e}")


# ---------------------------------------------------------------------------
# /gen/composite
# ---------------------------------------------------------------------------


@app.get("/gen/composite", response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}}, tags=["Charts"])
async def get_composite_chart(
    name1: str = Query(..., description="Name of subject 1", json_schema_extra={"example": "Romeo"}),
    year1: int = Query(..., description="Year of birth 1", json_schema_extra={"example": 1990}),
    month1: int = Query(..., description="Month of birth 1", json_schema_extra={"example": 1}),
    day1: int = Query(..., description="Day of birth 1", json_schema_extra={"example": 1}),
    hour1: int = Query(..., description="Hour of birth 1", json_schema_extra={"example": 12}),
    minute1: int = Query(..., description="Minute of birth 1", json_schema_extra={"example": 0}),
    city1: str = Query(..., description="City of birth 1", json_schema_extra={"example": "Verona"}),
    lng1: float = Query(..., description="Longitude 1", json_schema_extra={"example": 10.99}),
    lat1: float = Query(..., description="Latitude 1", json_schema_extra={"example": 45.44}),
    tz_str1: str = Query(..., description="Timezone 1", json_schema_extra={"example": "Europe/Rome"}),
    nation1: str = Query(" ", description="Nation 1", json_schema_extra={"example": "Italy"}),
    name2: str = Query(..., description="Name of subject 2", json_schema_extra={"example": "Juliet"}),
    year2: int = Query(..., description="Year of birth 2", json_schema_extra={"example": 1990}),
    month2: int = Query(..., description="Month of birth 2", json_schema_extra={"example": 1}),
    day2: int = Query(..., description="Day of birth 2", json_schema_extra={"example": 1}),
    hour2: int = Query(..., description="Hour of birth 2", json_schema_extra={"example": 12}),
    minute2: int = Query(..., description="Minute of birth 2", json_schema_extra={"example": 0}),
    city2: str = Query(..., description="City of birth 2", json_schema_extra={"example": "Verona"}),
    lng2: float = Query(..., description="Longitude 2", json_schema_extra={"example": 10.99}),
    lat2: float = Query(..., description="Latitude 2", json_schema_extra={"example": 45.44}),
    tz_str2: str = Query(..., description="Timezone 2", json_schema_extra={"example": "Europe/Rome"}),
    nation2: str = Query(" ", description="Nation 2", json_schema_extra={"example": "Italy"}),
    svg: bool = Query(False, description="Return SVG image if true, else return JSON", json_schema_extra={"example": False}),
):
    cache_key = cache.make_key({
        "s1": {"n": name1, "y": year1, "m": month1, "d": day1, "h": hour1, "min": minute1, "c": city1, "ln": lng1, "la": lat1, "tz": tz_str1, "nat": nation1},
        "s2": {"n": name2, "y": year2, "m": month2, "d": day2, "h": hour2, "min": minute2, "c": city2, "ln": lng2, "la": lat2, "tz": tz_str2, "nat": nation2},
        "svg": svg, "type": "composite",
    })

    cached = _cached_response(cache_key, svg)
    if cached:
        return cached

    s1 = create_subject(name1, year1, month1, day1, hour1, minute1, city1, nation1, lng1, lat1, tz_str1)
    s2 = create_subject(name2, year2, month2, day2, hour2, minute2, city2, nation2, lng2, lat2, tz_str2)

    composite_factory = CompositeSubjectFactory(s1, s2)
    composite_subject = composite_factory.get_midpoint_composite_subject_model()

    chart_data = ChartDataFactory.create_composite_chart_data(composite_subject)
    context_text = to_context(composite_subject)

    if not svg:
        response_data = {
            "composite_subject": composite_subject.model_dump(),
            "aspects": [a.model_dump() for a in chart_data.aspects],
            "context": context_text,
        }
        return _json_response(response_data, cache_key)

    try:
        return _svg_response(chart_data, "composite", cache_key)
    except Exception as e:
        logger.exception("Composite calculation failed")
        raise HTTPException(status_code=500, detail=f"Composite generation failed: {e}")
