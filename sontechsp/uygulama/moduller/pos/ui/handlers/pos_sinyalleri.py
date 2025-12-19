# Version: 0.1.0
# Last Update: 2024-12-18
# Module: pos_sinyalleri
# Description: POS sinyal/slot sistemi
# Changelog:
# - İlk oluşturma - POS sinyal sistemi

"""
POS Sinyal/Slot Sistemi

POS bileşenleri arasında iletişim için sinyal sistemi.
Gevşek bağlı (loosely coupled) bileşen iletişimi sağlar.

Sorumluluklar:
- Bileşenler arası sinyal iletimi
- Olay koordinasyonu
- Veri akışı yönetimi
- Hata bildirimi
"""

from typing import Dict, List, Any
from PyQt6.QtCore import QObject, pyqtSignal
from decimal import Decimal


class POSSinyalleri(QObject):
    """
    POS Sinyal Sistemi

    Tüm POS bileşenleri arasında kullanılan sinyaller.
    """

    # Ürün ve sepet sinyalleri
    urun_eklendi = pyqtSignal(dict)  # Ürün sepete eklendi
    urun_cikarildi = pyqtSignal(int)  # Ürün sepetten çıkarıldı (satır index)
    sepet_guncellendi = pyqtSignal(list)  # Sepet değişti
    sepet_temizlendi = pyqtSignal()  # Sepet temizlendi
    sepet_satir_secildi = pyqtSignal(int)  # Sepet satırı seçildi

    # Barkod sinyalleri
    barkod_okundu = pyqtSignal(str)  # Barkod okundu/girildi
    barkod_hatasi = pyqtSignal(str)  # Geçersiz barkod

    # Ödeme sinyalleri
    odeme_baslatildi = pyqtSignal(str, object)  # Ödeme türü, tutar
    odeme_tamamlandi = pyqtSignal(dict)  # Ödeme bilgileri
    odeme_iptal_edildi = pyqtSignal()  # Ödeme iptal edildi

    # Hızlı ürün sinyalleri
    hizli_urun_secildi = pyqtSignal(dict)  # Hızlı ürün seçildi
    kategori_degisti = pyqtSignal(int)  # Kategori değişti
    hizli_urunler_guncellendi = pyqtSignal(list)  # Hızlı ürünler güncellendi
    kategoriler_guncellendi = pyqtSignal(list)  # Kategoriler güncellendi

    # İşlem sinyalleri
    sepet_bekletildi = pyqtSignal(str)  # Sepet bekletildi (sepet_id)
    bekletilen_sepet_acildi = pyqtSignal(str)  # Bekletilen sepet açıldı
    iade_baslatildi = pyqtSignal()  # İade işlemi başlatıldı
    islem_iptal_edildi = pyqtSignal()  # İşlem iptal edildi

    # Fiş ve belge sinyalleri
    fis_yazdirildi = pyqtSignal(dict)  # Fiş yazdırıldı
    fatura_olusturuldu = pyqtSignal(dict)  # Fatura oluşturuldu

    # Klavye kısayol sinyalleri
    klavye_kisayolu = pyqtSignal(str)  # Klavye kısayolu basıldı

    # Sistem sinyalleri
    hata_olustu = pyqtSignal(str)  # Hata mesajı
    bilgi_mesaji = pyqtSignal(str)  # Bilgi mesajı
    uyari_mesaji = pyqtSignal(str)  # Uyarı mesajı

    # Durum sinyalleri
    yukleme_basladi = pyqtSignal(str)  # Yükleme başladı (mesaj)
    yukleme_bitti = pyqtSignal()  # Yükleme bitti

    # Servis entegrasyon sinyalleri
    sepet_baslatildi = pyqtSignal(int)  # Yeni sepet başlatıldı (sepet_id)
    servis_hatasi = pyqtSignal(str, str)  # Servis hatası (servis_adi, hata_mesaji)
    servis_basarili = pyqtSignal(str, str)  # Servis başarılı (servis_adi, mesaj)

    # Offline kuyruk sinyalleri
    offline_islem_kuyruga_ekle = pyqtSignal(object, dict)  # İşlem türü, veri
    offline_islem_eklendi = pyqtSignal(str, dict)  # İşlem türü, veri
    offline_senkronizasyon_tamamlandi = pyqtSignal(int)  # İşlenen kayıt sayısı
    network_durumu_degisti = pyqtSignal(bool)  # Network durumu (True/False)

    # Eşleştirme tablosu sinyalleri
    buton_tiklandi = pyqtSignal(str, str, str)  # Ekran, buton, handler

    def __init__(self):
        super().__init__()
        self._bagli_bilesenler: Dict[str, List] = {}

    def bilesen_bagla(self, bilesen_adi: str, bilesen_ref):
        """
        Bileşeni sinyal sistemine bağlar

        Args:
            bilesen_adi: Bileşen adı
            bilesen_ref: Bileşen referansı
        """
        if bilesen_adi not in self._bagli_bilesenler:
            self._bagli_bilesenler[bilesen_adi] = []

        self._bagli_bilesenler[bilesen_adi].append(bilesen_ref)

    def bilesen_ayir(self, bilesen_adi: str, bilesen_ref=None):
        """
        Bileşeni sinyal sisteminden ayırır

        Args:
            bilesen_adi: Bileşen adı
            bilesen_ref: Bileşen referansı (None ise tümü)
        """
        if bilesen_adi in self._bagli_bilesenler:
            if bilesen_ref is None:
                del self._bagli_bilesenler[bilesen_adi]
            else:
                if bilesen_ref in self._bagli_bilesenler[bilesen_adi]:
                    self._bagli_bilesenler[bilesen_adi].remove(bilesen_ref)

    def sepet_ogesi_olustur(self, barkod: str, urun_adi: str, adet: int, birim_fiyat: Decimal) -> Dict[str, Any]:
        """
        Sepet öğesi veri yapısı oluşturur

        Args:
            barkod: Ürün barkodu
            urun_adi: Ürün adı
            adet: Adet
            birim_fiyat: Birim fiyat

        Returns:
            Dict: Sepet öğesi verisi
        """
        return {
            "barkod": barkod,
            "urun_adi": urun_adi,
            "adet": adet,
            "birim_fiyat": birim_fiyat,
            "toplam_fiyat": birim_fiyat * adet,
            "indirim_orani": 0.0,
        }

    def odeme_bilgisi_olustur(self, odeme_turu: str, tutar: Decimal, **kwargs) -> Dict[str, Any]:
        """
        Ödeme bilgisi veri yapısı oluşturur

        Args:
            odeme_turu: Ödeme türü
            tutar: Ödeme tutarı
            **kwargs: Ek ödeme bilgileri

        Returns:
            Dict: Ödeme bilgisi verisi
        """
        odeme_bilgisi = {
            "odeme_turu": odeme_turu,
            "tutar": tutar,
            "alinan_para": kwargs.get("alinan_para"),
            "para_ustu": kwargs.get("para_ustu"),
            "musteri_id": kwargs.get("musteri_id"),
            "nakit_tutar": kwargs.get("nakit_tutar"),
            "kart_tutar": kwargs.get("kart_tutar"),
        }

        return odeme_bilgisi

    def hizli_urun_bilgisi_olustur(
        self, pozisyon: int, urun_id: int, urun_adi: str, barkod: str, fiyat: Decimal, kategori_id: int
    ) -> Dict[str, Any]:
        """
        Hızlı ürün bilgisi veri yapısı oluşturur

        Args:
            pozisyon: Buton pozisyonu
            urun_id: Ürün ID
            urun_adi: Ürün adı
            barkod: Barkod
            fiyat: Fiyat
            kategori_id: Kategori ID

        Returns:
            Dict: Hızlı ürün bilgisi
        """
        return {
            "pozisyon": pozisyon,
            "urun_id": urun_id,
            "urun_adi": urun_adi,
            "barkod": barkod,
            "fiyat": fiyat,
            "kategori_id": kategori_id,
            "aktif": True,
        }
