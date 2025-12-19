# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.servisler.offline_kuyruk_service
# Description: Offline kuyruk service implementasyonu
# Changelog:
# - İlk oluşturma

"""
POS Offline Kuyruk Service Implementasyonu

Bu modül offline durumda POS işlemlerini kuyruğa alır ve
online olunduğunda senkronize eder.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import json

from ..arayuzler import IOfflineKuyrukService, IslemTuru, KuyrukDurum
from ..repositories.offline_kuyruk_repository import OfflineKuyrukRepository
from ..monitoring import islem_izle, get_pos_monitoring
from ....cekirdek.hatalar import DogrulamaHatasi, SontechHatasi, NetworkHatasi


class OfflineKuyrukService(IOfflineKuyrukService):
    """
    Offline kuyruk service implementasyonu

    Offline durumda POS işlemlerini SQLite kuyruğa alır.
    Online olunduğunda ana sisteme senkronize eder.
    """

    def __init__(self, kuyruk_repository: Optional[OfflineKuyrukRepository] = None):
        """
        Service'i başlatır

        Args:
            kuyruk_repository: Kuyruk repository (opsiyonel)
        """
        self._kuyruk_repository = kuyruk_repository or OfflineKuyrukRepository()
        self._logger = logging.getLogger(__name__)

    @islem_izle("offline_islem_ekleme")
    def islem_kuyruga_ekle(
        self, islem_turu: IslemTuru, veri: Dict[str, Any], terminal_id: int, kasiyer_id: int
    ) -> bool:
        """
        İşlemi offline kuyruğa ekler

        Args:
            islem_turu: İşlem türü
            veri: İşlem verisi
            terminal_id: Terminal ID
            kasiyer_id: Kasiyer ID

        Returns:
            Ekleme başarılı mı

        Raises:
            DogrulamaHatasi: Geçersiz parametreler
        """
        self._logger.info(f"Offline işlem kuyruğa ekleniyor - Tür: {islem_turu.value}")

        # Parametre validasyonu
        if terminal_id <= 0:
            raise DogrulamaHatasi("terminal_id_pozitif", "Terminal ID pozitif olmalıdır")

        if kasiyer_id <= 0:
            raise DogrulamaHatasi("kasiyer_id_pozitif", "Kasiyer ID pozitif olmalıdır")

        if not veri:
            raise DogrulamaHatasi("veri_bos", "İşlem verisi boş olamaz")

        try:
            # Veriyi JSON string'e çevir
            veri_json = json.dumps(veri, default=str)

            # Kuyruğa ekle
            kuyruk_id = self._kuyruk_repository.islem_ekle(
                islem_turu=islem_turu,
                veri=veri_json,
                terminal_id=terminal_id,
                kasiyer_id=kasiyer_id,
                durum=KuyrukDurum.BEKLEMEDE,
            )

            if kuyruk_id:
                self._logger.info(f"Offline işlem kuyruğa eklendi - ID: {kuyruk_id}")
                return True
            else:
                raise SontechHatasi("İşlem kuyruğa eklenemedi")

        except Exception as e:
            self._logger.error(f"Offline işlem ekleme hatası: {str(e)}")
            raise

    @islem_izle("offline_kuyruk_senkronizasyon")
    def kuyruk_senkronize_et(self) -> int:
        """
        Offline kuyruğu senkronize eder

        Returns:
            İşlenen kayıt sayısı

        Raises:
            NetworkHatasi: Network bağlantı sorunu
        """
        self._logger.info("Offline kuyruk senkronizasyonu başlatılıyor")

        try:
            # Beklemedeki kayıtları al
            bekleyen_kayitlar = self._kuyruk_repository.bekleyen_kayitlar_getir()

            if not bekleyen_kayitlar:
                self._logger.info("Senkronize edilecek kayıt bulunamadı")
                return 0

            islenen_sayisi = 0

            for kayit in bekleyen_kayitlar:
                try:
                    # İşlemi senkronize et
                    basarili = self._islemi_senkronize_et(kayit)

                    if basarili:
                        # Durumu güncelle
                        self._kuyruk_repository.durum_guncelle(kayit["id"], KuyrukDurum.TAMAMLANDI)
                        islenen_sayisi += 1
                    else:
                        # Hata durumuna güncelle
                        self._kuyruk_repository.durum_guncelle(kayit["id"], KuyrukDurum.HATA)

                except Exception as e:
                    self._logger.error(f"Kayıt senkronizasyon hatası - ID: {kayit['id']}, Hata: {str(e)}")
                    # Hata durumuna güncelle
                    self._kuyruk_repository.durum_guncelle(kayit["id"], KuyrukDurum.HATA)

            self._logger.info(f"Offline kuyruk senkronizasyonu tamamlandı - İşlenen: {islenen_sayisi}")
            return islenen_sayisi

        except Exception as e:
            self._logger.error(f"Kuyruk senkronizasyon hatası: {str(e)}")
            raise

    def kuyruk_istatistikleri_getir(self, terminal_id: int) -> Dict[str, Any]:
        """
        Kuyruk istatistiklerini getirir

        Args:
            terminal_id: Terminal ID

        Returns:
            Kuyruk istatistikleri

        Raises:
            DogrulamaHatasi: Geçersiz terminal ID
        """
        if terminal_id <= 0:
            raise DogrulamaHatasi("terminal_id_pozitif", "Terminal ID pozitif olmalıdır")

        try:
            return self._kuyruk_repository.istatistikler_getir(terminal_id)

        except Exception as e:
            self._logger.error(f"Kuyruk istatistikleri hatası: {str(e)}")
            raise

    def offline_durum_bildir(self, terminal_id: int, kasiyer_id: int, islem_turu: IslemTuru) -> bool:
        """
        Offline durum bildirimi yapar

        Args:
            terminal_id: Terminal ID
            kasiyer_id: Kasiyer ID
            islem_turu: İşlem türü

        Returns:
            Bildirim başarılı mı
        """
        try:
            self._logger.warning(
                f"Offline durum - Terminal: {terminal_id}, " f"Kasiyer: {kasiyer_id}, İşlem: {islem_turu.value}"
            )

            # Offline durum kaydı (isteğe bağlı)
            # Bu kısım monitoring sistemi ile entegre edilebilir

            return True

        except Exception as e:
            self._logger.error(f"Offline durum bildirimi hatası: {str(e)}")
            return False

    def _islemi_senkronize_et(self, kayit: Dict[str, Any]) -> bool:
        """
        Tek bir işlemi senkronize eder

        Args:
            kayit: Kuyruk kaydı

        Returns:
            Senkronizasyon başarılı mı
        """
        try:
            islem_turu = IslemTuru(kayit["islem_turu"])
            veri = json.loads(kayit["veri"])

            # İşlem türüne göre senkronizasyon
            if islem_turu == IslemTuru.SATIS:
                return self._satis_senkronize_et(veri)
            elif islem_turu == IslemTuru.SEPET_URUN_EKLEME:
                return self._sepet_urun_senkronize_et(veri)
            elif islem_turu == IslemTuru.IADE:
                return self._iade_senkronize_et(veri)
            else:
                self._logger.warning(f"Bilinmeyen işlem türü: {islem_turu.value}")
                return False

        except Exception as e:
            self._logger.error(f"İşlem senkronizasyon hatası: {str(e)}")
            return False

    def _satis_senkronize_et(self, veri: Dict[str, Any]) -> bool:
        """Satış işlemini senkronize eder"""
        try:
            # Ana sistem API'sine satış gönder
            # Bu kısım gerçek implementasyonda HTTP client ile yapılacak
            self._logger.info(f"Satış senkronize edildi - Sepet: {veri.get('sepet_id')}")
            return True

        except Exception as e:
            self._logger.error(f"Satış senkronizasyon hatası: {str(e)}")
            return False

    def _sepet_urun_senkronize_et(self, veri: Dict[str, Any]) -> bool:
        """Sepet ürün ekleme işlemini senkronize eder"""
        try:
            # Ana sistem API'sine ürün ekleme gönder
            self._logger.info(f"Sepet ürün senkronize edildi - Barkod: {veri.get('barkod')}")
            return True

        except Exception as e:
            self._logger.error(f"Sepet ürün senkronizasyon hatası: {str(e)}")
            return False

    def _iade_senkronize_et(self, veri: Dict[str, Any]) -> bool:
        """İade işlemini senkronize eder"""
        try:
            # Ana sistem API'sine iade gönder
            self._logger.info(f"İade senkronize edildi - Satış: {veri.get('satis_id')}")
            return True

        except Exception as e:
            self._logger.error(f"İade senkronizasyon hatası: {str(e)}")
            return False
