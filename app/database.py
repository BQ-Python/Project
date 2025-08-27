# app/database.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from dotenv import load_dotenv

# Charge .env en développement (sans effet si non présent en prod)
load_dotenv()

Base = declarative_base()

def _get_database_url() -> str:
    """
    Cherche une URL de DB parmi plusieurs noms d'env variables,
    normalise le schéma, ajoute le driver et assure sslmode=require.
    """
    candidates = [
        "SUPABASE_DB_URL",
        "DATABASE_URL",        # très courant sur Railway
        "POSTGRES_URL",
        "PGDATABASE_URL",
    ]
    raw = None
    for name in candidates:
        val = os.getenv(name)
        if val and val.strip():
            raw = val.strip()
            break

    if not raw:
        raise RuntimeError(
            "Aucune URL de base de données trouvée. "
            "Définissez SUPABASE_DB_URL (ou DATABASE_URL). "
            "Exemple: postgresql+psycopg://USER:PASSWORD@HOST:5432/DB?sslmode=require"
        )

    url = raw

    # 1) Normaliser postgres:// -> postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # 2) Ajouter explicitement le driver si absent (psycopg v3)
    if url.startswith("postgresql://") and "+psycopg" not in url and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    # 3) Forcer sslmode=require si absent (recommandé par Supabase)
    if "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"

    return url

DATABASE_URL = _get_database_url()

# ---- Engine & Session (sync) ----
# Quelques options utiles en prod (Railway/Supabase)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,     # teste les connexions avant usage (drop idle)
    pool_size=5,            # adapte selon charge
    max_overflow=10,        # pics temporaires
    pool_recycle=1800,      # recycle après 30 min
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

# ----- Modèles -----
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

def init_db():
    Base.metadata.create_all(bind=engine)
