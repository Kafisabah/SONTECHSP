# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.servis_fabrikasi
# Description: Servis dependency injection fabrikası
# Changelog:
# - İlk sürüm oluşturuldu

from typing import Any, Dict, Optional


class ServisFabrikasi:
    """Singleton pattern ile servis örneklerini yöneten fabrika sınıfı"""
    
    _instance: Optional['ServisFabrikasi'] = None
    _servisler: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._servisler = {}
    
    def stok_servisi(self):
        """Stok servisi örneğini döndür"""
        if 'stok' not in self._servisler:
            # Stub servis oluştur
            self._servisler['stok'] = StubStokServisi()
        return self._servisler['stok']
    
    def pos_servisi(self):
        """POS servisi örneğini döndür"""
        if 'pos' not in self._servisler:
            # Stub servis oluştur
            self._servisler['pos'] = StubPosServisi()
        return self._servisler['pos']
    
    def crm_servisi(self):
        """CRM servisi örneğini döndür"""
        if 'crm' not in self._servisler:
            # Stub servis oluştur
            self._servisler['crm'] = StubCrmServisi()
        return self._servisler['crm']
    
    def eticaret_servisi(self):
        """E-ticaret servisi örneğini döndür"""
        if 'eticaret' not in self._servisler:
            # Stub servis oluştur
            self._servisler['eticaret'] = StubEticaretServisi()
        return self._servisler['eticaret']
    
    def ebelge_servisi(self):
        """E-belge servisi örneğini döndür"""
        if 'ebelge' not in self._servisler:
            # Stub servis oluştur
            self._servisler['ebelge'] = StubEbelgeServisi()
        return self._servisler['ebelge']
    
    def kargo_servisi(self):
        """Kargo servisi örneğini döndür"""
        if 'kargo' not in self._servisler:
            # Stub servis oluştur
            self._servisler['kargo'] = StubKargoServisi()
        return self._servisler['kargo']
    
    def rapor_servisi(self):
        """Rapor servisi örneğini döndür"""
        if 'rapor' not in self._servisler:
            # Stub servis oluştur
            self._servisler['rapor'] = StubRaporServisi()
        return self._servisler['rapor']
    
    def ayar_servisi(self):
        """Ayar servisi örneğini döndür"""
        if 'ayar' not in self._servisler:
            # Stub servis oluştur
            self._servisler['ayar'] = StubAyarServisi()
        return self._servisler['ayar']


# Stub servis sınıfları (yer tutucu)
class StubStokServisi:
    def urun_ara(self, arama_terimi: str):
        print(f"Stok servisi: Ürün arama - {arama_terimi}")
        return []
    
    def urun_filtrele(self, kategori: str, stok_durumu: str):
        print(f"Stok servisi: Ürün filtreleme - {kategori}, {stok_durumu}")
        return []
    
    def urun_listesi_getir(self):
        print("Stok servisi: Ürün listesi getirme")
        return []


class StubPosServisi:
    def barkod_ekle(self, barkod: str):
        print(f"POS servisi: Barkod ekleme - {barkod}")
        return True
    
    def odeme_tamamla(self, odeme_turu: str, tutar: float):
        print(f"POS servisi: Ödeme tamamlama - {odeme_turu}: {tutar}")
        return True
    
    def satis_beklet(self):
        print("POS servisi: Satış bekletme")
        return True
    
    def satis_iptal(self):
        print("POS servisi: Satış iptal")
        return True


class StubCrmServisi:
    def musteri_ara(self, arama_terimi: str):
        print(f"CRM servisi: Müşteri arama - {arama_terimi}")
        return []
    
    def musteri_filtrele(self, musteri_tipi: str, sadakat_durumu: str, tarih_filtresi: str):
        print(f"CRM servisi: Müşteri filtreleme - {musteri_tipi}, {sadakat_durumu}, {tarih_filtresi}")
        return []
    
    def musteri_listesi_getir(self):
        print("CRM servisi: Müşteri listesi getirme")
        return []


class StubEticaretServisi:
    def siparis_cek(self, magaza_id: int):
        print(f"E-ticaret servisi: Sipariş çekme - Mağaza: {magaza_id}")
        return []
    
    def stok_gonder(self, magaza_id: int):
        print(f"E-ticaret servisi: Stok gönderme - Mağaza: {magaza_id}")
        return True
    
    def fiyat_gonder(self, magaza_id: int):
        print(f"E-ticaret servisi: Fiyat gönderme - Mağaza: {magaza_id}")
        return True


class StubEbelgeServisi:
    def gonder(self, belge_id: int):
        print(f"E-belge servisi: Belge gönderme - {belge_id}")
        return True
    
    def durum_sorgula(self, belge_id: int):
        print(f"E-belge servisi: Durum sorgulama - {belge_id}")
        return "Gönderildi"
    
    def tekrar_dene(self, belge_id: int):
        print(f"E-belge servisi: Tekrar deneme - {belge_id}")
        return True


class StubKargoServisi:
    def etiket_olustur(self, siparis_id: int):
        print(f"Kargo servisi: Etiket oluşturma - {siparis_id}")
        return True
    
    def durum_sorgula(self, takip_no: str):
        print(f"Kargo servisi: Durum sorgulama - {takip_no}")
        return "Yolda"


class StubRaporServisi:
    def satis_ozeti(self, baslangic_tarih, bitis_tarih):
        print(f"Rapor servisi: Satış özeti - {baslangic_tarih} / {bitis_tarih}")
        return []


class StubAyarServisi:
    def kaydet(self, ayarlar: dict):
        print(f"Ayar servisi: Ayar kaydetme - {ayarlar}")
        return True