# Version: 0.1.0
# Last Update: 2024-12-19
# Module: kod_kalitesi.pos_kod_kalitesi
# Description: POS modülü için kod kalitesi kontrol araçları
# Changelog:
# - İlk oluşturma - POS kod kalitesi kontrolleri

"""
POS Kod Kalitesi Kontrol Araçları

POS modülü dosyalarının kod kalitesi standartlarına uygunluğunu kontrol eder.
Dosya boyutu, fonksiyon boyutu ve PEP8 uyumluluğunu denetler.
"""

import ast
import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from sontechsp.uygulama.cekirdek.kayit import kayit_al


@dataclass
class KodKalitesiSorunu:
    """Kod kalitesi sorunu veri yapısı"""

    dosya_yolu: str
    sorun_tipi: str  # 'dosya_boyutu', 'fonksiyon_boyutu', 'pep8'
    aciklama: str
    satir_no: Optional[int] = None
    fonksiyon_adi: Optional[str] = None
    mevcut_deger: Optional[int] = None
    limit_deger: Optional[int] = None


@dataclass
class KodKalitesiRaporu:
    """Kod kalitesi raporu veri yapısı"""

    analiz_tarihi: str
    toplam_dosya: int
    sorunlu_dosya: int
    toplam_sorun: int
    dosya_boyutu_sorunlari: List[KodKalitesiSorunu]
    fonksiyon_boyutu_sorunlari: List[KodKalitesiSorunu]
    pep8_sorunlari: List[KodKalitesiSorunu]
    temiz_dosyalar: List[str]


class POSKodKalitesiKontrolcu:
    """POS modülü kod kalitesi kontrol sınıfı"""

    def __init__(self):
        self.logger = kayit_al("pos_kod_kalitesi")
        self.pos_ui_klasoru = "sontechsp/uygulama/moduller/pos/ui"
        self.max_dosya_boyutu = 120
        self.max_fonksiyon_boyutu = 25

    def analiz_yap(self) -> KodKalitesiRaporu:
        """POS UI dosyalarının kod kalitesi analizini yapar"""
        self.logger.info("POS kod kalitesi analizi başlatılıyor")

        pos_dosyalari = self._pos_dosyalarini_bul()

        dosya_boyutu_sorunlari = []
        fonksiyon_boyutu_sorunlari = []
        pep8_sorunlari = []
        temiz_dosyalar = []

        for dosya_yolu in pos_dosyalari:
            dosya_sorunlari = self._dosya_analiz_et(dosya_yolu)

            if not dosya_sorunlari:
                temiz_dosyalar.append(dosya_yolu)
            else:
                for sorun in dosya_sorunlari:
                    if sorun.sorun_tipi == "dosya_boyutu":
                        dosya_boyutu_sorunlari.append(sorun)
                    elif sorun.sorun_tipi == "fonksiyon_boyutu":
                        fonksiyon_boyutu_sorunlari.append(sorun)
                    elif sorun.sorun_tipi == "pep8":
                        pep8_sorunlari.append(sorun)

        rapor = KodKalitesiRaporu(
            analiz_tarihi=datetime.now().isoformat(),
            toplam_dosya=len(pos_dosyalari),
            sorunlu_dosya=len(pos_dosyalari) - len(temiz_dosyalar),
            toplam_sorun=len(dosya_boyutu_sorunlari) + len(fonksiyon_boyutu_sorunlari) + len(pep8_sorunlari),
            dosya_boyutu_sorunlari=dosya_boyutu_sorunlari,
            fonksiyon_boyutu_sorunlari=fonksiyon_boyutu_sorunlari,
            pep8_sorunlari=pep8_sorunlari,
            temiz_dosyalar=temiz_dosyalar,
        )

        self.logger.info(f"Analiz tamamlandı: {rapor.toplam_sorun} sorun bulundu")
        return rapor

    def _pos_dosyalarini_bul(self) -> List[str]:
        """POS UI klasöründeki Python dosyalarını bulur"""
        pos_dosyalari = []

        if os.path.exists(self.pos_ui_klasoru):
            for root, dirs, files in os.walk(self.pos_ui_klasoru):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        pos_dosyalari.append(os.path.join(root, file))

        return pos_dosyalari

    def _dosya_analiz_et(self, dosya_yolu: str) -> List[KodKalitesiSorunu]:
        """Tek dosyanın kod kalitesi analizini yapar"""
        sorunlar = []

        try:
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                satirlar = f.readlines()
                icerik = "".join(satirlar)

            # Dosya boyutu kontrolü
            kod_satirlari = [satir for satir in satirlar if satir.strip() and not satir.strip().startswith("#")]

            if len(kod_satirlari) > self.max_dosya_boyutu:
                sorunlar.append(
                    KodKalitesiSorunu(
                        dosya_yolu=dosya_yolu,
                        sorun_tipi="dosya_boyutu",
                        aciklama=f"Dosya {len(kod_satirlari)} satır, limit {self.max_dosya_boyutu}",
                        mevcut_deger=len(kod_satirlari),
                        limit_deger=self.max_dosya_boyutu,
                    )
                )

            # Fonksiyon boyutu kontrolü
            try:
                tree = ast.parse(icerik)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        fonksiyon_satirlari = node.end_lineno - node.lineno + 1
                        if fonksiyon_satirlari > self.max_fonksiyon_boyutu:
                            sorunlar.append(
                                KodKalitesiSorunu(
                                    dosya_yolu=dosya_yolu,
                                    sorun_tipi="fonksiyon_boyutu",
                                    aciklama=f"Fonksiyon {node.name} {fonksiyon_satirlari} satır, limit {self.max_fonksiyon_boyutu}",
                                    satir_no=node.lineno,
                                    fonksiyon_adi=node.name,
                                    mevcut_deger=fonksiyon_satirlari,
                                    limit_deger=self.max_fonksiyon_boyutu,
                                )
                            )
            except SyntaxError:
                sorunlar.append(
                    KodKalitesiSorunu(
                        dosya_yolu=dosya_yolu, sorun_tipi="pep8", aciklama="Syntax hatası - dosya parse edilemiyor"
                    )
                )

            # PEP8 kontrolü
            for satir_no, satir in enumerate(satirlar, 1):
                # Satır uzunluğu kontrolü
                if len(satir.rstrip()) > 120:
                    sorunlar.append(
                        KodKalitesiSorunu(
                            dosya_yolu=dosya_yolu,
                            sorun_tipi="pep8",
                            aciklama=f"Satır uzunluğu {len(satir.rstrip())} karakter, limit 120",
                            satir_no=satir_no,
                            mevcut_deger=len(satir.rstrip()),
                            limit_deger=120,
                        )
                    )

                # Tab karakteri kontrolü
                if "\t" in satir:
                    sorunlar.append(
                        KodKalitesiSorunu(
                            dosya_yolu=dosya_yolu,
                            sorun_tipi="pep8",
                            aciklama="Tab karakteri kullanılmış, 4 boşluk kullanın",
                            satir_no=satir_no,
                        )
                    )

                # Satır sonu boşluk kontrolü
                if satir.endswith(" \n") or satir.endswith(" \r\n"):
                    sorunlar.append(
                        KodKalitesiSorunu(
                            dosya_yolu=dosya_yolu,
                            sorun_tipi="pep8",
                            aciklama="Satır sonunda gereksiz boşluk",
                            satir_no=satir_no,
                        )
                    )

        except Exception as e:
            self.logger.error(f"Dosya analiz hatası {dosya_yolu}: {e}")
            sorunlar.append(
                KodKalitesiSorunu(dosya_yolu=dosya_yolu, sorun_tipi="pep8", aciklama=f"Dosya okunamadı: {str(e)}")
            )

        return sorunlar

    def rapor_olustur(self, rapor: KodKalitesiRaporu, dosya_yolu: str = "pos_kod_kalitesi_raporu.json"):
        """Kod kalitesi raporunu JSON dosyasına kaydeder"""
        rapor_dict = {
            "analiz_tarihi": rapor.analiz_tarihi,
            "toplam_dosya": rapor.toplam_dosya,
            "sorunlu_dosya": rapor.sorunlu_dosya,
            "toplam_sorun": rapor.toplam_sorun,
            "dosya_boyutu_sorunlari": [
                {
                    "dosya_yolu": s.dosya_yolu,
                    "aciklama": s.aciklama,
                    "mevcut_deger": s.mevcut_deger,
                    "limit_deger": s.limit_deger,
                }
                for s in rapor.dosya_boyutu_sorunlari
            ],
            "fonksiyon_boyutu_sorunlari": [
                {
                    "dosya_yolu": s.dosya_yolu,
                    "fonksiyon_adi": s.fonksiyon_adi,
                    "satir_no": s.satir_no,
                    "aciklama": s.aciklama,
                    "mevcut_deger": s.mevcut_deger,
                    "limit_deger": s.limit_deger,
                }
                for s in rapor.fonksiyon_boyutu_sorunlari
            ],
            "pep8_sorunlari": [
                {"dosya_yolu": s.dosya_yolu, "satir_no": s.satir_no, "aciklama": s.aciklama}
                for s in rapor.pep8_sorunlari
            ],
            "temiz_dosyalar": rapor.temiz_dosyalar,
        }

        with open(dosya_yolu, "w", encoding="utf-8") as f:
            json.dump(rapor_dict, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Rapor kaydedildi: {dosya_yolu}")

    def konsol_raporu_yazdir(self, rapor: KodKalitesiRaporu):
        """Kod kalitesi raporunu konsola yazdırır"""
        print("=" * 70)
        print("🔍 POS KOD KALİTESİ ANALİZ RAPORU")
        print("=" * 70)
        print(f"📅 Analiz Tarihi: {rapor.analiz_tarihi}")
        print(f"📁 Toplam Dosya: {rapor.toplam_dosya}")
        print(f"⚠️  Sorunlu Dosya: {rapor.sorunlu_dosya}")
        print(f"🐛 Toplam Sorun: {rapor.toplam_sorun}")
        print()

        if rapor.dosya_boyutu_sorunlari:
            print(f"📄 DOSYA BOYUTU SORUNLARI ({len(rapor.dosya_boyutu_sorunlari)} adet):")
            for sorun in rapor.dosya_boyutu_sorunlari[:5]:
                print(f"  • {sorun.dosya_yolu}")
                print(f"    {sorun.aciklama}")
            if len(rapor.dosya_boyutu_sorunlari) > 5:
                print(f"  ... ve {len(rapor.dosya_boyutu_sorunlari) - 5} dosya daha")
            print()

        if rapor.fonksiyon_boyutu_sorunlari:
            print(f"🔧 FONKSİYON BOYUTU SORUNLARI ({len(rapor.fonksiyon_boyutu_sorunlari)} adet):")
            for sorun in rapor.fonksiyon_boyutu_sorunlari[:5]:
                print(f"  • {sorun.dosya_yolu}::{sorun.fonksiyon_adi} (satır {sorun.satir_no})")
                print(f"    {sorun.aciklama}")
            if len(rapor.fonksiyon_boyutu_sorunlari) > 5:
                print(f"  ... ve {len(rapor.fonksiyon_boyutu_sorunlari) - 5} fonksiyon daha")
            print()

        if rapor.pep8_sorunlari:
            print(f"📏 PEP8 SORUNLARI ({len(rapor.pep8_sorunlari)} adet):")
            for sorun in rapor.pep8_sorunlari[:10]:
                satir_info = f" (satır {sorun.satir_no})" if sorun.satir_no else ""
                print(f"  • {sorun.dosya_yolu}{satir_info}")
                print(f"    {sorun.aciklama}")
            if len(rapor.pep8_sorunlari) > 10:
                print(f"  ... ve {len(rapor.pep8_sorunlari) - 10} sorun daha")
            print()

        if rapor.temiz_dosyalar:
            print(f"✅ TEMİZ DOSYALAR ({len(rapor.temiz_dosyalar)} adet):")
            for dosya in rapor.temiz_dosyalar:
                print(f"  • {dosya}")
            print()

        print("=" * 70)


def main():
    """Ana çalıştırma fonksiyonu"""
    kontrolcu = POSKodKalitesiKontrolcu()
    rapor = kontrolcu.analiz_yap()

    # Konsol raporu
    kontrolcu.konsol_raporu_yazdir(rapor)

    # JSON raporu
    kontrolcu.rapor_olustur(rapor)

    return rapor


if __name__ == "__main__":
    main()
