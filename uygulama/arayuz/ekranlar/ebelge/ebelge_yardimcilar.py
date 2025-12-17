# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ebelge.ebelge_yardimcilar
# Description: E-belge yardımcı fonksiyonlar
# Changelog:
# - İlk sürüm oluşturuldu

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QTableWidgetItem

from ...yardimcilar import UIYardimcilari

if TYPE_CHECKING:
    from .ebelge_ana import EbelgeAnaEkran


class EbelgeYardimcilar:
    """E-belge yardımcı fonksiyonlar"""
    
    def __init__(self, parent: 'EbelgeAnaEkran') -> None:
        self.parent = parent
    
    def filtre_uygula(self) -> None:
        """Filtre uygula"""
        try:
            # Tüm listeleri yenile
            self.parent.bekleyen_listesi_yenile()
            self.parent.gonderilen_listesi_yenile()
            self.parent.hatali_listesi_yenile()
            
        except Exception as e:
            self.parent.hata_goster("Filtre Hatası", str(e))
    
    def belge_gonder(self):
        """Belge gönderme işlemi"""
        try:
            # E-belge servisini çağır
            ebelge_servisi = self.parent.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.parent.durum.islem_baslat("Belgeler gönderiliyor...")
            
            sonuc = self.parent.servis_cagir_guvenli(ebelge_servisi.gonder)
            
            if sonuc:
                self.parent.bilgi_goster_mesaj("Başarılı", "Belgeler başarıyla gönderildi")
                self.parent.bekleyen_listesi_yenile()
                self.parent.gonderilen_listesi_yenile()
            
            self.parent.durum.islem_bitir()
            
        except Exception as e:
            self.parent.durum.islem_bitir()
            self.parent.hata_goster("Belge Gönderme Hatası", str(e))
    
    def durum_sorgula(self):
        """Durum sorgulama işlemi"""
        try:
            # E-belge servisini çağır
            ebelge_servisi = self.parent.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.parent.durum.islem_baslat("Durum sorgulanıyor...")
            
            sonuc = self.parent.servis_cagir_guvenli(ebelge_servisi.durum_sorgula)
            
            if sonuc:
                self.parent.bilgi_goster_mesaj("Başarılı", "Durum sorgulaması tamamlandı")
                self.parent.gonderilen_listesi_yenile()
            
            self.parent.durum.islem_bitir()
            
        except Exception as e:
            self.parent.durum.islem_bitir()
            self.parent.hata_goster("Durum Sorgulama Hatası", str(e))
    
    def tekrar_dene(self):
        """Tekrar deneme işlemi"""
        try:
            # E-belge servisini çağır
            ebelge_servisi = self.parent.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.parent.durum.islem_baslat("Hatalı belgeler tekrar gönderiliyor...")
            
            sonuc = self.parent.servis_cagir_guvenli(ebelge_servisi.tekrar_dene)
            
            if sonuc:
                self.parent.bilgi_goster_mesaj("Başarılı", "Hatalı belgeler tekrar gönderildi")
                self.parent.hatali_listesi_yenile()
                self.parent.bekleyen_listesi_yenile()
            
            self.parent.durum.islem_bitir()
            
        except Exception as e:
            self.parent.durum.islem_bitir()
            self.parent.hata_goster("Tekrar Deneme Hatası", str(e))
    
    def toplu_gonder(self):
        """Toplu gönderme işlemi"""
        try:
            if not self.parent.onay_iste("Onay", "Tüm bekleyen belgeler gönderilecek. Emin misiniz?"):
                return
            
            # E-belge servisini çağır
            ebelge_servisi = self.parent.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.parent.durum.islem_baslat("Toplu gönderim yapılıyor...")
            
            sonuc = self.parent.servis_cagir_guvenli(ebelge_servisi.gonder)
            
            if sonuc:
                self.parent.bilgi_goster_mesaj("Başarılı", "Toplu gönderim tamamlandı")
                self.parent.bekleyen_listesi_yenile()
                self.parent.gonderilen_listesi_yenile()
            
            self.parent.durum.islem_bitir()
            
        except Exception as e:
            self.parent.durum.islem_bitir()
            self.parent.hata_goster("Toplu Gönderim Hatası", str(e))
    
    def xml_goruntule(self):
        """XML görüntüleme"""
        try:
            # XML görüntüleme dialog'u (stub)
            self.parent.bilgi_goster_mesaj("Bilgi", "XML görüntüleme dialog'u açılacak")
            
        except Exception as e:
            self.parent.hata_goster("XML Görüntüleme Hatası", str(e))
    
    def secilenleri_gonder(self):
        """Seçilen belgeleri gönder"""
        try:
            secili_satirlar = self.parent.bekleyen_tablo.selectionModel().selectedRows()
            if not secili_satirlar:
                self.parent.hata_goster("Hata", "Lütfen gönderilecek belgeleri seçin")
                return
            
            if not self.parent.onay_iste("Onay", f"{len(secili_satirlar)} belge gönderilecek. Emin misiniz?"):
                return
            
            # Seçili belgeleri gönder (stub)
            self.parent.bilgi_goster_mesaj("Başarılı", f"{len(secili_satirlar)} belge gönderildi")
            self.parent.bekleyen_listesi_yenile()
            
        except Exception as e:
            self.parent.hata_goster("Seçili Gönderim Hatası", str(e))
    
    def pdf_indir(self):
        """PDF indirme"""
        try:
            # PDF indirme dialog'u (stub)
            self.parent.bilgi_goster_mesaj("Bilgi", "PDF indirme dialog'u açılacak")
            
        except Exception as e:
            self.parent.hata_goster("PDF İndirme Hatası", str(e))
    
    def hatalari_duzelt(self):
        """Hataları düzeltme"""
        try:
            # Hata düzeltme dialog'u (stub)
            self.parent.bilgi_goster_mesaj("Bilgi", "Hata düzeltme dialog'u açılacak")
            
        except Exception as e:
            self.parent.hata_goster("Hata Düzeltme Hatası", str(e))