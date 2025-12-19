# Version: 0.1.0
# Last Update: 2024-12-19
# Module: kod_kalitesi.otomatik_kod_kalitesi
# Description: Otomatik kod kalitesi raporlama sistemi
# Changelog:
# - İlk oluşturma - Otomatik raporlama sistemi

"""
Otomatik Kod Kalitesi Raporlama Sistemi

Belirli aralıklarla kod kalitesi analizleri yapar ve raporlar oluşturur.
CI/CD pipeline'lara entegre edilebilir.
"""

import os
import json
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

from sontechsp.uygulama.cekirdek.kayit import kayit_al
from .pos_kod_kalitesi import POSKodKalitesiKontrolcu, KodKalitesiRaporu


class OtomatikKodKalitesiSistemi:
    """Otomatik kod kalitesi raporlama sistemi"""

    def __init__(self, rapor_klasoru: str = "kod_kalitesi_raporlari"):
        self.logger = kayit_al("otomatik_kod_kalitesi")
        self.rapor_klasoru = Path(rapor_klasoru)
        self.rapor_klasoru.mkdir(exist_ok=True)
        self.pos_kontrolcu = POSKodKalitesiKontrolcu()

    def gunluk_analiz_yap(self):
        """Günlük kod kalitesi analizi yapar"""
        self.logger.info("Günlük kod kalitesi analizi başlatılıyor")

        try:
            # POS analizi
            pos_rapor = self.pos_kontrolcu.analiz_yap()

            # Rapor dosyası adı
            tarih_str = datetime.now().strftime("%Y%m%d")
            rapor_dosyasi = self.rapor_klasoru / f"pos_kod_kalitesi_{tarih_str}.json"

            # Raporu kaydet
            self.pos_kontrolcu.rapor_olustur(pos_rapor, str(rapor_dosyasi))

            # Özet rapor oluştur
            self._ozet_rapor_olustur(pos_rapor, tarih_str)

            # Eğer sorun varsa uyarı ver
            if pos_rapor.toplam_sorun > 0:
                self.logger.warning(f"Kod kalitesi sorunları bulundu: {pos_rapor.toplam_sorun} sorun")
                self._uyari_raporu_olustur(pos_rapor, tarih_str)
            else:
                self.logger.info("Kod kalitesi analizi temiz - sorun bulunamadı")

        except Exception as e:
            self.logger.error(f"Günlük analiz hatası: {e}")
            raise

    def haftalik_trend_analizi(self):
        """Haftalık trend analizi yapar"""
        self.logger.info("Haftalık trend analizi başlatılıyor")

        try:
            # Son 7 günün raporlarını bul
            son_raporlar = self._son_raporlari_bul(7)

            if len(son_raporlar) < 2:
                self.logger.warning("Trend analizi için yeterli rapor yok")
                return

            # Trend analizi yap
            trend_raporu = self._trend_analizi_yap(son_raporlar)

            # Trend raporunu kaydet
            tarih_str = datetime.now().strftime("%Y%m%d")
            trend_dosyasi = self.rapor_klasoru / f"pos_trend_analizi_{tarih_str}.json"

            with open(trend_dosyasi, "w", encoding="utf-8") as f:
                json.dump(trend_raporu, f, ensure_ascii=False, indent=2)

            self.logger.info(f"Trend analizi kaydedildi: {trend_dosyasi}")

        except Exception as e:
            self.logger.error(f"Trend analizi hatası: {e}")
            raise

    def _ozet_rapor_olustur(self, rapor: KodKalitesiRaporu, tarih_str: str):
        """Özet rapor oluşturur"""
        ozet = {
            "tarih": tarih_str,
            "toplam_dosya": rapor.toplam_dosya,
            "sorunlu_dosya": rapor.sorunlu_dosya,
            "toplam_sorun": rapor.toplam_sorun,
            "sorun_dagilimi": {
                "dosya_boyutu": len(rapor.dosya_boyutu_sorunlari),
                "fonksiyon_boyutu": len(rapor.fonksiyon_boyutu_sorunlari),
                "pep8": len(rapor.pep8_sorunlari),
            },
            "kalite_skoru": self._kalite_skoru_hesapla(rapor),
        }

        ozet_dosyasi = self.rapor_klasoru / f"pos_ozet_{tarih_str}.json"
        with open(ozet_dosyasi, "w", encoding="utf-8") as f:
            json.dump(ozet, f, ensure_ascii=False, indent=2)

    def _uyari_raporu_olustur(self, rapor: KodKalitesiRaporu, tarih_str: str):
        """Uyarı raporu oluşturur"""
        uyari_raporu = {
            "tarih": tarih_str,
            "uyari_seviyesi": self._uyari_seviyesi_belirle(rapor),
            "kritik_sorunlar": [],
            "oncelikli_dosyalar": [],
        }

        # Kritik sorunları belirle
        for sorun in rapor.dosya_boyutu_sorunlari:
            if sorun.mevcut_deger and sorun.mevcut_deger > 200:  # Çok büyük dosyalar
                uyari_raporu["kritik_sorunlar"].append(
                    {"tip": "kritik_dosya_boyutu", "dosya": sorun.dosya_yolu, "deger": sorun.mevcut_deger}
                )

        for sorun in rapor.fonksiyon_boyutu_sorunlari:
            if sorun.mevcut_deger and sorun.mevcut_deger > 50:  # Çok büyük fonksiyonlar
                uyari_raporu["kritik_sorunlar"].append(
                    {
                        "tip": "kritik_fonksiyon_boyutu",
                        "dosya": sorun.dosya_yolu,
                        "fonksiyon": sorun.fonksiyon_adi,
                        "deger": sorun.mevcut_deger,
                    }
                )

        uyari_dosyasi = self.rapor_klasoru / f"pos_uyari_{tarih_str}.json"
        with open(uyari_dosyasi, "w", encoding="utf-8") as f:
            json.dump(uyari_raporu, f, ensure_ascii=False, indent=2)

    def _son_raporlari_bul(self, gun_sayisi: int) -> List[Dict[str, Any]]:
        """Son N günün raporlarını bulur"""
        raporlar = []

        for i in range(gun_sayisi):
            tarih = datetime.now() - timedelta(days=i)
            tarih_str = tarih.strftime("%Y%m%d")
            rapor_dosyasi = self.rapor_klasoru / f"pos_ozet_{tarih_str}.json"

            if rapor_dosyasi.exists():
                with open(rapor_dosyasi, "r", encoding="utf-8") as f:
                    raporlar.append(json.load(f))

        return raporlar

    def _trend_analizi_yap(self, raporlar: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Trend analizi yapar"""
        if len(raporlar) < 2:
            return {}

        # Raporları tarihe göre sırala
        raporlar.sort(key=lambda x: x["tarih"])

        ilk_rapor = raporlar[0]
        son_rapor = raporlar[-1]

        trend = {
            "analiz_tarihi": datetime.now().isoformat(),
            "rapor_sayisi": len(raporlar),
            "tarih_araligi": {"baslangic": ilk_rapor["tarih"], "bitis": son_rapor["tarih"]},
            "degisimler": {
                "toplam_sorun": son_rapor["toplam_sorun"] - ilk_rapor["toplam_sorun"],
                "sorunlu_dosya": son_rapor["sorunlu_dosya"] - ilk_rapor["sorunlu_dosya"],
                "kalite_skoru": son_rapor["kalite_skoru"] - ilk_rapor["kalite_skoru"],
            },
            "trend_yonu": self._trend_yonu_belirle(raporlar),
            "oneriler": self._oneriler_olustur(raporlar),
        }

        return trend

    def _kalite_skoru_hesapla(self, rapor: KodKalitesiRaporu) -> float:
        """Kod kalitesi skoru hesaplar (0-100 arası)"""
        if rapor.toplam_dosya == 0:
            return 100.0

        # Temiz dosya oranı
        temiz_oran = len(rapor.temiz_dosyalar) / rapor.toplam_dosya

        # Sorun ağırlıkları
        dosya_boyutu_agirlik = len(rapor.dosya_boyutu_sorunlari) * 3
        fonksiyon_boyutu_agirlik = len(rapor.fonksiyon_boyutu_sorunlari) * 2
        pep8_agirlik = len(rapor.pep8_sorunlari) * 1

        toplam_agirlik = dosya_boyutu_agirlik + fonksiyon_boyutu_agirlik + pep8_agirlik

        # Skor hesapla
        if toplam_agirlik == 0:
            return 100.0

        skor = max(0, 100 - (toplam_agirlik / rapor.toplam_dosya * 10))
        return round(skor, 2)

    def _uyari_seviyesi_belirle(self, rapor: KodKalitesiRaporu) -> str:
        """Uyarı seviyesi belirler"""
        kalite_skoru = self._kalite_skoru_hesapla(rapor)

        if kalite_skoru >= 90:
            return "düşük"
        elif kalite_skoru >= 70:
            return "orta"
        elif kalite_skoru >= 50:
            return "yüksek"
        else:
            return "kritik"

    def _trend_yonu_belirle(self, raporlar: List[Dict[str, Any]]) -> str:
        """Trend yönü belirler"""
        if len(raporlar) < 2:
            return "belirsiz"

        skor_degisimi = raporlar[-1]["kalite_skoru"] - raporlar[0]["kalite_skoru"]

        if skor_degisimi > 5:
            return "iyileşiyor"
        elif skor_degisimi < -5:
            return "kötüleşiyor"
        else:
            return "stabil"

    def _oneriler_olustur(self, raporlar: List[Dict[str, Any]]) -> List[str]:
        """Trend analizine göre öneriler oluşturur"""
        oneriler = []

        if len(raporlar) < 2:
            return oneriler

        son_rapor = raporlar[-1]
        trend_yonu = self._trend_yonu_belirle(raporlar)

        if trend_yonu == "kötüleşiyor":
            oneriler.append("Kod kalitesi düşüş trendinde - acil müdahale gerekli")

        if son_rapor["sorun_dagilimi"]["dosya_boyutu"] > 5:
            oneriler.append("Büyük dosyaları daha küçük modüllere bölmeyi düşünün")

        if son_rapor["sorun_dagilimi"]["fonksiyon_boyutu"] > 10:
            oneriler.append("Büyük fonksiyonları yardımcı fonksiyonlara ayırın")

        if son_rapor["sorun_dagilimi"]["pep8"] > 20:
            oneriler.append("Otomatik kod formatlama araçları kullanmayı düşünün")

        if son_rapor["kalite_skoru"] < 70:
            oneriler.append("Kod kalitesi hedefinin altında - refactoring planı yapın")

        return oneriler

    def zamanli_gorevleri_baslat(self):
        """Zamanlanmış görevleri başlatır"""
        self.logger.info("Otomatik kod kalitesi sistemi başlatılıyor")

        # Günlük analiz - her gün saat 09:00'da
        schedule.every().day.at("09:00").do(self.gunluk_analiz_yap)

        # Haftalık trend analizi - her pazartesi saat 10:00'da
        schedule.every().monday.at("10:00").do(self.haftalik_trend_analizi)

        self.logger.info("Zamanlanmış görevler kuruldu")

        # Sürekli çalış
        while True:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et


def main():
    """Ana çalıştırma fonksiyonu"""
    sistem = OtomatikKodKalitesiSistemi()

    # İlk analizi hemen yap
    sistem.gunluk_analiz_yap()

    # Zamanlanmış görevleri başlat
    sistem.zamanli_gorevleri_baslat()


if __name__ == "__main__":
    main()
