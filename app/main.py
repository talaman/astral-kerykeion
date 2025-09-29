from fastapi import FastAPI, Depends, HTTPException, status, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from kerykeion import AstrologicalSubject, KerykeionChartSVG
from fastapi import Query
import hashlib
import json
import time
import sys
import logging





app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced in-memory cache with size management
CACHE_MAX_ITEMS = 700  # Maximum number of cached items
CACHE_MAX_SIZE_MB = 100  # Maximum cache size in MB

cache = {}  # Main cache storage: {key: {"content": str, "media_type": str, "last_used": float, "size": int}}
cache_access_order = []  # Track access order for LRU


def get_cache_size_mb():
    """Calculate total cache size in MB"""
    total_size = sum(item["size"] for item in cache.values())
    return total_size / (1024 * 1024)


def evict_lru_items():
    """Remove least recently used items to free up space"""
    global cache_access_order
    
    items_evicted = 0
    # Remove items until we're under limits
    while (len(cache) > CACHE_MAX_ITEMS or get_cache_size_mb() > CACHE_MAX_SIZE_MB) and cache:
        # Find least recently used item
        if cache_access_order:
            lru_key = cache_access_order[0]
            # Remove from cache and access order
            if lru_key in cache:
                del cache[lru_key]
                items_evicted += 1
            cache_access_order.remove(lru_key)
        else:
            # Fallback: remove any item if access order is empty
            key_to_remove = next(iter(cache))
            del cache[key_to_remove]
            items_evicted += 1
    
    if items_evicted > 0:
        logger.info(f"Cache eviction: removed {items_evicted} items. Current: {len(cache)} items, {get_cache_size_mb():.2f}MB")


def update_cache_access(cache_key):
    """Update access order for LRU tracking"""
    global cache_access_order
    
    # Remove key from current position and add to end (most recent)
    if cache_key in cache_access_order:
        cache_access_order.remove(cache_key)
    cache_access_order.append(cache_key)
    
    # Update last_used timestamp
    if cache_key in cache:
        cache[cache_key]["last_used"] = time.time()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/cache/info")
async def cache_info():
    """Get information about the current cache state"""
    return {
        "cache_items": len(cache),
        "cache_size_mb": round(get_cache_size_mb(), 2),
        "max_items": CACHE_MAX_ITEMS,
        "max_size_mb": CACHE_MAX_SIZE_MB,
        "cached_keys": list(cache.keys()),
        "access_order": cache_access_order
    }


@app.delete("/cache/clear")
async def clear_cache():
    """Clear all cached responses"""
    global cache_access_order
    cache.clear()
    cache_access_order.clear()
    return {"message": "Cache cleared successfully"}


@app.put("/cache/config")
async def update_cache_config(max_items: int = None, max_size_mb: float = None):
    """Update cache configuration limits"""
    global CACHE_MAX_ITEMS, CACHE_MAX_SIZE_MB
    
    if max_items is not None and max_items > 0:
        CACHE_MAX_ITEMS = max_items
    
    if max_size_mb is not None and max_size_mb > 0:
        CACHE_MAX_SIZE_MB = max_size_mb
    
    # Trigger eviction if new limits are exceeded
    evict_lru_items()
    
    return {
        "message": "Cache configuration updated",
        "max_items": CACHE_MAX_ITEMS,
        "max_size_mb": CACHE_MAX_SIZE_MB,
        "current_items": len(cache),
        "current_size_mb": round(get_cache_size_mb(), 2)
    }


@app.get("/gen", response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}})
async def get_chart(
    name: str = Query(..., description="Name of the subject", example="Ada Lovelace"),
    year: int = Query(..., description="Year of birth", example=1815),
    month: int = Query(..., description="Month of birth", example=12),
    day: int = Query(..., description="Day of birth", example=10),
    hour: int = Query(..., description="Hour of birth", example=6),
    minute: int = Query(..., description="Minute of birth", example=0),
    city: str = Query(..., description="City of birth", example="London"),
    lng: float = Query(..., description="Longitude of birth location", example=-0.1278),
    lat: float = Query(..., description="Latitude of birth location", example=51.5074),
    tz_str: str = Query(..., description="Timezone string of birth location", example="Europe/London"),
    svg: bool = Query(False, description="Return SVG image if true, else return JSON")

):
    import os
    import uuid
    import shutil
    from glob import glob
    
    # Create cache key from parameters
    cache_data = {
        "name": name,
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "city": city,
        "lng": lng,
        "lat": lat,
        "tz_str": tz_str,
        "svg": svg
    }
    cache_key = hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    # Check cache first
    if cache_key in cache:
        cached_response = cache[cache_key]
        # Update access order for LRU
        update_cache_access(cache_key)
        
        content_type = "SVG" if svg else "JSON"
        logger.info(f"Cache HIT: {content_type} for {name} ({cache_key[:8]}...) - Cache: {len(cache)} items, {get_cache_size_mb():.2f}MB")
        
        if svg:
            return Response(content=cached_response["content"], media_type="image/svg+xml")
        else:
            return Response(content=cached_response["content"], media_type="application/json")

    base_output_dir = "./temp/output"
    os.makedirs(base_output_dir, exist_ok=True)
    subject1 = AstrologicalSubject(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city,
        lng=lng,
        lat=lat,
        tz_str=tz_str,
        online=False  
    )
    r = subject1.json(dump=False, indent=2)

    if not svg:
        logger.info(f"Cache MISS: JSON for {name} ({cache_key[:8]}...) - Generating new response")
        
        # Cache JSON response with size tracking
        content_size = sys.getsizeof(r)
        cache[cache_key] = {
            "content": r, 
            "media_type": "application/json",
            "last_used": time.time(),
            "size": content_size
        }
        update_cache_access(cache_key)
        evict_lru_items()  # Check if eviction is needed
        
        logger.info(f"Cache STORE: JSON for {name} ({content_size} bytes) - Cache: {len(cache)} items, {get_cache_size_mb():.2f}MB")
        return Response(content=r, media_type="application/json")

    # Create a unique subfolder to capture the generated file(s)
    temp_dir = os.path.join(base_output_dir, uuid.uuid4().hex)
    os.makedirs(temp_dir, exist_ok=True)
    try:
        chart = KerykeionChartSVG(
            subject1,
            new_output_directory=temp_dir,
            chart_language="ES",
            theme=None
        )
        # This writes the SVG to temp_dir and returns None
        chart.makeSVG()

        # Find the generated SVG (pick the newest if multiple exist)
        svgs = sorted(
            glob(os.path.join(temp_dir, "*.svg")),
            key=lambda p: os.path.getmtime(p),
            reverse=True,
        )
        if not svgs:
            raise HTTPException(status_code=500, detail="SVG generation failed: no file created")

        svg_path = svgs[0]
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_text = f.read()

        # Read and embed CSS styles
        css_path = "./themes/astral.css"
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            
            # Embed CSS into SVG
            if "<svg" in svg_text and "<style>" not in svg_text:
                # Find the first occurrence of > after <svg to insert the style tag
                svg_start = svg_text.find("<svg")
                if svg_start != -1:
                    svg_tag_end = svg_text.find(">", svg_start)
                    if svg_tag_end != -1:
                        # Insert CSS style tag right after the opening <svg> tag
                        style_tag = f'\n<style type="text/css">\n<![CDATA[\n{css_content}\n]]>\n</style>\n'
                        svg_text = svg_text[:svg_tag_end + 1] + style_tag + svg_text[svg_tag_end + 1:]
        except FileNotFoundError:
            # If CSS file not found, proceed without styling
            pass

        logger.info(f"Cache MISS: SVG for {name} ({cache_key[:8]}...) - Generating new chart")
        
        # Cache SVG response with size tracking
        content_size = sys.getsizeof(svg_text)
        cache[cache_key] = {
            "content": svg_text, 
            "media_type": "image/svg+xml",
            "last_used": time.time(),
            "size": content_size
        }
        update_cache_access(cache_key)
        evict_lru_items()  # Check if eviction is needed
        
        logger.info(f"Cache STORE: SVG for {name} ({content_size} bytes) - Cache: {len(cache)} items, {get_cache_size_mb():.2f}MB")
        return Response(content=svg_text, media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVG generation failed: {str(e)}")
    finally:
        # Always clean up the temp directory
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            # Best-effort cleanup; ignore failures
            pass
