import json
from kerykeion import AstrologicalSubjectFactory, to_context

def test_context():
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
    print(f"Context Title: {context.splitlines()[0]}")
    print(f"Context Length: {len(context)} characters")
    
    if "Test User" in context:
        print("Verification SUCCESS: Context contains subject name.")
    else:
        print("Verification FAILED: Context does not contain subject name.")

if __name__ == "__main__":
    test_context()
