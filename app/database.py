import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from dotenv import load_dotenv

load_dotenv()  # Charge les variables depuis un fichier .env si présent

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

if not SUPABASE_DB_URL:
    raise ValueError("La variable d'environnement SUPABASE_DB_URL n'est pas définie.")

# Initialiser le moteur SQLAlchemy
engine = create_engine(SUPABASE_DB_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base pour les modèles
Base = declarative_base()

# Définition des modèles
class Bank(Base):
    __tablename__ = "banks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    swaps = relationship("Swap", back_populates="bank")


class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String(3))
    amount = Column(Float)
    interest_rate = Column(Float)
    start_date = Column(Date)
    maturity_date = Column(Date)
    conversion_rate = Column(Float)
    payment_frequency = Column(String)


class Swap(Base):
    __tablename__ = "swaps"
    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date)
    maturity_date = Column(Date)
    currency = Column(String(3))
    spot_rate = Column(Float)
    forward_rate = Column(Float)
    nominal = Column(Float)

    bank_id = Column(Integer, ForeignKey("banks.id"))
    bank = relationship("Bank", back_populates="swaps")


# Fonction pour créer les tables dans Supabase
def init_db():
    Base.metadata.create_all(bind=engine)
