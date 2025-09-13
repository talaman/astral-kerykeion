from fastapi import FastAPI, Depends, HTTPException, status, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from kerykeion import AstrologicalSubject, KerykeionChartSVG
from fastapi import Query





app = FastAPI()

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


@app.get("/v1/api/gen", response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}})
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
        return Response(content=r, media_type="application/json")

    # Create a unique subfolder to capture the generated file(s)
    temp_dir = os.path.join(base_output_dir, uuid.uuid4().hex)
    os.makedirs(temp_dir, exist_ok=True)
    try:
        chart = KerykeionChartSVG(
            subject1,
            new_output_directory=temp_dir,
            chart_language="ES",
            theme="light"
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
