from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()


# Vercel automatically provides POSTGRES_URL
# # Note: SQLAlchemy requires 'postgresql://' instead of 'postgres://' 
DATABASE_URL = os.getenv("POSTGRES_URL")

# Don't validate at import time - let it fail gracefully when queries are made
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DATABASE_URL = "sqlite:///./users.db"

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
else:
    # Dummy objects for startup - will fail when actually used
    engine = None
    SessionLocal = None

Base = declarative_base()