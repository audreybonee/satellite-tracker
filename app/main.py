from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import get_settings
from app.crud import latest_elements_query
from app.db import get_db
from app.orbit import propagate_omm


settings = get_settings()
app = FastAPI(title="Satellite Tracker")
static_dir = settings.project_root / "app" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def index():
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/satellites")
def satellites(
    limit: int = Query(100, ge=1, le=10_000),
    db: Session = Depends(get_db),
):
    rows = db.execute(latest_elements_query().limit(limit)).all()
    return [
        {
            "norad_id": sat.norad_id,
            "name": sat.name,
            "object_id": sat.object_id,
            "country": sat.country,
            "group_name": sat.group_name,
            "epoch": elem.epoch.isoformat(),
        }
        for sat, elem in rows
    ]


@app.get("/api/positions")
def positions(
    limit: int = Query(1000, ge=1, le=10_000),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    rows = db.execute(latest_elements_query().limit(limit)).all()

    output = []
    for sat, elem in rows:
        pos = propagate_omm(elem.raw_omm, now)
        if pos is None:
            continue
        output.append(
            {
                "norad_id": sat.norad_id,
                "name": sat.name,
                "object_id": sat.object_id,
                "country": sat.country,
                "group_name": sat.group_name,
                "epoch": elem.epoch.isoformat(),
                "inclination": elem.inclination,
                "eccentricity": elem.eccentricity,
                "mean_motion": elem.mean_motion,
                "ra_of_asc_node": elem.ra_of_asc_node,
                "arg_of_pericenter": elem.arg_of_pericenter,
                **pos,
            }
        )
    return {"generated_at": now.isoformat(), "count": len(output), "satellites": output}

