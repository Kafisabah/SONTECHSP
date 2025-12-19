# Version: 0.1.0
# Last Update: 2024-12-19
# Module: pos_servis_entegratoru
# Description: POS UI ve servis katmanı entegrasyon yöneticisi
# Changelog:
# - İlk oluşturma - POS servis entegrasyonu

"""
POS Servis Entegratörü

POS UI bileşenleri ile servis katmanı arasında entegrasyon sağlar.
Servis çağrılarını yönetir ve hata durumlarını işler.

Sorumluluklar:
- UI bileşenlerini servislerle bağlama
- Servis çağrı hata yönetimi
- Offline kuyruk entegrasyonu
- Sinyal/slot koordinasyonu
"""

from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime

from sontechsp.uygulama.cekirdek.kayit import kayit_al
from sontechsp.uygulama.cekirdek.hatalar import POSHatasi, NetworkHatasi
from ..handlers.pos_sinyalleri import POSSinyalleri
from ..handlers.pos_hata_yoneticisi import POSHataYoneticisi
from ...arayuzler import (
    ISepetService,
    IOdemeService,
    IStokService,
    IOfflineKuyrukService,
    OdemeTuru,
    IslemTuru,
    SepetDurum,
)


class POSServisEntegratoru:
    """
    POS Servis Entegratörü

    UI bileşenleri ile servis katmanı arasında köprü görevi görür.
    Tüm servis çağrılarını koordine eder ve hata yönetimi sağlar.
    """

    def __init__(
        self,
        sinyaller: POSSinyalleri,
        hata_yoneticisi: POSHataYoneticisi,
        sepet_service: Optional[ISepetService] = None,
        odeme_service: Optional[IOdemeService] = None,
        stok_service: Optional[IStokService] = None,
        offline_kuyruk_service: Optional[IOfflineKuyrukService] = None,
    ):
        """
        Entegratör constructor

        Args:
            sinyaller: POS sinyal sistemi
            hata_yoneticisi: Hata yöneticisi
            sepet_service: Sepet servisi (opsiyonel)
            odeme_service: Ödeme servisi (opsiyonel)
            stok_service: Stok servisi (opsiyonel)
            offline_kuyruk_service: Offline kuyruk servisi (opsiyonel)
        """
        self._sinyaller = sinyaller
        self._hata_yoneticisi = hata_yoneticisi
        self._sepet_service = sepet_service
        self._odeme_service = odeme_service
        self._stok_service = stok_service
        self._offline_kuyruk_service = offline_kuyruk_service
        self._logger = kayit_al(__name__)

        # Aktif sepet bilgileri
        self._aktif_sepet_id: Optional[int] = None
        self._terminal_id = 1  # Mock terminal ID
        self._kasiyer_id = 1  # Mock kasiyer ID

        # Sinyalleri bağla
        self._sinyalleri_bagla()

        self._logger.info("POS servis entegratörü başlatıldı")

    def _sinyalleri_bagla(self):
        """Sinyal/slot bağlantılarını kurar"""
        # Barkod ekleme
        self._sinyaller.urun_eklendi.connect(self._urun_sepete_ekle)

        # Sepet işlemleri
        self._sinyaller.urun_cikarildi.connect(self._urun_sepetten_cikar)
        self._sinyaller.sepet_temizlendi.connect(self._sepet_temizle)

        # Ödeme işlemleri
        self._sinyaller.odeme_baslatildi.connect(self._odeme_islemi_baslat)

        # Offline kuyruk
        if self._offline_kuyruk_service:
            self._sinyaller.offline_islem_kuyruga_ekle.connect(self._offline_islem_ekle)

    def baslat(self):
        """Entegratörü başlatır ve yeni sepet oluşturur"""
        try:
            if self._sepet_service:
                # Yeni sepet oluştur
                self._aktif_sepet_id = self._sepet_service.yeni_sepet_olustur(self._terminal_id, self._kasiyer_id)
                self._logger.info(f"Yeni sepet oluşturuldu: {self._aktif_sepet_id}")
            else:
                # Mock sepet ID
                self._aktif_sepet_id = 1
                self._logger.info("Mock sepet oluşturuldu")

            # Sepet başlatıldı sinyali gönder
            self._sinyaller.sepet_baslatildi.emit(self._aktif_sepet_id)

        except Exception as e:
            self._logger.error(f"Sepet başlatma hatası: {str(e)}")
            self._hata_yoneticisi.hata_yakala(e, "Sepet Başlatma")

    def _urun_sepete_ekle(self, urun_verisi: Dict[str, Any]):
        """
        Ürünü sepete ekler

        Args:
            urun_verisi: Ürün bilgileri
        """
        try:
            if not self._aktif_sepet_id:
                raise POSHatasi("Aktif sepet bulunamadı")

            barkod = urun_verisi.get("barkod")
            if not barkod:
                raise POSHatasi("Barkod bilgisi eksik")

            if self._sepet_service:
                # Gerçek servis çağrısı
                basarili = self._sepet_service.barkod_ekle(self._aktif_sepet_id, barkod)

                if basarili:
                    # Güncel sepet bilgisini al ve sinyali gönder
                    self._sepet_bilgisini_guncelle()
                    self._logger.info(f"Ürün sepete eklendi: {barkod}")
                else:
                    raise POSHatasi("Ürün sepete eklenemedi")
            else:
                # Mock işlem - direkt sinyal gönder
                self._sinyaller.sepet_guncellendi.emit([urun_verisi])
                self._logger.info(f"Mock ürün sepete eklendi: {barkod}")

        except Exception as e:
            self._logger.error(f"Ürün ekleme hatası: {str(e)}")

            # Offline durumda kuyruğa ekle
            if self._offline_kuyruk_service and isinstance(e, NetworkHatasi):
                self._offline_islem_ekle(IslemTuru.SEPET_URUN_EKLEME, urun_verisi)
            else:
                self._hata_yoneticisi.hata_yakala(e, "Ürün Ekleme")
                # Hata sinyali gönder
                self._sinyaller.servis_hatasi.emit("Sepet Servisi", str(e))

    def _urun_sepetten_cikar(self, satir_index: int):
        """
        Ürünü sepetten çıkarır

        Args:
            satir_index: Sepet satır index'i
        """
        try:
            if not self._aktif_sepet_id:
                raise POSHatasi("Aktif sepet bulunamadı")

            if self._sepet_service:
                # Gerçek servis çağrısı
                # Not: Satır index'ini satır ID'ye çevirmek gerekir
                # Şimdilik basit bir yaklaşım kullanıyoruz
                satir_id = satir_index + 1  # Mock satır ID

                basarili = self._sepet_service.satir_sil(satir_id)

                if basarili:
                    # Güncel sepet bilgisini al ve sinyali gönder
                    self._sepet_bilgisini_guncelle()
                    self._logger.info(f"Ürün sepetten çıkarıldı: satır {satir_index}")
                else:
                    raise POSHatasi("Ürün sepetten çıkarılamadı")
            else:
                # Mock işlem
                self._logger.info(f"Mock ürün sepetten çıkarıldı: satır {satir_index}")

        except Exception as e:
            self._logger.error(f"Ürün çıkarma hatası: {str(e)}")
            self._hata_yoneticisi.hata_yakala(e, "Ürün Çıkarma")

    def _sepet_temizle(self):
        """Sepeti temizler"""
        try:
            if not self._aktif_sepet_id:
                raise POSHatasi("Aktif sepet bulunamadı")

            if self._sepet_service:
                # Gerçek servis çağrısı
                basarili = self._sepet_service.sepet_bosalt(self._aktif_sepet_id)

                if basarili:
                    # Sepet temizlendi sinyali gönder
                    self._sinyaller.sepet_guncellendi.emit([])
                    self._logger.info("Sepet temizlendi")
                else:
                    raise POSHatasi("Sepet temizlenemedi")
            else:
                # Mock işlem
                self._sinyaller.sepet_guncellendi.emit([])
                self._logger.info("Mock sepet temizlendi")

        except Exception as e:
            self._logger.error(f"Sepet temizleme hatası: {str(e)}")
            self._hata_yoneticisi.hata_yakala(e, "Sepet Temizleme")

    def _odeme_islemi_baslat(self, odeme_turu: str, tutar: Decimal):
        """
        Ödeme işlemini başlatır

        Args:
            odeme_turu: Ödeme türü
            tutar: Ödeme tutarı
        """
        try:
            if not self._aktif_sepet_id:
                raise POSHatasi("Aktif sepet bulunamadı")

            # Ödeme türünü enum'a çevir
            odeme_turu_enum = self._odeme_turu_cevir(odeme_turu)

            if self._odeme_service:
                # Gerçek servis çağrısı
                basarili = self._odeme_service.tek_odeme_yap(self._aktif_sepet_id, odeme_turu_enum, tutar)

                if basarili:
                    # Ödeme tamamlandı sinyali gönder
                    odeme_bilgisi = {
                        "sepet_id": self._aktif_sepet_id,
                        "odeme_turu": odeme_turu,
                        "tutar": float(tutar),
                        "tarih": datetime.now().isoformat(),
                    }
                    self._sinyaller.odeme_tamamlandi.emit(odeme_bilgisi)

                    # Yeni sepet başlat
                    self._yeni_sepet_baslat()

                    self._logger.info(f"Ödeme tamamlandı: {odeme_turu} - {tutar}")
                else:
                    raise POSHatasi("Ödeme işlemi başarısız")
            else:
                # Mock işlem
                odeme_bilgisi = {
                    "sepet_id": self._aktif_sepet_id,
                    "odeme_turu": odeme_turu,
                    "tutar": float(tutar),
                    "tarih": datetime.now().isoformat(),
                }
                self._sinyaller.odeme_tamamlandi.emit(odeme_bilgisi)
                self._logger.info(f"Mock ödeme tamamlandı: {odeme_turu} - {tutar}")

        except Exception as e:
            self._logger.error(f"Ödeme işlemi hatası: {str(e)}")

            # Offline durumda kuyruğa ekle
            if self._offline_kuyruk_service and isinstance(e, NetworkHatasi):
                odeme_verisi = {"sepet_id": self._aktif_sepet_id, "odeme_turu": odeme_turu, "tutar": float(tutar)}
                self._offline_islem_ekle(IslemTuru.SATIS, odeme_verisi)
            else:
                self._hata_yoneticisi.hata_yakala(e, "Ödeme İşlemi")

    def _offline_islem_ekle(self, islem_turu: IslemTuru, veri: Dict[str, Any]):
        """
        Offline işlemi kuyruğa ekler

        Args:
            islem_turu: İşlem türü
            veri: İşlem verisi
        """
        try:
            if self._offline_kuyruk_service:
                basarili = self._offline_kuyruk_service.islem_kuyruga_ekle(
                    islem_turu=islem_turu, veri=veri, terminal_id=self._terminal_id, kasiyer_id=self._kasiyer_id
                )

                if basarili:
                    # Offline durum bildirimi
                    self._offline_kuyruk_service.offline_durum_bildir(self._terminal_id, self._kasiyer_id, islem_turu)

                    # Offline işlem eklendi sinyali
                    self._sinyaller.offline_islem_eklendi.emit(islem_turu.value, veri)

                    self._logger.info(f"Offline işlem kuyruğa eklendi: {islem_turu.value}")
                else:
                    raise POSHatasi("Offline işlem kuyruğa eklenemedi")
            else:
                self._logger.warning("Offline kuyruk servisi mevcut değil")

        except Exception as e:
            self._logger.error(f"Offline işlem ekleme hatası: {str(e)}")
            self._hata_yoneticisi.hata_yakala(e, "Offline İşlem")

    def _sepet_bilgisini_guncelle(self):
        """Güncel sepet bilgisini alır ve sinyali gönderir"""
        try:
            if self._sepet_service and self._aktif_sepet_id:
                sepet_bilgisi = self._sepet_service.sepet_bilgisi_getir(self._aktif_sepet_id)

                if sepet_bilgisi:
                    # Sepet satırlarını UI formatına çevir
                    sepet_satirlari = self._sepet_satirlarini_cevir(sepet_bilgisi.get("satirlar", []))
                    self._sinyaller.sepet_guncellendi.emit(sepet_satirlari)

        except Exception as e:
            self._logger.error(f"Sepet bilgisi güncelleme hatası: {str(e)}")

    def _sepet_satirlarini_cevir(self, satirlar: List[Dict]) -> List[Dict[str, Any]]:
        """
        Sepet satırlarını UI formatına çevirir

        Args:
            satirlar: Servis katmanından gelen sepet satırları

        Returns:
            UI formatında sepet satırları
        """
        ui_satirlar = []

        for satir in satirlar:
            ui_satir = {
                "barkod": satir.get("barkod", ""),
                "urun_adi": satir.get("urun_adi", ""),
                "adet": satir.get("adet", 0),
                "birim_fiyat": Decimal(str(satir.get("birim_fiyat", 0))),
                "toplam_fiyat": Decimal(str(satir.get("toplam_fiyat", 0))),
            }
            ui_satirlar.append(ui_satir)

        return ui_satirlar

    def _odeme_turu_cevir(self, odeme_turu: str) -> OdemeTuru:
        """
        String ödeme türünü enum'a çevirir

        Args:
            odeme_turu: String ödeme türü

        Returns:
            OdemeTuru enum değeri
        """
        odeme_turu_map = {
            "nakit": OdemeTuru.NAKIT,
            "kart": OdemeTuru.KART,
            "parcali": OdemeTuru.PARCALI,
            "acik_hesap": OdemeTuru.ACIK_HESAP,
        }

        return odeme_turu_map.get(odeme_turu, OdemeTuru.NAKIT)

    def _yeni_sepet_baslat(self):
        """Yeni sepet başlatır"""
        try:
            if self._sepet_service:
                # Yeni sepet oluştur
                self._aktif_sepet_id = self._sepet_service.yeni_sepet_olustur(self._terminal_id, self._kasiyer_id)

                # Sepet başlatıldı sinyali gönder
                self._sinyaller.sepet_baslatildi.emit(self._aktif_sepet_id)

                # Boş sepet sinyali gönder
                self._sinyaller.sepet_guncellendi.emit([])

                self._logger.info(f"Yeni sepet başlatıldı: {self._aktif_sepet_id}")
            else:
                # Mock yeni sepet
                self._aktif_sepet_id = (self._aktif_sepet_id or 0) + 1
                self._sinyaller.sepet_baslatildi.emit(self._aktif_sepet_id)
                self._sinyaller.sepet_guncellendi.emit([])

        except Exception as e:
            self._logger.error(f"Yeni sepet başlatma hatası: {str(e)}")
            self._hata_yoneticisi.hata_yakala(e, "Yeni Sepet")

    def offline_kuyruk_senkronize_et(self):
        """Offline kuyruğu senkronize eder"""
        try:
            if self._offline_kuyruk_service:
                islenen_sayisi = self._offline_kuyruk_service.kuyruk_senkronize_et()

                if islenen_sayisi > 0:
                    # Senkronizasyon tamamlandı sinyali
                    self._sinyaller.offline_senkronizasyon_tamamlandi.emit(islenen_sayisi)
                    self._logger.info(f"Offline kuyruk senkronize edildi: {islenen_sayisi} işlem")

        except Exception as e:
            self._logger.error(f"Offline senkronizasyon hatası: {str(e)}")
            self._hata_yoneticisi.hata_yakala(e, "Offline Senkronizasyon")

    def kuyruk_istatistikleri_getir(self) -> Dict[str, Any]:
        """
        Kuyruk istatistiklerini getirir

        Returns:
            Kuyruk istatistikleri
        """
        try:
            if self._offline_kuyruk_service:
                return self._offline_kuyruk_service.kuyruk_istatistikleri_getir(self._terminal_id)
            else:
                return {"toplam_kayit": 0, "durum_sayilari": {}, "islem_turu_sayilari": {}, "network_durumu": True}

        except Exception as e:
            self._logger.error(f"Kuyruk istatistikleri hatası: {str(e)}")
            return {"hata": str(e)}

    def aktif_sepet_id_getir(self) -> Optional[int]:
        """Aktif sepet ID'sini döndürür"""
        return self._aktif_sepet_id

    def servis_durumu_kontrol(self) -> Dict[str, bool]:
        """
        Servislerin durumunu kontrol eder

        Returns:
            Servis durum bilgileri
        """
        return {
            "sepet_service": self._sepet_service is not None,
            "odeme_service": self._odeme_service is not None,
            "stok_service": self._stok_service is not None,
            "offline_kuyruk_service": self._offline_kuyruk_service is not None,
        }
