"""
Koneksi database & session factory (SQLAlchemy ORM).

Pakai SQLite untuk pengembangan lokal, tapi seluruh akses data lewat ORM --
tidak ada SQL mentah spesifik SQLite -- supaya pindah ke PostgreSQL nanti
cukup mengganti DATABASE_URL tanpa menulis ulang query.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import DATABASE_URL

# check_same_thread=False khusus SQLite: uvicorn melayani request di beberapa
# thread, sedangkan SQLite secara default mengunci koneksi ke thread pembuatnya.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency FastAPI: satu session per request, selalu ditutup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Buat tabel yang belum ada. Aman dipanggil berulang (no-op kalau sudah ada)."""
    import models  # noqa: F401  -- registrasi model ke Base.metadata

    Base.metadata.create_all(bind=engine)
