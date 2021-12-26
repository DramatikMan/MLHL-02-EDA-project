from typing import ClassVar

from sqlalchemy import Column, String, Integer, Date, ForeignKey, Time
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    __name__: ClassVar[str]

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class City(Base):
    name = Column(String(length=50), primary_key=True)
    airport = Column(String(length=3), primary_key=True)


class Flight(Base):
    destination = Column(
        String(length=50),
        ForeignKey(column='city.name'),
        primary_key=True
    )
    parsing_date = Column(Date, primary_key=True)
    departure_date = Column(Date, primary_key=True)
    days_until = Column(Integer, primary_key=True)
    airlines = Column(String(length=50), primary_key=True)
    departure_time = Column(Time, primary_key=True)
    arrival_time = Column(Time, primary_key=True)
    duration_m = Column(Integer, primary_key=True)
    departure_airport = Column(String(length=3), primary_key=True)
    arrival_airport = Column(
        String(length=3),
        ForeignKey(column='city.airport'),
        primary_key=True
    )
    min_price = Column(Integer, primary_key=True)
    stops_count = Column(Integer, primary_key=True)
