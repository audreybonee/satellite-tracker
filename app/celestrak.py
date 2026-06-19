from __future__ import annotations

from datetime import datetime
from typing import Any
import requests

CELESTRAK_GP_URL = "https://celestrak.org/NORAD/elements/gp.php"


def fetch_gp_json(group: str = "stations") -> list[dict[str, Any]]:
    """Fetch CelesTrak GP data in JSON format for a named group.

    Starter groups:
    - stations
    - starlink
    - weather
    - gps-ops
    - active
    """
    response = requests.get(
        CELESTRAK_GP_URL,
        params={"GROUP": group, "FORMAT": "json"},
        timeout=30,
        headers={"User-Agent": "satellite-tracker-python-starter/0.1"},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError(f"Expected a JSON list from CelesTrak, got {type(payload)}")
    return payload


def parse_epoch(value: str) -> datetime:
    # CelesTrak usually returns ISO timestamps such as 2026-01-01T12:34:56.789
    # Remove trailing Z if present because datetime.fromisoformat handles +00:00 better.
    value = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)
    return dt.replace(tzinfo=None)


def normalize_omm_record(record: dict[str, Any], group_name: str) -> dict[str, Any]:
    """Normalize the CelesTrak JSON shape into fields used by the DB."""
    norad_id = int(record.get("NORAD_CAT_ID") or record.get("OBJECT_NUMBER"))
    epoch = parse_epoch(record["EPOCH"])

    return {
        "norad_id": norad_id,
        "name": record.get("OBJECT_NAME") or record.get("OBJECT_NAME") or f"NORAD {norad_id}",
        "object_id": record.get("OBJECT_ID"),
        "country": record.get("COUNTRY_CODE"),
        "group_name": group_name,
        "epoch": epoch,
        "mean_motion": _float_or_none(record.get("MEAN_MOTION")),
        "eccentricity": _float_or_none(record.get("ECCENTRICITY")),
        "inclination": _float_or_none(record.get("INCLINATION")),
        "ra_of_asc_node": _float_or_none(record.get("RA_OF_ASC_NODE")),
        "arg_of_pericenter": _float_or_none(record.get("ARG_OF_PERICENTER")),
        "mean_anomaly": _float_or_none(record.get("MEAN_ANOMALY")),
        "bstar": _float_or_none(record.get("BSTAR")),
        "raw_omm": record,
    }


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)
