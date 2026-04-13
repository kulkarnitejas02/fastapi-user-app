from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Vercel automatically provides POSTGRES_URL
# Note: SQLAlchemy requires 'postgresql://' instead of 'postgres://' 
DATABASE_URL = os.getenv("POSTGRES_URL")

if not DATABASE_URL:
    raise ValueError(
        "POSTGRES_URL not found. On Vercel, set it in project Settings → Environment Variables. "
        "Locally, add POSTGRES_URL to your .env file."
    )

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to PostgreSQL: {DATABASE_URL[:50]}...")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()