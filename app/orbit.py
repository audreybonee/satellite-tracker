from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite
from typing import Any

from sgp4.api import Satrec, jday
from sgp4.omm import initialize

EARTH_RADIUS_KM = 6371.0


def propagate_omm(raw_omm: dict[str, Any], when: datetime | None = None) -> dict[str, float] | None:
    """Propagate one OMM record and return an Earth-centered position in kilometers.

    The SGP4 library returns a TEME-like Earth-centered inertial vector. For a first
    visualization pass, plotting that vector around a globe is enough. For precise
    ground tracks, add a TEME -> ITRF/geodetic conversion with astropy later.
    """
    when = when or datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    satrec = Satrec()

    # sgp4.omm.initialize expects OMM-like field names. CelesTrak JSON uses compatible names.
    fields = {k: str(v) for k, v in raw_omm.items() if v is not None}
    initialize(satrec, fields)

    jd, fr = jday(
        when.year,
        when.month,
        when.day,
        when.hour,
        when.minute,
        when.second + when.microsecond / 1_000_000,
    )
    error_code, position_km, velocity_km_s = satrec.sgp4(jd, fr)
    if error_code != 0:
        return None

    x, y, z = position_km
    vx, vy, vz = velocity_km_s
    values = [x, y, z, vx, vy, vz]
    if not all(isfinite(v) for v in values):
        return None

    radius = (x * x + y * y + z * z) ** 0.5
    altitude = radius - EARTH_RADIUS_KM

    return {
        "x_km": x,
        "y_km": y,
        "z_km": z,
        "vx_km_s": vx,
        "vy_km_s": vy,
        "vz_km_s": vz,
        "altitude_km": altitude,
    }
