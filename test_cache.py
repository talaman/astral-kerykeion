#!/usr/bin/env python3
"""
Test script to demonstrate cache functionality
"""
import requests
import time
import json

BASE_URL = "http://localhost:8002"

def test_cache():
    print("🧪 Testing Cache Functionality")
    print("=" * 50)
    
    # Test parameters
    params = {
        "name": "Test Subject",
        "year": 1990,
        "month": 5,
        "day": 15,
        "hour": 12,
        "minute": 30,
        "city": "London",
        "lng": -0.1278,
        "lat": 51.5074,
        "tz_str": "Europe/London",
        "svg": False
    }
    
    print("1️⃣ First request (should be MISS):")
    start_time = time.time()
    response1 = requests.get(f"{BASE_URL}/gen", params=params)
    time1 = time.time() - start_time
    print(f"   ⏱️  Response time: {time1:.3f}s")
    print(f"   📊 Status: {response1.status_code}")
    
    print("\n2️⃣ Second request (should be HIT):")
    start_time = time.time()
    response2 = requests.get(f"{BASE_URL}/gen", params=params)
    time2 = time.time() - start_time
    print(f"   ⏱️  Response time: {time2:.3f}s")
    print(f"   📊 Status: {response2.status_code}")
    
    # Test SVG caching
    print("\n3️⃣ First SVG request (should be MISS):")
    params["svg"] = True
    start_time = time.time()
    response3 = requests.get(f"{BASE_URL}/gen", params=params)
    time3 = time.time() - start_time
    print(f"   ⏱️  Response time: {time3:.3f}s")
    print(f"   📊 Status: {response3.status_code}")
    
    print("\n4️⃣ Second SVG request (should be HIT):")
    start_time = time.time()
    response4 = requests.get(f"{BASE_URL}/gen", params=params)
    time4 = time.time() - start_time
    print(f"   ⏱️  Response time: {time4:.3f}s")
    print(f"   📊 Status: {response4.status_code}")
    
    # Check cache info
    print("\n📈 Cache Information:")
    cache_info = requests.get(f"{BASE_URL}/cache/info")
    if cache_info.status_code == 200:
        info = cache_info.json()
        print(f"   📦 Items: {info['cache_items']}")
        print(f"   💾 Size: {info['cache_size_mb']} MB")
        print(f"   🎯 Hit ratio improvement: {((time1 - time2) / time1 * 100):.1f}% faster")
    
    print(f"\n✅ Test completed!")
    print(f"   First JSON: {time1:.3f}s")
    print(f"   Cached JSON: {time2:.3f}s ({((time1 - time2) / time1 * 100):+.1f}%)")
    print(f"   First SVG: {time3:.3f}s") 
    print(f"   Cached SVG: {time4:.3f}s ({((time3 - time4) / time3 * 100):+.1f}%)")

if __name__ == "__main__":
    try:
        test_cache()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on http://localhost:8000")
        print("💡 Start with: uvicorn main:app --host 0.0.0.0 --port 8000")