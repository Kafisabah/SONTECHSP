# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.ebelge
# Description: SONTECHSP e-belge modelleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP E-belge Modelleri

Tablolar:
- ebelge_cikis_kuyrugu: E-belge çıkış kuyruğu
- ebelge_durumlari: E-belge durum bilgileri
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..taban import Taban


class EbelgeCikisKuyruk(Taban):
    """E-belge çıkış kuyruğu tablosu"""
    
    __tablename__ = "ebelge_cikis_kuyrugu"
    
    belge_tipi: Mapped[str] = mapped_column(String(20), nullable=False)
    belge_no: Mapped[str] = mapped_column(String(50), nullable=False)
    durum: Mapped[str] = mapped_column(String(20), nullable=False)
    xml_icerik: Mapped[str] = mapped_column(Text, nullable=False)


class EbelgeDurum(Taban):
    """E-belge durum bilgileri tablosu"""
    
    __tablename__ = "ebelge_durumlari"
    
    belge_no: Mapped[str] = mapped_column(String(50), nullable=False)
    durum_kodu: Mapped[str] = mapped_column(String(10), nullable=False)
    durum_aciklama: Mapped[str] = mapped_column(String(200), nullable=False)