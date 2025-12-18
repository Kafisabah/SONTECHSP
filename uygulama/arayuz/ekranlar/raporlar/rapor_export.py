# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.raporlar.rapor_export
# Description: Rapor dışa aktarma işlemleri
# Changelog:
# - İlk sürüm oluşturuldu

import csv
import json
from datetime import datetime
from typing import List, Dict, Any


class RaporExportIslemleri:
    """Rapor dışa aktarma işlemleri"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def disa_aktar(self, format_turu: str):
        """Dışa aktarma işlemi"""
        try:
            if not self.parent.rapor_verileri:
                self.parent.hata_goster("Hata", "Önce bir rapor oluşturun")
                return
            
            if format_turu == "excel":
                self._excel_aktar()
            elif format_turu == "pdf":
                self._pdf_aktar()
            elif format_turu == "csv":
                self._csv_aktar()
            else:
                self.parent.hata_goster("Hata", f"Desteklenmeyen format: {format_turu}")
            
        except Exception as e:
            self.parent.hata_goster("Dışa Aktarma Hatası", str(e))
    
    def _excel_aktar(self):
        """Excel formatında dışa aktarma"""
        try:
            # Excel export stub - gerçek implementasyon için openpyxl gerekli
            dosya_adi = f"rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            self.parent.bilgi_goster_mesaj("Bilgi", f"Rapor Excel formatında kaydedilecek: {dosya_adi}")
            
        except Exception as e:
            raise Exception(f"Excel aktarma hatası: {str(e)}")
    
    def _pdf_aktar(self):
        """PDF formatında dışa aktarma"""
        try:
            # PDF export stub - gerçek implementasyon için reportlab gerekli
            dosya_adi = f"rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            self.parent.bilgi_goster_mesaj("Bilgi", f"Rapor PDF formatında kaydedilecek: {dosya_adi}")
            
        except Exception as e:
            raise Exception(f"PDF aktarma hatası: {str(e)}")
    
    def _csv_aktar(self):
        """CSV formatında dışa aktarma"""
        try:
            dosya_adi = f"rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # CSV başlıkları
            basliklar = ["Tarih", "Açıklama", "Miktar", "Tutar", "Kategori", "Durum"]
            
            # CSV verilerini hazırla
            csv_verileri = []
            for veri in self.parent.rapor_verileri:
                satir = [
                    veri["tarih"],
                    veri["aciklama"],
                    str(veri["miktar"]),
                    f"{veri['tutar']:.2f}",
                    veri["kategori"],
                    veri["durum"]
                ]
                csv_verileri.append(satir)
            
            # Dosyaya yaz (stub - gerçek implementasyon dosya dialog'u gerektirir)
            self.parent.bilgi_goster_mesaj("Bilgi", f"Rapor CSV formatında kaydedilecek: {dosya_adi}")
            
        except Exception as e:
            raise Exception(f"CSV aktarma hatası: {str(e)}")
    
    def yazdir(self):
        """Yazdırma işlemi"""
        try:
            if not self.parent.rapor_verileri:
                self.parent.hata_goster("Hata", "Önce bir rapor oluşturun")
                return
            
            # Yazdırma dialog'u stub - gerçek implementasyon için QPrinter gerekli
            self.parent.bilgi_goster_mesaj("Bilgi", "Yazdırma dialog'u açılacak")
            
        except Exception as e:
            self.parent.hata_goster("Yazdırma Hatası", str(e))
    
    def rapor_ozeti_olustur(self) -> Dict[str, Any]:
        """Rapor özeti oluştur"""
        try:
            if not self.parent.rapor_verileri:
                return {}
            
            toplam_tutar = sum(veri["tutar"] for veri in self.parent.rapor_verileri)
            ortalama = toplam_tutar / len(self.parent.rapor_verileri)
            en_yuksek = max(veri["tutar"] for veri in self.parent.rapor_verileri)
            en_dusuk = min(veri["tutar"] for veri in self.parent.rapor_verileri)
            
            ozet = {
                "toplam_kayit": len(self.parent.rapor_verileri),
                "toplam_tutar": toplam_tutar,
                "ortalama": ortalama,
                "en_yuksek": en_yuksek,
                "en_dusuk": en_dusuk,
                "rapor_tarihi": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "rapor_turu": self.parent.aktif_rapor_tipi,
                "alt_tur": self.parent.alt_rapor_combo.currentText() if hasattr(self.parent, 'alt_rapor_combo') else ""
            }
            
            return ozet
            
        except Exception as e:
            self.parent.hata_goster("Özet Oluşturma Hatası", str(e))
            return {}