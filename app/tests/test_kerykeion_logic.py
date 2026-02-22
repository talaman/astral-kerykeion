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
