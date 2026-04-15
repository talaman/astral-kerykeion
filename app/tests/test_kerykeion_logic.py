import pytest
from kerykeion import AstrologicalSubjectFactory, AspectsFactory, to_context

def test_birth_chart_context_generation():
    name = "Test User"
    year = 1990
    month = 1
    day = 1
    hour = 12
    minute = 0
    city = "London"
    nation = "United Kingdom"
    lng = -0.1278
    lat = 51.5074
    tz_str = "Europe/London"

    subject = AstrologicalSubjectFactory.from_birth_data(
        name, year, month, day, hour, minute,
        city, nation, lng=lng, lat=lat, tz_str=tz_str, online=False
    )
    
    context = to_context(subject)
    assert len(context) > 0
    assert "Test User" in context

def test_synastry_aspects_calculation():
    name1 = "Romeo"
    year1 = 1990
    month1 = 1
    day1 = 1
    hour1 = 12
    minute1 = 0
    city1 = "London"
    nation1 = "United Kingdom"
    lng1 = -0.1278
    lat1 = 51.5074
    tz_str1 = "Europe/London"

    name2 = "Juliet"
    year2 = 1995
    month2 = 2
    day2 = 14
    hour2 = 12
    minute2 = 0
    city2 = "Paris"
    nation2 = "France"
    lng2 = 2.3522
    lat2 = 48.8566
    tz_str2 = "Europe/Paris"

    subject1 = AstrologicalSubjectFactory.from_birth_data(
        name1, year1, month1, day1, hour1, minute1, city1, nation1,
        lng=lng1, lat=lat1, tz_str=tz_str1, online=False
    )
    
    subject2 = AstrologicalSubjectFactory.from_birth_data(
        name2, year2, month2, day2, hour2, minute2, city2, nation2,
        lng=lng2, lat=lat2, tz_str=tz_str2, online=False
    )

    aspects_data = AspectsFactory.synastry_aspects(subject1, subject2)
    assert len(aspects_data.aspects) > 0
    assert hasattr(aspects_data.aspects[0], "model_dump")

def test_transit_aspects_calculation():
    name = "Kanye"
    year = 1977
    month = 6
    day = 8
    hour = 8
    minute = 45
    city = "Atlanta"
    nation = "US"
    lng = -84.3879824
    lat = 33.7489954
    tz_str = "America/New_York"

    t_year = 2026
    t_month = 2
    t_day = 22
    t_hour = 14
    t_minute = 0
    t_city = "Atlanta"
    t_nation = "US"
    t_lng = -84.3879824
    t_lat = 33.7489954
    t_tz_str = "America/New_York"

    natal_subject = AstrologicalSubjectFactory.from_birth_data(
        name, year, month, day, hour, minute, city, nation,
        lng=lng, lat=lat, tz_str=tz_str, online=False
    )
    
    transit_subject = AstrologicalSubjectFactory.from_birth_data(
        "Transit", t_year, t_month, t_day, t_hour, t_minute, t_city, t_nation,
        lng=t_lng, lat=t_lat, tz_str=t_tz_str, online=False
    )

    aspects_data = AspectsFactory.synastry_aspects(natal_subject, transit_subject)
    assert hasattr(aspects_data, "aspects")
    assert len(aspects_data.aspects) > 0
    assert hasattr(aspects_data.aspects[0], "model_dump")
