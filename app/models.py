from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String)
    nominal = Column(Float)
    rate = Column(Float)
    start_date = Column(Date)
    maturity_date = Column(Date)
    payment_frequency = Column(String)  # ✅ Nouveau champ ajouté

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

class Bank(Base):
    __tablename__ = "banks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
