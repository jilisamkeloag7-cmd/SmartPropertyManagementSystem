from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from Database.config import DATABASE_URL

# SQLite needs check_same_thread=False for multi-threaded Qt use
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Session = scoped_session(SessionFactory)

def get_session():
    """Return a scoped session — call .remove() when done in a thread."""
    return Session()