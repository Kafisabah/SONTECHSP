# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.yardimcilar
# Description: UI yardımcı fonksiyonları
# Changelog:
# - İlk sürüm oluşturuldu

from typing import List, Any, Optional
from datetime import datetime
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox, QWidget
from PyQt6.QtCore import Qt
import locale


class UIYardimcilari:
    """UI yardımcı fonksiyonları sınıfı"""
    
    @staticmethod
    def tablo_doldur(tablo: QTableWidget, basliklar: List[str], 
                     veriler: List[List[Any]]) -> None:
        """
        Tablo widget'ını verilerle doldur
        
        Args:
            tablo: Doldurulacak QTableWidget
            basliklar: Sütun başlıkları
            veriler: Tablo verileri (satır listesi)
        """
        try:
            # Tablo boyutlarını ayarla
            tablo.setRowCount(len(veriler))
            tablo.setColumnCount(len(basliklar))
            
            # Başlıkları ayarla
            tablo.setHorizontalHeaderLabels(basliklar)
            
            # Verileri doldur
            for satir_idx, satir in enumerate(veriler):
                for sutun_idx, deger in enumerate(satir):
                    # Veriyi formatla
                    formatli_deger = UIYardimcilari.veri_formatla(deger)
                    
                    # Tablo öğesi oluştur
                    item = QTableWidgetItem(str(formatli_deger))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    
                    # Tabloya ekle
                    tablo.setItem(satir_idx, sutun_idx, item)
            
            # Sütun genişliklerini ayarla
            tablo.resizeColumnsToContents()
            
        except Exception as e:
            UIYardimcilari.hata_goster(
                None, 
                "Tablo Doldurma Hatası", 
                f"Tablo doldurulurken hata oluştu: {e}"
            )
    
    @staticmethod
    def para_formatla(tutar: float, para_birimi: str = "TL") -> str:
        """
        Para tutarını Türk Lirası formatında formatla
        
        Args:
            tutar: Formatlanacak tutar
            para_birimi: Para birimi (varsayılan: TL)
            
        Returns:
            Formatlanmış para string'i (örn: "1.234,56 TL")
        """
        try:
            # Türkçe locale ayarla (Windows için)
            try:
                locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
            except locale.Error:
                # Eğer Türkçe locale yoksa, varsayılan formatı kullan
                pass
            
            # Para formatlaması
            if tutar == 0:
                return f"0,00 {para_birimi}"
            
            # Sayıyı formatla (Türk formatı: 1.234.567,89)
            formatli_sayi = f"{tutar:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            return f"{formatli_sayi} {para_birimi}"
            
        except Exception as e:
            return f"{tutar} {para_birimi}"
    
    @staticmethod
    def tarih_formatla(tarih: datetime, format_tipi: str = "kisa") -> str:
        """
        Tarihi yerel formatta formatla
        
        Args:
            tarih: Formatlanacak datetime objesi
            format_tipi: Format tipi ("kisa", "uzun", "saat")
            
        Returns:
            Formatlanmış tarih string'i
        """
        try:
            if format_tipi == "kisa":
                return tarih.strftime("%d.%m.%Y")
            elif format_tipi == "uzun":
                return tarih.strftime("%d %B %Y")
            elif format_tipi == "saat":
                return tarih.strftime("%d.%m.%Y %H:%M")
            else:
                return tarih.strftime("%d.%m.%Y")
                
        except Exception as e:
            return str(tarih)
    
    @staticmethod
    def veri_formatla(deger: Any) -> str:
        """
        Genel veri formatlaması
        
        Args:
            deger: Formatlanacak değer
            
        Returns:
            Formatlanmış string
        """
        try:
            if deger is None:
                return "-"
            elif isinstance(deger, float):
                # Para olup olmadığını kontrol et (basit heuristic)
                if abs(deger) > 0.01:  # Küçük değerler para olabilir
                    return UIYardimcilari.para_formatla(deger)
                else:
                    return f"{deger:.2f}"
            elif isinstance(deger, datetime):
                return UIYardimcilari.tarih_formatla(deger)
            elif isinstance(deger, bool):
                return "Evet" if deger else "Hayır"
            else:
                return str(deger)
                
        except Exception:
            return str(deger)
    
    @staticmethod
    def hata_goster(parent: Optional[QWidget], baslik: str, mesaj: str) -> None:
        """
        Standart hata dialog'u göster
        
        Args:
            parent: Ana widget (None olabilir)
            baslik: Dialog başlığı
            mesaj: Hata mesajı
        """
        try:
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(baslik)
            msg_box.setText(mesaj)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            # Türkçe buton metni
            msg_box.button(QMessageBox.StandardButton.Ok).setText("Tamam")
            
            msg_box.exec()
            
        except Exception as e:
            # Son çare: print ile hata göster
            print(f"Hata Dialog Hatası: {e}")
            print(f"Orijinal Hata - {baslik}: {mesaj}")
    
    @staticmethod
    def bilgi_goster(parent: Optional[QWidget], baslik: str, mesaj: str) -> None:
        """
        Standart bilgi dialog'u göster
        
        Args:
            parent: Ana widget (None olabilir)
            baslik: Dialog başlığı
            mesaj: Bilgi mesajı
        """
        try:
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle(baslik)
            msg_box.setText(mesaj)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            # Türkçe buton metni
            msg_box.button(QMessageBox.StandardButton.Ok).setText("Tamam")
            
            msg_box.exec()
            
        except Exception as e:
            print(f"Bilgi Dialog Hatası: {e}")
    
    @staticmethod
    def onay_iste(parent: Optional[QWidget], baslik: str, mesaj: str) -> bool:
        """
        Kullanıcıdan onay iste
        
        Args:
            parent: Ana widget (None olabilir)
            baslik: Dialog başlığı
            mesaj: Onay mesajı
            
        Returns:
            True: Evet, False: Hayır
        """
        try:
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setWindowTitle(baslik)
            msg_box.setText(mesaj)
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            # Türkçe buton metinleri
            msg_box.button(QMessageBox.StandardButton.Yes).setText("Evet")
            msg_box.button(QMessageBox.StandardButton.No).setText("Hayır")
            
            sonuc = msg_box.exec()
            return sonuc == QMessageBox.StandardButton.Yes
            
        except Exception as e:
            print(f"Onay Dialog Hatası: {e}")
            return False