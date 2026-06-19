from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import Base, engine
from app import models  # noqa: F401 - ensures SQLAlchemy model registration


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables are ready.")


if __name__ == "__main__":
    main()
