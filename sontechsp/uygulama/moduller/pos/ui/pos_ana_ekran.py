# Version: 0.1.0
# Last Update: 2024-12-19
# Module: pos_ana_ekran
# Description: POS ana ekran container - Grid layout (3x3) yapısı
# Changelog:
# - İlk oluşturma - POS UI altyapısı
# - Kod analizi ve düzeltmeler

"""
POS Ana Ekran Container

Ana POS ekranı için container sınıfı.
Grid layout (3x3) yapısında bileşenleri organize eder.

Sorumluluklar:
- Ana POS layout yönetimi
- Bileşen container'ları
- Sinyal koordinasyonu
- Klavye kısayolu yönetimi
"""

from typing import Dict, Optional, Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from sontechsp.uygulama.arayuz.taban_ekran import TabanEkran
from sontechsp.uygulama.cekirdek.hatalar import POSHatasi
from sontechsp.uygulama.cekirdek.kayit import kayit_al
from .handlers.pos_sinyalleri import POSSinyalleri
from .handlers.klavye_kisayol_yoneticisi import KlavyeKisayolYoneticisi
from .handlers.pos_hata_yoneticisi import POSHataYoneticisi
from .handlers.pos_servis_entegratoru import POSServisEntegratoru
from .bilesenler.hizli_urun_paneli import HizliUrunPaneli
from .bilesenler.barkod_paneli import BarkodPaneli
from .bilesenler.sepet_tablosu import SepetTablosu
from .bilesenler.odeme_paneli import OdemePaneli
from .bilesenler.islem_kisayollari import IslemKisayollari
from .bilesenler.eslestirme_dialog import EslestirmeDialog


class POSAnaEkran(TabanEkran):
    """
    POS Ana Ekran Container

    Grid layout (3x3) yapısında POS bileşenlerini organize eder.
    """

    def __init__(self, sepet_service=None, odeme_service=None, stok_service=None, offline_kuyruk_service=None):
        # Bileşen referansları - super().__init__() çağrısından önce tanımla
        self._bilesenler: Dict[str, QWidget] = {}

        # Sinyal sistemi - super().__init__() çağrısından önce tanımla
        self.pos_sinyalleri = POSSinyalleri()

        # Klavye kısayol yöneticisi
        self.klavye_yoneticisi = KlavyeKisayolYoneticisi()

        # Hata yöneticisi (super().__init__() çağrısından sonra oluşturulacak)
        self.hata_yoneticisi = None

        # Servisleri başlat (eğer verilmemişse default'ları kullan)
        # Önce stok servisi (diğerleri buna bağımlı)
        self._stok_service = stok_service or self._default_stok_service_olustur()
        self._sepet_service = sepet_service or self._default_sepet_service_olustur()
        self._odeme_service = odeme_service or self._default_odeme_service_olustur()
        self._offline_kuyruk_service = offline_kuyruk_service or self._default_offline_kuyruk_service_olustur()

        # Servis entegratörü (hata yöneticisi olmadan geçici oluştur)
        self.servis_entegratoru = None

        # Eşleştirme dialog referansı
        self._eslestirme_dialog: Optional[EslestirmeDialog] = None

        super().__init__("POS Ana Ekran")
        self.logger = kayit_al("pos_ana_ekran")

        # Hata yöneticisini şimdi oluştur (super().__init__() çağrısından sonra)
        self.hata_yoneticisi = POSHataYoneticisi(self)

        # Servis entegratörünü yeniden oluştur (hata yöneticisi ile)
        self.servis_entegratoru = POSServisEntegratoru(
            sinyaller=self.pos_sinyalleri,
            hata_yoneticisi=self.hata_yoneticisi,
            sepet_service=self._sepet_service,
            odeme_service=self._odeme_service,
            stok_service=self._stok_service,
            offline_kuyruk_service=self._offline_kuyruk_service,
        )

        # POS özel sinyalleri bağla
        self._pos_sinyalleri_bagla()

        # Servis entegratörünü başlat
        self.servis_entegratoru.baslat()

        self.logger.info("POS ana ekran oluşturuldu")

    def _ui_kur(self):
        """UI bileşenlerini kurar"""
        # Grid layout (3x3) - TabanEkran'ın icerik_layout'una ekle
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        # Bileşen container'larını oluştur
        self._barkod_container_olustur(grid_layout, 0, 0, 1, 2)
        self._sepet_container_olustur(grid_layout, 1, 0, 1, 2)
        self._odeme_container_olustur(grid_layout, 2, 0, 1, 2)
        self._hizli_urun_container_olustur(grid_layout, 0, 2, 2, 1)
        self._islem_kisayol_container_olustur(grid_layout, 2, 2, 1, 1)

        self.icerik_layout.addLayout(grid_layout)

        # Alt panel - Eşleştirme tablosu butonu
        alt_panel = self._alt_panel_olustur()
        self.icerik_layout.addWidget(alt_panel)

    def _barkod_container_olustur(self, layout: QGridLayout, row: int, col: int, rowspan: int, colspan: int):
        """Barkod paneli container'ını oluşturur"""
        container = self._container_olustur("Barkod Girişi")

        # Barkod panelini oluştur ve ekle
        barkod_paneli = BarkodPaneli(self.pos_sinyalleri, self._stok_service)
        self._bilesenler["barkod_paneli"] = barkod_paneli

        # Container'daki placeholder'ı kaldır ve bileşeni ekle
        container_layout = container.layout()
        if container_layout.count() > 1:  # Başlık + placeholder
            container_layout.itemAt(1).widget().deleteLater()
        container_layout.addWidget(barkod_paneli)

        layout.addWidget(container, row, col, rowspan, colspan)
        self._bilesenler["barkod_container"] = container

    def _sepet_container_olustur(self, layout: QGridLayout, row: int, col: int, rowspan: int, colspan: int):
        """Sepet tablosu container'ını oluşturur"""
        container = self._container_olustur("Sepet")

        # Sepet tablosunu oluştur ve ekle
        sepet_tablosu = SepetTablosu(self.pos_sinyalleri)
        self._bilesenler["sepet_tablosu"] = sepet_tablosu

        # Container'daki placeholder'ı kaldır ve bileşeni ekle
        container_layout = container.layout()
        if container_layout.count() > 1:  # Başlık + placeholder
            container_layout.itemAt(1).widget().deleteLater()
        container_layout.addWidget(sepet_tablosu)

        layout.addWidget(container, row, col, rowspan, colspan)
        self._bilesenler["sepet_container"] = container

    def _odeme_container_olustur(self, layout: QGridLayout, row: int, col: int, rowspan: int, colspan: int):
        """Ödeme paneli container'ını oluşturur"""
        container = self._container_olustur("Ödeme")

        # Ödeme panelini oluştur ve ekle
        odeme_paneli = OdemePaneli(self.pos_sinyalleri)
        self._bilesenler["odeme_paneli"] = odeme_paneli

        # Container'daki placeholder'ı kaldır ve bileşeni ekle
        container_layout = container.layout()
        if container_layout.count() > 1:  # Başlık + placeholder
            container_layout.itemAt(1).widget().deleteLater()
        container_layout.addWidget(odeme_paneli)

        layout.addWidget(container, row, col, rowspan, colspan)
        self._bilesenler["odeme_container"] = container

    def _hizli_urun_container_olustur(self, layout: QGridLayout, row: int, col: int, rowspan: int, colspan: int):
        """Hızlı ürün paneli container'ını oluşturur"""
        container = self._container_olustur("Hızlı Ürünler")

        # Hızlı ürün panelini oluştur ve ekle
        hizli_urun_paneli = HizliUrunPaneli(self.pos_sinyalleri)
        self._bilesenler["hizli_urun_paneli"] = hizli_urun_paneli

        # Container'daki placeholder'ı kaldır ve bileşeni ekle
        container_layout = container.layout()
        if container_layout.count() > 1:  # Başlık + placeholder
            container_layout.itemAt(1).widget().deleteLater()
        container_layout.addWidget(hizli_urun_paneli)

        layout.addWidget(container, row, col, rowspan, colspan)
        self._bilesenler["hizli_urun_container"] = container

    def _islem_kisayol_container_olustur(self, layout: QGridLayout, row: int, col: int, rowspan: int, colspan: int):
        """İşlem kısayolları container'ını oluşturur"""
        container = self._container_olustur("İşlem Kısayolları")

        # İşlem kısayolları panelini oluştur ve ekle
        islem_kisayollari = IslemKisayollari(self.pos_sinyalleri, self)
        self._bilesenler["islem_kisayollari"] = islem_kisayollari

        # Container'daki placeholder'ı kaldır ve bileşeni ekle
        container_layout = container.layout()
        if container_layout.count() > 1:  # Başlık + placeholder
            container_layout.itemAt(1).widget().deleteLater()
        container_layout.addWidget(islem_kisayollari)

        layout.addWidget(container, row, col, rowspan, colspan)
        self._bilesenler["islem_container"] = container

    def _container_olustur(self, baslik: str) -> QFrame:
        """Bileşen container'ı oluşturur"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(
            """
            QFrame {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                margin: 2px;
            }
        """
        )

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)

        # Container başlığı
        baslik_label = QLabel(baslik)
        baslik_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                color: #34495e;
                font-size: 12px;
                padding: 4px;
                background-color: #f8f9fa;
                border-radius: 3px;
            }
        """
        )
        layout.addWidget(baslik_label)

        # İçerik alanı (şimdilik boş)
        icerik_label = QLabel(f"{baslik} bileşeni henüz eklenmedi")
        icerik_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icerik_label.setStyleSheet(
            """
            QLabel {
                color: #95a5a6;
                font-style: italic;
                padding: 20px;
            }
        """
        )
        layout.addWidget(icerik_label)

        return frame

    def _alt_panel_olustur(self) -> QWidget:
        """Alt panel (eşleştirme tablosu butonu) oluşturur"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 5, 0, 0)

        # Spacer
        layout.addStretch()

        # Eşleştirme tablosu butonu
        self.eslestirme_butonu = QPushButton("Eşleştirmeleri Göster")
        self.eslestirme_butonu.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
        )
        self.eslestirme_butonu.clicked.connect(self._eslestirme_tablosu_goster)
        layout.addWidget(self.eslestirme_butonu)

        return panel

    def _pos_sinyalleri_bagla(self):
        """POS özel sinyal-slot bağlantılarını kurar"""
        # Klavye kısayolları
        self.klavye_yoneticisi.kisayol_tetiklendi.connect(self._klavye_kisayolu_isle)

        # POS sinyalleri
        self.pos_sinyalleri.hata_olustu.connect(self._hata_goster)
        self.pos_sinyalleri.servis_hatasi.connect(self._servis_hatasi_isle)
        self.pos_sinyalleri.servis_basarili.connect(self._servis_basarili_isle)
        self.pos_sinyalleri.offline_islem_eklendi.connect(self._offline_islem_eklendi)
        self.pos_sinyalleri.offline_senkronizasyon_tamamlandi.connect(self._offline_senkronizasyon_tamamlandi)

        # Hata yöneticisi sinyalleri
        self.hata_yoneticisi.hata_islendi.connect(self._hata_islendi)
        self.hata_yoneticisi.kritik_hata.connect(self._kritik_hata_islendi)
        self.hata_yoneticisi.sistem_durumu_korundu.connect(self._sistem_durumu_korundu)

    def _klavye_kisayolu_isle(self, kisayol: str):
        """Klavye kısayolu işler"""
        self.logger.debug(f"Klavye kısayolu: {kisayol}")
        # İleride bileşenlere yönlendirilecek

    def _hata_goster(self, hata_mesaji: str):
        """Hata mesajını gösterir"""
        self.logger.error(f"POS hatası: {hata_mesaji}")
        # Hata yöneticisi üzerinden işle
        from sontechsp.uygulama.cekirdek.hatalar import POSHatasi

        hata = POSHatasi(hata_mesaji, islem_tipi="genel")
        self.hata_yoneticisi.hata_yakala(hata, "POS Ana Ekran")

    def _hata_islendi(self, hata_tipi: str, mesaj: str):
        """Hata işlendiğinde çağrılır"""
        self.logger.debug(f"Hata işlendi: {hata_tipi} - {mesaj}")

    def _kritik_hata_islendi(self, mesaj: str):
        """Kritik hata işlendiğinde çağrılır"""
        self.logger.critical(f"Kritik POS hatası: {mesaj}")
        # İleride: Güvenli duruma geçiş işlemleri

    def _sistem_durumu_korundu(self):
        """Sistem durumu korunduğunda çağrılır"""
        self.logger.info("POS sistem durumu korundu")

    def _servis_hatasi_isle(self, servis_adi: str, hata_mesaji: str):
        """Servis hatası işlendiğinde çağrılır"""
        self.logger.error(f"Servis hatası - {servis_adi}: {hata_mesaji}")
        # UI'da hata gösterimi yapılabilir

    def _servis_basarili_isle(self, servis_adi: str, mesaj: str):
        """Servis başarılı işlendiğinde çağrılır"""
        self.logger.info(f"Servis başarılı - {servis_adi}: {mesaj}")

    def _offline_islem_eklendi(self, islem_turu: str, veri: dict):
        """Offline işlem eklendiğinde çağrılır"""
        self.logger.info(f"Offline işlem eklendi: {islem_turu}")
        # UI'da offline durum gösterimi yapılabilir

    def _offline_senkronizasyon_tamamlandi(self, islenen_sayisi: int):
        """Offline senkronizasyon tamamlandığında çağrılır"""
        self.logger.info(f"Offline senkronizasyon tamamlandı: {islenen_sayisi} işlem")
        # UI'da başarı mesajı gösterilebilir

    def bilesen_ekle(self, bilesen_adi: str, bilesen: QWidget):
        """Bileşen ekler"""
        if bilesen_adi in self._bilesenler:
            container = self._bilesenler[bilesen_adi]
            # Container'daki placeholder'ı kaldır ve bileşeni ekle
            layout = container.layout()
            if layout.count() > 1:  # Başlık + placeholder
                layout.itemAt(1).widget().deleteLater()
            layout.addWidget(bilesen)

            self.logger.debug(f"Bileşen eklendi: {bilesen_adi}")

    def keyPressEvent(self, event):
        """Klavye olaylarını yakalar"""
        # Klavye yöneticisine yönlendir
        if self.klavye_yoneticisi.olay_isle(event):
            return

        # Üst sınıfa yönlendir
        super().keyPressEvent(event)

    def temizle(self):
        """Ekranı temizler"""
        self.logger.debug("POS ana ekran temizleniyor")

        # Tüm bileşenlerin temizle metodlarını çağır
        for bilesen_adi, bilesen in self._bilesenler.items():
            if hasattr(bilesen, "temizle"):
                try:
                    bilesen.temizle()
                except Exception as e:
                    self.logger.error(f"Bileşen temizleme hatası - {bilesen_adi}: {str(e)}")

    def offline_senkronizasyon_yap(self):
        """Offline kuyruk senkronizasyonu yapar"""
        try:
            self.servis_entegratoru.offline_kuyruk_senkronize_et()
        except Exception as e:
            self.logger.error(f"Offline senkronizasyon hatası: {str(e)}")
            self.hata_yoneticisi.hata_yakala(e, "Offline Senkronizasyon")

    def kuyruk_istatistikleri_getir(self) -> Dict[str, Any]:
        """Kuyruk istatistiklerini getirir"""
        return self.servis_entegratoru.kuyruk_istatistikleri_getir()

    def servis_durumu_getir(self) -> Dict[str, bool]:
        """Servis durumlarını getirir"""
        return self.servis_entegratoru.servis_durumu_kontrol()

    def _eslestirme_tablosu_goster(self):
        """Eşleştirme tablosu dialogunu gösterir"""
        try:
            if self._eslestirme_dialog is None:
                self._eslestirme_dialog = EslestirmeDialog(self)
                self._eslestirme_dialog.dialog_kapandi.connect(self._eslestirme_dialog_kapandi)

            self._eslestirme_dialog.show()
            self._eslestirme_dialog.raise_()
            self._eslestirme_dialog.activateWindow()

            self.logger.debug("Eşleştirme tablosu dialogu açıldı")

        except Exception as e:
            self.logger.error(f"Eşleştirme tablosu açılırken hata: {e}")
            # Hata yöneticisi üzerinden işle
            self.hata_yoneticisi.hata_yakala(e, "Eşleştirme Tablosu")

    def _eslestirme_dialog_kapandi(self):
        """Eşleştirme dialogu kapatıldığında çağrılır"""
        self.logger.debug("Eşleştirme tablosu dialogu kapatıldı")

    def _default_sepet_service_olustur(self):
        """Default sepet servisi oluşturur"""
        try:
            from ...servisler.sepet_service import SepetService

            return SepetService(stok_service=self._stok_service)
        except ImportError:
            # Logger henüz tanımlı değil, print kullan
            print("Uyarı: Sepet servisi yüklenemedi")
            return None
        except Exception:
            print("Hata: Sepet servisi oluşturulamadı")
            return None

    def _default_odeme_service_olustur(self):
        """Default ödeme servisi oluşturur"""
        try:
            from ...servisler.odeme_service import OdemeService

            return OdemeService(stok_service=self._stok_service)
        except ImportError:
            print("Uyarı: Ödeme servisi yüklenemedi")
            return None
        except Exception:
            print("Hata: Ödeme servisi oluşturulamadı")
            return None

    def _default_stok_service_olustur(self):
        """Default stok servisi oluşturur"""
        try:
            from ...servisler.stok_service import StokService
            from ....stok.servisler.stok_entegrasyon_service import StokEntegrasyonService
            from ....stok.servisler.stok_rezervasyon_service import StokRezervasyonService
            from ....stok.servisler.barkod_service import BarkodService
            from ....stok.depolar.stok_bakiye_repository import StokBakiyeRepository

            # Stok modülü bağımlılıklarını oluştur
            bakiye_repository = StokBakiyeRepository()
            entegrasyon_service = StokEntegrasyonService()
            rezervasyon_service = StokRezervasyonService()
            barkod_service = BarkodService()

            return StokService(
                stok_entegrasyon_service=entegrasyon_service,
                rezervasyon_service=rezervasyon_service,
                barkod_service=barkod_service,
                bakiye_repository=bakiye_repository,
            )
        except ImportError:
            print("Uyarı: Stok servisi yüklenemedi")
            return None
        except Exception:
            print("Hata: Stok servisi oluşturulamadı")
            return None

    def _default_offline_kuyruk_service_olustur(self):
        """Default offline kuyruk servisi oluşturur"""
        try:
            from ...servisler.offline_kuyruk_service import OfflineKuyrukService

            return OfflineKuyrukService()
        except ImportError:
            print("Uyarı: Offline kuyruk servisi yüklenemedi")
            return None
        except Exception:
            print("Hata: Offline kuyruk servisi oluşturulamadı")
            return None

    def servis_cagri_yap(self, servis_adi: str, metod_adi: str, *args, **kwargs):
        """
        Güvenli servis çağrısı yapar

        Args:
            servis_adi: Servis adı ('sepet', 'odeme', 'stok', 'offline_kuyruk')
            metod_adi: Çağrılacak metod adı
            *args: Pozisyonel parametreler
            **kwargs: Anahtar kelime parametreleri

        Returns:
            Servis çağrı sonucu veya None
        """
        try:
            # Servis referansını al
            servis = None
            if servis_adi == "sepet":
                servis = self._sepet_service
            elif servis_adi == "odeme":
                servis = self._odeme_service
            elif servis_adi == "stok":
                servis = self._stok_service
            elif servis_adi == "offline_kuyruk":
                servis = self._offline_kuyruk_service

            if not servis:
                self.logger.warning(f"Servis mevcut değil: {servis_adi}")
                return None

            # Metod var mı kontrol et
            if not hasattr(servis, metod_adi):
                self.logger.error(f"Metod bulunamadı: {servis_adi}.{metod_adi}")
                return None

            # Metodu çağır
            metod = getattr(servis, metod_adi)
            sonuc = metod(*args, **kwargs)

            # Başarılı servis çağrısı sinyali
            self.pos_sinyalleri.servis_basarili.emit(servis_adi, f"{metod_adi} başarılı")

            return sonuc

        except Exception as e:
            self.logger.error(f"Servis çağrı hatası - {servis_adi}.{metod_adi}: {str(e)}")

            # Hata yöneticisi ile işle
            self.hata_yoneticisi.hata_yakala(e, f"{servis_adi} Servisi")

            # Servis hatası sinyali
            self.pos_sinyalleri.servis_hatasi.emit(servis_adi, str(e))

            return None

    def barkod_ile_urun_ekle(self, barkod: str) -> bool:
        """
        Barkod ile ürün ekler (UI'dan çağrılır)

        Args:
            barkod: Ürün barkodu

        Returns:
            Ekleme başarılı mı
        """
        try:
            if not barkod or not barkod.strip():
                raise POSHatasi("Barkod boş olamaz")

            # Servis entegratörü üzerinden ürün ekle
            urun_verisi = {"barkod": barkod.strip()}
            self.pos_sinyalleri.urun_eklendi.emit(urun_verisi)

            return True

        except Exception as e:
            self.logger.error(f"Barkod ürün ekleme hatası: {str(e)}")
            self.hata_yoneticisi.hata_yakala(e, "Barkod Ürün Ekleme")
            return False

    def odeme_yap(self, odeme_turu: str, tutar: float) -> bool:
        """
        Ödeme işlemi yapar (UI'dan çağrılır)

        Args:
            odeme_turu: Ödeme türü ('nakit', 'kart', 'parcali', 'acik_hesap')
            tutar: Ödeme tutarı

        Returns:
            Ödeme başarılı mı
        """
        try:
            from decimal import Decimal

            if tutar <= 0:
                raise POSHatasi("Ödeme tutarı pozitif olmalıdır")

            # Servis entegratörü üzerinden ödeme yap
            tutar_decimal = Decimal(str(tutar))
            self.pos_sinyalleri.odeme_baslatildi.emit(odeme_turu, tutar_decimal)

            return True

        except Exception as e:
            self.logger.error(f"Ödeme işlemi hatası: {str(e)}")
            self.hata_yoneticisi.hata_yakala(e, "Ödeme İşlemi")
            return False

    def sepet_satiri_sil(self, satir_index: int) -> bool:
        """
        Sepet satırını siler (UI'dan çağrılır)

        Args:
            satir_index: Satır index'i

        Returns:
            Silme başarılı mı
        """
        try:
            if satir_index < 0:
                raise POSHatasi("Geçersiz satır index'i")

            # Servis entegratörü üzerinden satır sil
            self.pos_sinyalleri.urun_cikarildi.emit(satir_index)

            return True

        except Exception as e:
            self.logger.error(f"Satır silme hatası: {str(e)}")
            self.hata_yoneticisi.hata_yakala(e, "Satır Silme")
            return False

    def sepet_bosalt(self) -> bool:
        """
        Sepeti boşaltır (UI'dan çağrılır)

        Returns:
            Boşaltma başarılı mı
        """
        try:
            # Servis entegratörü üzerinden sepet temizle
            self.pos_sinyalleri.sepet_temizlendi.emit()

            return True

        except Exception as e:
            self.logger.error(f"Sepet boşaltma hatası: {str(e)}")
            self.hata_yoneticisi.hata_yakala(e, "Sepet Boşaltma")
            return False

    def _icerik_olustur(self):
        """TabanEkran'dan gelen soyut metod - içerik oluşturur"""
        self._ui_kur()

    def yenile(self):
        """TabanEkran'dan gelen soyut metod - ekranı yeniler"""
        self.logger.debug("POS ana ekran yenileniyor")

        # Tüm bileşenlerin yenile metodlarını çağır
        for bilesen_adi, bilesen in self._bilesenler.items():
            if hasattr(bilesen, "yenile"):
                try:
                    bilesen.yenile()
                except Exception as e:
                    self.logger.error(f"Bileşen yenileme hatası - {bilesen_adi}: {str(e)}")
