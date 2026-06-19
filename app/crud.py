from __future__ import annotations

from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Satellite, OrbitalElement


def upsert_satellite_with_element(db: Session, normalized: dict) -> None:
    sat = db.get(Satellite, normalized["norad_id"])
    if sat is None:
        sat = Satellite(
            norad_id=normalized["norad_id"],
            name=normalized["name"],
            object_id=normalized.get("object_id"),
            country=normalized.get("country"),
            group_name=normalized.get("group_name"),
            updated_at=datetime.utcnow(),
        )
        db.add(sat)
    else:
        sat.name = normalized["name"]
        sat.object_id = normalized.get("object_id")
        sat.country = normalized.get("country")
        sat.group_name = normalized.get("group_name")
        sat.updated_at = datetime.utcnow()

    existing = db.execute(
        select(OrbitalElement).where(
            OrbitalElement.norad_id == normalized["norad_id"],
            OrbitalElement.epoch == normalized["epoch"],
        )
    ).scalar_one_or_none()

    if existing is None:
        db.add(
            OrbitalElement(
                norad_id=normalized["norad_id"],
                epoch=normalized["epoch"],
                mean_motion=normalized.get("mean_motion"),
                eccentricity=normalized.get("eccentricity"),
                inclination=normalized.get("inclination"),
                ra_of_asc_node=normalized.get("ra_of_asc_node"),
                arg_of_pericenter=normalized.get("arg_of_pericenter"),
                mean_anomaly=normalized.get("mean_anomaly"),
                bstar=normalized.get("bstar"),
                raw_omm=normalized["raw_omm"],
            )
        )


def latest_elements_query():
    latest_epoch = (
        select(
            OrbitalElement.norad_id,
            func.max(OrbitalElement.epoch).label("max_epoch"),
        )
        .group_by(OrbitalElement.norad_id)
        .subquery()
    )

    return (
        select(Satellite, OrbitalElement)
        .join(OrbitalElement, OrbitalElement.norad_id == Satellite.norad_id)
        .join(
            latest_epoch,
            (latest_epoch.c.norad_id == OrbitalElement.norad_id)
            & (latest_epoch.c.max_epoch == OrbitalElement.epoch),
        )
        .order_by(Satellite.norad_id)
    )
