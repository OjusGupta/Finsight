from sqlalchemy.orm import sessionmaker, Session

from backend.app.database.connection import engine


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db():
    db: Session = SessionLocal()


    try:
        yield db
    finally:
        db.close()