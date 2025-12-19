# Version: 0.1.0
# Last Update: 2024-12-19
# Module: sepet_modeli
# Description: POS sepet tablosu için QAbstractTableModel
# Changelog:
# - İlk oluşturma

"""
Sepet Modeli - POS sepet tablosu için model sınıfı
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Any
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex, pyqtSignal
from PyQt6.QtGui import QColor
from .turkuaz_tema import TurkuazTema


@dataclass
class SepetOgesi:
    """Sepet öğesi veri sınıfı"""

    barkod: str
    urun_adi: str
    adet: int
    birim_fiyat: Decimal
    toplam_fiyat: Decimal
    indirim_orani: float = 0.0

    def toplam_hesapla(self) -> Decimal:
        """Toplam fiyatı hesaplar"""
        return self.birim_fiyat * self.adet * (Decimal("1") - Decimal(str(self.indirim_orani)))


class SepetModeli(QAbstractTableModel):
    """Sepet tablosu için model sınıfı"""

    sepet_degisti = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.kolonlar = ["Barkod", "Ürün", "Adet", "Fiyat", "Tutar", "Sil"]
        self.sepet_ogeleri: List[SepetOgesi] = []
        self.tema = TurkuazTema()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Satır sayısını döndürür"""
        return len(self.sepet_ogeleri)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Kolon sayısını döndürür"""
        return len(self.kolonlar)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Hücre verilerini döndürür"""
        if not index.isValid() or index.row() >= len(self.sepet_ogeleri):
            return None

        oge = self.sepet_ogeleri[index.row()]
        kolon = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if kolon == 0:  # Barkod
                return oge.barkod
            elif kolon == 1:  # Ürün
                return oge.urun_adi
            elif kolon == 2:  # Adet
                return str(oge.adet)
            elif kolon == 3:  # Fiyat
                return f"{oge.birim_fiyat:.2f} ₺"
            elif kolon == 4:  # Tutar
                return f"{oge.toplam_hesapla():.2f} ₺"
            elif kolon == 5:  # Sil
                return "Sil"

        elif role == Qt.ItemDataRole.BackgroundRole:
            # Seçili satır vurgulama - tema renklerini kullan
            if index.row() % 2 == 0:
                return QColor(self.tema.acik_gri)  # Açık gri
            else:
                return QColor("white")

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if kolon in [2, 3, 4]:  # Adet, Fiyat, Tutar
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Başlık verilerini döndürür"""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.kolonlar[section]
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Hücre özelliklerini döndürür"""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        # Adet kolonu düzenlenebilir
        if index.column() == 2:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        """Hücre verisini günceller"""
        if not index.isValid() or index.row() >= len(self.sepet_ogeleri):
            return False

        if role == Qt.ItemDataRole.EditRole and index.column() == 2:  # Adet
            try:
                yeni_adet = int(value)
                if yeni_adet > 0:
                    self.sepet_ogeleri[index.row()].adet = yeni_adet
                    self.sepet_ogeleri[index.row()].toplam_fiyat = self.sepet_ogeleri[index.row()].toplam_hesapla()
                    self.dataChanged.emit(index, index)
                    self.sepet_degisti.emit()
                    return True
            except ValueError:
                pass

        return False

    def oge_ekle(self, oge: SepetOgesi):
        """Sepete öğe ekler"""
        self.beginInsertRows(QModelIndex(), len(self.sepet_ogeleri), len(self.sepet_ogeleri))
        self.sepet_ogeleri.append(oge)
        self.endInsertRows()
        self.sepet_degisti.emit()

    def oge_sil(self, satir: int):
        """Sepetten öğe siler"""
        if 0 <= satir < len(self.sepet_ogeleri):
            self.beginRemoveRows(QModelIndex(), satir, satir)
            del self.sepet_ogeleri[satir]
            self.endRemoveRows()
            self.sepet_degisti.emit()

    def sepeti_temizle(self):
        """Sepeti temizler"""
        self.beginResetModel()
        self.sepet_ogeleri.clear()
        self.endResetModel()
        self.sepet_degisti.emit()

    def adet_degistir(self, satir: int, degisim: int):
        """Belirtilen satırdaki ürünün adetini değiştirir"""
        if 0 <= satir < len(self.sepet_ogeleri):
            oge = self.sepet_ogeleri[satir]
            yeni_adet = oge.adet + degisim

            if yeni_adet > 0:
                oge.adet = yeni_adet
                oge.toplam_fiyat = oge.toplam_hesapla()

                # Değişikliği bildir
                index = self.createIndex(satir, 2)  # Adet kolonu
                self.dataChanged.emit(index, index)
                self.sepet_degisti.emit()
            elif yeni_adet <= 0:
                # Adet 0 veya negatif olursa ürünü sil
                self.oge_sil(satir)

    def genel_toplam(self) -> Decimal:
        """Sepet genel toplamını hesaplar"""
        return sum(oge.toplam_hesapla() for oge in self.sepet_ogeleri)
