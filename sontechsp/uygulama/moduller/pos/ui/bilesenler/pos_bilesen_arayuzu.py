# Version: 0.1.0
# Last Update: 2024-12-18
# Module: pos_bilesen_arayuzu
# Description: POS bileşenleri için temel arayüz
# Changelog:
# - İlk oluşturma - Temel POS bileşen arayüzü
# - Metaclass çakışması düzeltildi

"""
POS Bileşen Arayüzü

Tüm POS UI bileşenlerinin uygulaması gereken temel arayüz.
Tutarlı davranış ve entegrasyon sağlar.

Sorumluluklar:
- Bileşen yaşam döngüsü yönetimi
- Klavye kısayolu desteği
- Veri güncelleme protokolü
- Temizleme ve yenileme işlemleri
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QWidget


class POSBilesenArayuzu(ABC):
    """
    POS Bileşen Temel Arayüzü

    Tüm POS bileşenlerinin uygulaması gereken temel metodlar.
    """

    @abstractmethod
    def baslat(self) -> None:
        """
        Bileşeni başlatır

        Bileşenin ilk kurulumu ve başlangıç durumu ayarları.
        """
        pass

    @abstractmethod
    def temizle(self) -> None:
        """
        Bileşeni temizler

        Bileşenin durumunu sıfırlar ve temizlik işlemlerini yapar.
        """
        pass

    @abstractmethod
    def guncelle(self, veri: Dict[str, Any]) -> None:
        """
        Bileşeni günceller

        Args:
            veri: Güncelleme verisi
        """
        pass

    @abstractmethod
    def klavye_kisayolu_isle(self, tus: str) -> bool:
        """
        Klavye kısayolunu işler

        Args:
            tus: Basılan tuş kombinasyonu

        Returns:
            bool: Kısayol işlendiyse True, aksi halde False
        """
        pass

    def aktif_mi(self) -> bool:
        """
        Bileşenin aktif olup olmadığını döndürür

        Returns:
            bool: Bileşen aktifse True
        """
        return True

    def hata_durumu_ayarla(self, hata_var: bool, mesaj: Optional[str] = None):
        """
        Bileşenin hata durumunu ayarlar

        Args:
            hata_var: Hata durumu var mı
            mesaj: Hata mesajı (opsiyonel)
        """
        pass

    def odak_al(self) -> None:
        """
        Bileşene odak verir

        Klavye girişi için bileşeni aktif hale getirir.
        """
        pass

    def veri_dogrula(self, veri: Dict[str, Any]) -> bool:
        """
        Veri doğrulaması yapar

        Args:
            veri: Doğrulanacak veri

        Returns:
            bool: Veri geçerliyse True
        """
        return True


class POSBilesenWidget(QWidget):
    """
    POS Bileşen Widget Temel Sınıfı

    QWidget tabanlı POS bileşenleri için temel sınıf.
    POSBilesenArayuzu metodlarını uygular.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._aktif = True
        self._hata_durumu = False
        self._hata_mesaji = None

    def baslat(self) -> None:
        """Bileşeni başlatır"""
        self._aktif = True
        self.setEnabled(True)

    def temizle(self) -> None:
        """Bileşeni temizler"""
        self._hata_durumu = False
        self._hata_mesaji = None
        self.setStyleSheet("")

    def guncelle(self, veri: Dict[str, Any]) -> None:
        """Bileşeni günceller"""
        # Alt sınıflar bu metodu override etmeli
        pass

    def klavye_kisayolu_isle(self, tus: str) -> bool:
        """Klavye kısayolunu işler"""
        # Alt sınıflar bu metodu override etmeli
        return False

    def aktif_mi(self) -> bool:
        """Bileşenin aktif durumunu döndürür"""
        return self._aktif and self.isEnabled()

    def aktif_durumu_ayarla(self, aktif: bool):
        """Bileşenin aktif durumunu ayarlar"""
        self._aktif = aktif
        self.setEnabled(aktif)

    def hata_durumu_ayarla(self, hata_var: bool, mesaj: Optional[str] = None):
        """Hata durumunu ayarlar"""
        self._hata_durumu = hata_var
        self._hata_mesaji = mesaj

        # Görsel hata durumu (kırmızı border)
        if hata_var:
            self.setStyleSheet(
                """
                QWidget {
                    border: 2px solid #e74c3c;
                    border-radius: 4px;
                }
            """
            )
        else:
            self.setStyleSheet("")

    def odak_al(self):
        """Bileşene odak verir"""
        self.setFocus()

    def hata_durumunda_mi(self) -> bool:
        """Hata durumunda olup olmadığını döndürür"""
        return self._hata_durumu

    def hata_mesajini_al(self) -> Optional[str]:
        """Hata mesajını döndürür"""
        return self._hata_mesaji

    def veri_dogrula(self, veri: Dict[str, Any]) -> bool:
        """Veri doğrulaması yapar"""
        return True
