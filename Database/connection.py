
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from Database.config import DATABASE_URL, IS_CLOUD

if IS_CLOUD:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=280,
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
