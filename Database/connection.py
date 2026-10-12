print(">>> connection.py V2 <<<")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from Database.config import DATABASE_URL, IS_CLOUD

if IS_CLOUD:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,     # reconnect if connection dropped
        pool_recycle=300,       # recycle every 5 min
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )

SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Session = scoped_session(SessionFactory)


def get_session():
    return Session()