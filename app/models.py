from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Swap(Base):
    __tablename__ = "swaps"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String)
    nominal = Column(Float)
    start_date = Column(Date)
    maturity_date = Column(Date)
    spot_rate = Column(Float)
    forward_rate = Column(Float)
    bank_id = Column(Integer, ForeignKey("banks.id"))
    bank = relationship("Bank")

    # Champs calculés
    spot_value_eur = Column(Float)
    forward_value_eur = Column(Float)
    swap_points_eur = Column(Float)
    mtm_eur = Column(Float)
    total_days = Column(Integer)
    remaining_days = Column(Integer)

class Bank(Base):
    __tablename__ = "banks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
