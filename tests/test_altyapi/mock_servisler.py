# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_altyapi.mock_servisler
# Description: Mock servis implementasyonları
# Changelog:
# - İlk oluşturma

"""
Mock Servis İmplementasyonları

Bu modül test için gerekli mock servisleri içerir:
- DummySaglayici: E-belge sağlayıcı simülasyonu
- MockNetworkService: İnternet bağlantı simülasyonu
- MockStokService: Stok işlem simülasyonu

Görev 8: Test altyapısı ve mock servisleri oluştur
Requirements: Mock servis implementasyonları
"""

import random
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from unittest.mock import Mock

from sontechsp.uygulama.moduller.ebelge.saglayici_arayuzu import SaglayiciArayuzu
from sontechsp.uygulama.moduller.ebelge.dto import EBelgeGonderDTO, EBelgeSonucDTO
from sontechsp.uygulama.moduller.ebelge.hatalar import EBelgeHatasiBase
from sontechsp.uygulama.cekirdek.hatalar import NetworkHatasi, DogrulamaHatasi


class DummySaglayici(SaglayiciArayuzu):
    """
    Dummy E-belge Sağlayıcı

    Test için %50 hata oranı ile gerçekçi e-belge sağlayıcı simülasyonu yapar.
    Kontrollü hata senaryoları ile güvenilir test sağlar.
    """

    def __init__(self, hata_orani: float = 0.5, gecikme_ms: int = 100):
        """
        Args:
            hata_orani: Hata verme oranı (0.0-1.0 arası)
            gecikme_ms: Simüle edilecek gecikme süresi (ms)
        """
        self.hata_orani = hata_orani
        self.gecikme_ms = gecikme_ms
        self.gonderim_sayaci = 0
        self.basarili_gonderimler = []
        self.basarisiz_gonderimler = []

    def belge_gonder(self, belge_data: Dict[str, Any]) -> EBelgeSonucDTO:
        """E-belge gönderimi simülasyonu"""
        self.gonderim_sayaci += 1

        # Gecikme simülasyonu
        if self.gecikme_ms > 0:
            time.sleep(self.gecikme_ms / 1000.0)

        # Rastgele hata üretimi
        if random.random() < self.hata_orani:
            # Hata senaryosu
            hata_mesajlari = [
                "Network timeout",
                "Geçersiz belge formatı",
                "Sağlayıcı servisi kullanılamıyor",
                "Kimlik doğrulama hatası",
                "Günlük limit aşıldı",
            ]

            hata_mesaji = random.choice(hata_mesajlari)
            self.basarisiz_gonderimler.append(
                {
                    "belge_id": belge_data.get("belge_id"),
                    "hata": hata_mesaji,
                    "zaman": datetime.now(),
                }
            )

            raise EBelgeHatasiBase(f"DummySaglayici hatası: {hata_mesaji}")

        # Başarı senaryosu
        ettn = f"DUMMY-{self.gonderim_sayaci:06d}-{random.randint(1000, 9999)}"

        sonuc = EBelgeSonucDTO(
            basarili_mi=True,
            dis_belge_no=ettn,
            durum_kodu="GONDERILDI",
            mesaj="Belge başarıyla gönderildi",
            ham_cevap_json={"ettn": ettn, "durum": "GONDERILDI"},
        )

        self.basarili_gonderimler.append(
            {
                "belge_id": belge_data.get("belge_id"),
                "ettn": ettn,
                "zaman": datetime.now(),
            }
        )

        return sonuc

    def durum_sorgula(self, ettn: str) -> str:
        """E-belge durum sorgulama simülasyonu"""
        # Gecikme simülasyonu
        if self.gecikme_ms > 0:
            time.sleep(self.gecikme_ms / 1000.0)

        # Rastgele durum döndür
        durumlar = [
            "GONDERILDI",
            "TESLIM_EDILDI",
            "KABUL_EDILDI",
            "REDDEDILDI",
        ]

        return random.choice(durumlar)

    def istatistikler(self) -> Dict[str, Any]:
        """Mock sağlayıcı istatistikleri"""
        return {
            "toplam_gonderim": self.gonderim_sayaci,
            "basarili_gonderim": len(self.basarili_gonderimler),
            "basarisiz_gonderim": len(self.basarisiz_gonderimler),
            "basari_orani": len(self.basarili_gonderimler) / max(1, self.gonderim_sayaci),
            "hata_orani_ayari": self.hata_orani,
        }

    def sifirla(self):
        """Mock durumunu sıfırla"""
        self.gonderim_sayaci = 0
        self.basarili_gonderimler.clear()
        self.basarisiz_gonderimler.clear()


class MockNetworkService:
    """
    Mock Network Servisi

    İnternet bağlantı durumu kontrolü simülasyonu yapar.
    Test senaryolarında network durumunu kontrol etmek için kullanılır.
    """

    def __init__(self, baslangic_durumu: bool = True):
        """
        Args:
            baslangic_durumu: Başlangıç network durumu (True=online, False=offline)
        """
        self._online = baslangic_durumu
        self._baglanti_gecmisi = []
        self._kesinti_sayaci = 0

    @property
    def online(self) -> bool:
        """Network online durumu"""
        return self._online

    def network_durumu_kontrol(self) -> bool:
        """Network durumu kontrolü"""
        # Durum geçmişine kaydet
        self._baglanti_gecmisi.append(
            {
                "zaman": datetime.now(),
                "durum": self._online,
            }
        )

        return self._online

    def network_offline_yap(self):
        """Network'ü offline yap"""
        if self._online:
            self._kesinti_sayaci += 1
        self._online = False

    def network_online_yap(self):
        """Network'ü online yap"""
        self._online = True

    def network_durumu_degistir(self):
        """Network durumunu değiştir (toggle)"""
        if self._online:
            self.network_offline_yap()
        else:
            self.network_online_yap()

    def kesinti_simulasyonu(self, sure_saniye: float):
        """
        Belirli süre için network kesintisi simülasyonu

        Args:
            sure_saniye: Kesinti süresi (saniye)
        """
        self.network_offline_yap()
        time.sleep(sure_saniye)
        self.network_online_yap()

    def istatistikler(self) -> Dict[str, Any]:
        """Network istatistikleri"""
        return {
            "mevcut_durum": "online" if self._online else "offline",
            "toplam_kesinti": self._kesinti_sayaci,
            "durum_gecmisi_sayisi": len(self._baglanti_gecmisi),
            "son_kontrol": self._baglanti_gecmisi[-1] if self._baglanti_gecmisi else None,
        }

    def sifirla(self):
        """Mock durumunu sıfırla"""
        self._online = True
        self._baglanti_gecmisi.clear()
        self._kesinti_sayaci = 0


class MockStokService:
    """
    Mock Stok Servisi

    Stok işlemleri simülasyonu yapar.
    Eş zamanlı stok testleri için kullanılır.
    """

    def __init__(self):
        self._stok_bakiyeleri: Dict[int, int] = {}  # urun_id -> bakiye
        self._islem_gecmisi: List[Dict[str, Any]] = []
        self._lock_durumu: Dict[int, bool] = {}  # urun_id -> locked

    def stok_bakiye_getir(self, urun_id: int) -> int:
        """Stok bakiyesi getir"""
        return self._stok_bakiyeleri.get(urun_id, 0)

    def stok_bakiye_ayarla(self, urun_id: int, bakiye: int):
        """Stok bakiyesi ayarla"""
        self._stok_bakiyeleri[urun_id] = bakiye
        self._islem_gecmisi.append(
            {
                "tip": "bakiye_ayarla",
                "urun_id": urun_id,
                "yeni_bakiye": bakiye,
                "zaman": datetime.now(),
            }
        )

    def stok_dus(self, urun_id: int, miktar: int, lock_kontrol: bool = True) -> bool:
        """
        Stok düşüm işlemi

        Args:
            urun_id: Ürün ID
            miktar: Düşülecek miktar
            lock_kontrol: Lock kontrolü yapılsın mı

        Returns:
            İşlem başarılı mı
        """
        # Lock kontrolü
        if lock_kontrol and self._lock_durumu.get(urun_id, False):
            raise DogrulamaHatasi(f"Ürün {urun_id} kilitli durumda")

        mevcut_bakiye = self.stok_bakiye_getir(urun_id)

        if mevcut_bakiye < miktar:
            self._islem_gecmisi.append(
                {
                    "tip": "stok_dus_basarisiz",
                    "urun_id": urun_id,
                    "istenen_miktar": miktar,
                    "mevcut_bakiye": mevcut_bakiye,
                    "zaman": datetime.now(),
                }
            )
            return False

        # Stok düş
        yeni_bakiye = mevcut_bakiye - miktar
        self._stok_bakiyeleri[urun_id] = yeni_bakiye

        self._islem_gecmisi.append(
            {
                "tip": "stok_dus_basarili",
                "urun_id": urun_id,
                "dusurilen_miktar": miktar,
                "eski_bakiye": mevcut_bakiye,
                "yeni_bakiye": yeni_bakiye,
                "zaman": datetime.now(),
            }
        )

        return True

    def urun_kilitle(self, urun_id: int):
        """Ürünü kilitle (row-level lock simülasyonu)"""
        self._lock_durumu[urun_id] = True
        self._islem_gecmisi.append(
            {
                "tip": "urun_kilitle",
                "urun_id": urun_id,
                "zaman": datetime.now(),
            }
        )

    def urun_kilit_kaldir(self, urun_id: int):
        """Ürün kilidini kaldır"""
        self._lock_durumu[urun_id] = False
        self._islem_gecmisi.append(
            {
                "tip": "kilit_kaldir",
                "urun_id": urun_id,
                "zaman": datetime.now(),
            }
        )

    def istatistikler(self) -> Dict[str, Any]:
        """Stok servisi istatistikleri"""
        return {
            "toplam_urun": len(self._stok_bakiyeleri),
            "toplam_islem": len(self._islem_gecmisi),
            "kilitli_urun_sayisi": sum(1 for locked in self._lock_durumu.values() if locked),
            "toplam_stok": sum(self._stok_bakiyeleri.values()),
        }

    def sifirla(self):
        """Mock durumunu sıfırla"""
        self._stok_bakiyeleri.clear()
        self._islem_gecmisi.clear()
        self._lock_durumu.clear()


class MockPOSService:
    """
    Mock POS Servisi

    POS işlemleri simülasyonu yapar.
    Transaction testleri için kullanılır.
    """

    def __init__(self, mock_stok_service: MockStokService):
        self.stok_service = mock_stok_service
        self._satislar: List[Dict[str, Any]] = []
        self._transaction_aktif = False
        self._transaction_rollback_count = 0

    def transaction_baslat(self):
        """Transaction başlat"""
        if self._transaction_aktif:
            raise DogrulamaHatasi("Zaten aktif transaction var")
        self._transaction_aktif = True

    def transaction_commit(self):
        """Transaction commit"""
        if not self._transaction_aktif:
            raise DogrulamaHatasi("Aktif transaction yok")
        self._transaction_aktif = False

    def transaction_rollback(self):
        """Transaction rollback"""
        if not self._transaction_aktif:
            raise DogrulamaHatasi("Aktif transaction yok")
        self._transaction_aktif = False
        self._transaction_rollback_count += 1

    def satis_tamamla(self, satis_data: Dict[str, Any]) -> bool:
        """
        Satış tamamlama işlemi (atomik)

        Args:
            satis_data: Satış verisi (urunler listesi içermeli)

        Returns:
            İşlem başarılı mı
        """
        try:
            self.transaction_baslat()

            # Stok düşümleri
            for urun in satis_data.get("urunler", []):
                urun_id = urun["id"]
                miktar = urun["adet"]

                if not self.stok_service.stok_dus(urun_id, miktar):
                    raise DogrulamaHatasi(f"Ürün {urun_id} için yetersiz stok")

            # Satış kaydı oluştur
            satis_kaydi = {
                "id": len(self._satislar) + 1,
                "fis_no": satis_data.get("fis_no"),
                "toplam_tutar": satis_data.get("toplam_tutar"),
                "durum": "TAMAMLANDI",
                "zaman": datetime.now(),
                "urunler": satis_data.get("urunler", []),
            }

            self._satislar.append(satis_kaydi)
            self.transaction_commit()

            return True

        except Exception:
            self.transaction_rollback()
            raise

    def istatistikler(self) -> Dict[str, Any]:
        """POS servisi istatistikleri"""
        return {
            "toplam_satis": len(self._satislar),
            "transaction_aktif": self._transaction_aktif,
            "rollback_sayisi": self._transaction_rollback_count,
            "toplam_ciro": sum(satis.get("toplam_tutar", 0) for satis in self._satislar),
        }

    def sifirla(self):
        """Mock durumunu sıfırla"""
        self._satislar.clear()
        self._transaction_aktif = False
        self._transaction_rollback_count = 0


# Mock servis fabrikası
class MockServisFabrikasi:
    """Mock servis fabrikası - Test için gerekli mock servisleri sağlar"""

    @staticmethod
    def dummy_saglayici_olustur(hata_orani: float = 0.5) -> DummySaglayici:
        """DummySaglayici oluştur"""
        return DummySaglayici(hata_orani=hata_orani)

    @staticmethod
    def mock_network_olustur(online: bool = True) -> MockNetworkService:
        """MockNetworkService oluştur"""
        return MockNetworkService(baslangic_durumu=online)

    @staticmethod
    def mock_stok_olustur() -> MockStokService:
        """MockStokService oluştur"""
        return MockStokService()

    @staticmethod
    def mock_pos_olustur(stok_service: MockStokService) -> MockPOSService:
        """MockPOSService oluştur"""
        return MockPOSService(stok_service)

    @staticmethod
    def tam_mock_ortam_olustur() -> Dict[str, Any]:
        """Tam mock ortamı oluştur"""
        stok_service = MockServisFabrikasi.mock_stok_olustur()

        return {
            "dummy_saglayici": MockServisFabrikasi.dummy_saglayici_olustur(),
            "network_service": MockServisFabrikasi.mock_network_olustur(),
            "stok_service": stok_service,
            "pos_service": MockServisFabrikasi.mock_pos_olustur(stok_service),
        }
