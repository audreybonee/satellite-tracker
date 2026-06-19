from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.celestrak import fetch_gp_json, normalize_omm_record
from app.crud import upsert_satellite_with_element
from app.db import Base, SessionLocal, engine
from app import models  # noqa: F401 - ensures SQLAlchemy model registration


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest CelesTrak GP JSON satellite data.")
    parser.add_argument("--group", default="stations", help="CelesTrak group, e.g. stations, starlink, weather, active")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit for development runs")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)

    records = fetch_gp_json(args.group)
    if args.limit is not None:
        records = records[: args.limit]

    db = SessionLocal()
    try:
        for idx, record in enumerate(records, start=1):
            normalized = normalize_omm_record(record, args.group)
            upsert_satellite_with_element(db, normalized)
            if idx % 500 == 0:
                db.commit()
                print(f"Committed {idx} records...")
        db.commit()
    finally:
        db.close()

    print(f"Ingested {len(records)} records from CelesTrak group={args.group!r}.")


if __name__ == "__main__":
    main()
