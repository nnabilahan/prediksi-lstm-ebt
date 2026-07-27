"""Model ORM tabel database SIPREBAR."""
from datetime import date

from sqlalchemy import Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from config import SUMBER_REKONSTRUKSI
from database import Base


class DataHistoris(Base):
    """Satu baris observasi bulanan produksi EBT untuk satu jenis PLT.

    Kolom `sumber` sengaja ada di level database, bukan cuma di komentar kode:
    dataset awal adalah hasil REKONSTRUKSI/ESTIMASI (lihat audit/source/README.md),
    bukan observasi terverifikasi Dinas ESDM. Membedakannya dari data yang
    benar-benar diinput pengguna membuat status tiap baris tetap eksplisit dan
    bisa ditelusuri lewat query, bukan hilang begitu data bercampur.
    """

    __tablename__ = "data_historis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tanggal: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    jenis_plt: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    produksi: Mapped[float] = mapped_column(Float, nullable=False)
    kapasitas: Mapped[float] = mapped_column(Float, nullable=False)
    cuaca: Mapped[float] = mapped_column(Float, nullable=False)
    sumber: Mapped[str] = mapped_column(
        String(32), nullable=False, default=SUMBER_REKONSTRUKSI
    )

    def __repr__(self) -> str:
        return (
            f"<DataHistoris id={self.id} {self.tanggal} {self.jenis_plt} "
            f"produksi={self.produksi} sumber={self.sumber}>"
        )
