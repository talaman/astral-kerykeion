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


@app.get("/v1/api/chart", response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}})
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
    tz_str: str = Query(..., description="Timezone string of birth location", example="Europe/London")
):
    import os
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
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
    return Response(content=r, media_type="application/json")
    # birth_chart_svg = KerykeionChartSVG(subject1, new_output_directory=output_dir, chart_language="ES")
    # svg_content = birth_chart_svg.makeSVG()
    # return Response(content=svg_content, media_type="image/svg+xml")