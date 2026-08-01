from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# For MySQL, swap DATABASE_URL to e.g. "mysql+pymysql://user:pass@localhost:3306/complaints_db"
# and install PyMySQL instead of psycopg2-binary.
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
