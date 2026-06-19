-- Optional hand-written schema for Postgres/Tiger Cloud.
-- The Python app can also create tables automatically with `python scripts/init_db.py`.

CREATE TABLE IF NOT EXISTS satellites (
    norad_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    object_id TEXT,
    country TEXT,
    group_name TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orbital_elements (
    id BIGSERIAL PRIMARY KEY,
    norad_id INTEGER NOT NULL REFERENCES satellites(norad_id),
    epoch TIMESTAMP NOT NULL,
    mean_motion DOUBLE PRECISION,
    eccentricity DOUBLE PRECISION,
    inclination DOUBLE PRECISION,
    ra_of_asc_node DOUBLE PRECISION,
    arg_of_pericenter DOUBLE PRECISION,
    mean_anomaly DOUBLE PRECISION,
    bstar DOUBLE PRECISION,
    raw_omm JSONB NOT NULL,
    ingested_at TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (norad_id, epoch)
);

CREATE INDEX IF NOT EXISTS idx_orbital_elements_norad_epoch
    ON orbital_elements (norad_id, epoch DESC);

CREATE INDEX IF NOT EXISTS idx_satellites_group_name
    ON satellites (group_name);

-- V2 idea for Tiger/Timescale:
-- CREATE TABLE position_snapshots (
--     time TIMESTAMPTZ NOT NULL,
--     norad_id INTEGER NOT NULL REFERENCES satellites(norad_id),
--     x_km DOUBLE PRECISION NOT NULL,
--     y_km DOUBLE PRECISION NOT NULL,
--     z_km DOUBLE PRECISION NOT NULL,
--     altitude_km DOUBLE PRECISION NOT NULL
-- );
-- SELECT create_hypertable('position_snapshots', 'time', if_not_exists => TRUE);
