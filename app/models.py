from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class Satellite(Base):
    __tablename__ = "satellites"

    norad_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    object_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    group_name: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    elements: Mapped[list["OrbitalElement"]] = relationship(
        back_populates="satellite", cascade="all, delete-orphan"
    )


class OrbitalElement(Base):
    __tablename__ = "orbital_elements"
    __table_args__ = (
        UniqueConstraint("norad_id", "epoch", name="uq_orbital_elements_norad_epoch"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    norad_id: Mapped[int] = mapped_column(ForeignKey("satellites.norad_id"), index=True)
    epoch: Mapped[datetime] = mapped_column(DateTime, index=True)

    mean_motion: Mapped[float | None] = mapped_column(Float, nullable=True)
    eccentricity: Mapped[float | None] = mapped_column(Float, nullable=True)
    inclination: Mapped[float | None] = mapped_column(Float, nullable=True)
    ra_of_asc_node: Mapped[float | None] = mapped_column(Float, nullable=True)
    arg_of_pericenter: Mapped[float | None] = mapped_column(Float, nullable=True)
    mean_anomaly: Mapped[float | None] = mapped_column(Float, nullable=True)
    bstar: Mapped[float | None] = mapped_column(Float, nullable=True)

    raw_omm: Mapped[dict] = mapped_column(JSON)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    satellite: Mapped[Satellite] = relationship(back_populates="elements")
