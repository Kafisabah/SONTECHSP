# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.test_entegrasyon.test_guncelleyici
# Description: Test dosyalarını refactoring sonrası güncelleyen sistem
# Changelog:
# - İlk versiyon: TestGuncelleyici sınıfı oluşturuldu

"""
Test Güncelleyici

Refactoring işlemleri sonrasında etkilenen test dosyalarını
tespit eder ve import yapılarını günceller.
"""

import ast
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class DosyaDegisikligi:
    """Dosya değişiklik bilgisi"""
    eski_yol: str
    yeni_yol: str
    eski_modul: str
    yeni_modul: str
    tasınan_semboller: List[str] = field(default_factory=list)


@dataclass
class TestGuncellemeBilgisi:
    """Test güncelleme bilgisi"""
    test_dosyasi: str
    etkilenen_importlar: List[str] = field(default_factory=list)
    yeni_importlar: List[str] = field(default_factory=list)
    guncelleme_basarili: bool = False
    hata_mesaji: str = ""


class TestGuncelleyici:
    """
    Test dosyalarını refactoring sonrası güncelleyen sınıf.
    
    Dosya bölme, taşıma ve yeniden adlandırma işlemlerinden
    etkilenen test dosyalarını tespit eder ve import yapılarını
    otomatik olarak günceller.
    """
    
    def __init__(self, test_klasoru: str = "tests"):
        """
        Args:
            test_klasoru: Test dosyalarının bulunduğu klasör
        """
        self.test_klasoru = test_klasoru
    
    def etkilenen_testleri_tespit_et(
        self,
        degisiklikler: List[DosyaDegisikligi]
    ) -> List[str]:
        """
        Verilen değişikliklerden etkilenen test dosyalarını tespit eder.
        
        Args:
            degisiklikler: Dosya değişiklikleri listesi
            
        Returns:
            Etkilenen test dosyalarının yolları
        """
        etkilenen_testler = set()
        
        # Tüm test dosyalarını tara
        for test_dosyasi in self._test_dosyalarini_bul():
            # Test dosyasındaki import'ları analiz et
            importlar = self._test_importlarini_analiz_et(test_dosyasi)
            
            # Değişikliklerle eşleşen import var mı kontrol et
            for degisiklik in degisiklikler:
                for import_ifadesi in importlar:
                    if self._import_etkilenmi(import_ifadesi, degisiklik):
                        etkilenen_testler.add(test_dosyasi)
                        break
        
        return list(etkilenen_testler)
    
    def testleri_guncelle(
        self,
        degisiklikler: List[DosyaDegisikligi]
    ) -> List[TestGuncellemeBilgisi]:
        """
        Etkilenen testleri günceller.
        
        Args:
            degisiklikler: Dosya değişiklikleri listesi
            
        Returns:
            Test güncelleme bilgileri
        """
        sonuclar = []
        
        # Etkilenen testleri tespit et
        etkilenen_testler = self.etkilenen_testleri_tespit_et(degisiklikler)
        
        # Her test dosyasını güncelle
        for test_dosyasi in etkilenen_testler:
            sonuc = self._test_dosyasini_guncelle(test_dosyasi, degisiklikler)
            sonuclar.append(sonuc)
        
        return sonuclar
    
    def import_yapisini_guncelle(
        self,
        test_dosyasi: str,
        eski_modul: str,
        yeni_modul: str,
        semboller: List[str] = None
    ) -> bool:
        """
        Test dosyasındaki import yapısını günceller.
        
        Args:
            test_dosyasi: Test dosyası yolu
            eski_modul: Eski modül yolu
            yeni_modul: Yeni modül yolu
            semboller: Taşınan semboller (None ise tüm import güncellenir)
            
        Returns:
            Güncelleme başarılı mı
        """
        try:
            # Dosyayı oku
            with open(test_dosyasi, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            # Import'ları güncelle
            yeni_icerik = self._import_satirlarini_guncelle(
                icerik, eski_modul, yeni_modul, semboller
            )
            
            # Dosyayı yaz
            with open(test_dosyasi, 'w', encoding='utf-8') as f:
                f.write(yeni_icerik)
            
            return True
            
        except Exception as e:
            print(f"Test güncelleme hatası: {e}")
            return False
    
    def _test_dosyalarini_bul(self) -> List[str]:
        """
        Test klasöründeki tüm test dosyalarını bulur.
        
        Returns:
            Test dosyası yolları
        """
        test_dosyalari = []
        
        if not os.path.exists(self.test_klasoru):
            return test_dosyalari
        
        for root, dirs, files in os.walk(self.test_klasoru):
            for dosya in files:
                if dosya.startswith('test_') and dosya.endswith('.py'):
                    test_dosyalari.append(os.path.join(root, dosya))
        
        return test_dosyalari
    
    def _test_importlarini_analiz_et(self, test_dosyasi: str) -> List[str]:
        """
        Test dosyasındaki import ifadelerini analiz eder.
        
        Args:
            test_dosyasi: Test dosyası yolu
            
        Returns:
            Import ifadeleri listesi
        """
        try:
            with open(test_dosyasi, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            agac = ast.parse(icerik)
            importlar = []
            
            for node in ast.walk(agac):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        importlar.append(f"import {alias.name}")
                
                elif isinstance(node, ast.ImportFrom):
                    modul = node.module or ""
                    semboller = [alias.name for alias in node.names]
                    importlar.append(f"from {modul} import {', '.join(semboller)}")
            
            return importlar
            
        except Exception:
            return []
    
    def _import_etkilenmi(
        self,
        import_ifadesi: str,
        degisiklik: DosyaDegisikligi
    ) -> bool:
        """
        Import ifadesinin değişiklikten etkilenip etkilenmediğini kontrol eder.
        
        Args:
            import_ifadesi: Import ifadesi
            degisiklik: Dosya değişikliği
            
        Returns:
            Etkilenmiş mi
        """
        # Eski modül adı import'ta geçiyor mu
        return degisiklik.eski_modul in import_ifadesi
    
    def _test_dosyasini_guncelle(
        self,
        test_dosyasi: str,
        degisiklikler: List[DosyaDegisikligi]
    ) -> TestGuncellemeBilgisi:
        """
        Tek bir test dosyasını günceller.
        
        Args:
            test_dosyasi: Test dosyası yolu
            degisiklikler: Dosya değişiklikleri
            
        Returns:
            Güncelleme bilgisi
        """
        bilgi = TestGuncellemeBilgisi(test_dosyasi=test_dosyasi)
        
        try:
            # Dosyayı oku
            with open(test_dosyasi, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            yeni_icerik = icerik
            
            # Her değişiklik için import'ları güncelle
            for degisiklik in degisiklikler:
                # Etkilenen import'ları tespit et
                importlar = self._test_importlarini_analiz_et(test_dosyasi)
                etkilenen = [
                    imp for imp in importlar
                    if self._import_etkilenmi(imp, degisiklik)
                ]
                
                if etkilenen:
                    bilgi.etkilenen_importlar.extend(etkilenen)
                    
                    # Import'ları güncelle
                    yeni_icerik = self._import_satirlarini_guncelle(
                        yeni_icerik,
                        degisiklik.eski_modul,
                        degisiklik.yeni_modul,
                        degisiklik.tasınan_semboller
                    )
            
            # Değişiklik varsa dosyayı yaz
            if yeni_icerik != icerik:
                with open(test_dosyasi, 'w', encoding='utf-8') as f:
                    f.write(yeni_icerik)
                
                bilgi.guncelleme_basarili = True
            else:
                bilgi.guncelleme_basarili = True  # Değişiklik gerekmedi
            
        except Exception as e:
            bilgi.guncelleme_basarili = False
            bilgi.hata_mesaji = str(e)
        
        return bilgi
    
    def _import_satirlarini_guncelle(
        self,
        icerik: str,
        eski_modul: str,
        yeni_modul: str,
        semboller: List[str] = None
    ) -> str:
        """
        İçerikteki import satırlarını günceller.
        
        Args:
            icerik: Dosya içeriği
            eski_modul: Eski modül yolu
            yeni_modul: Yeni modül yolu
            semboller: Taşınan semboller
            
        Returns:
            Güncellenmiş içerik
        """
        satirlar = icerik.split('\n')
        yeni_satirlar = []
        
        for satir in satirlar:
            yeni_satir = satir
            
            # "from X import Y" formatı
            if 'from' in satir and 'import' in satir:
                if eski_modul in satir:
                    # Sembol kontrolü
                    if semboller:
                        # Sadece belirtilen sembolleri güncelle
                        for sembol in semboller:
                            if sembol in satir:
                                yeni_satir = satir.replace(eski_modul, yeni_modul)
                                break
                    else:
                        # Tüm import'u güncelle
                        yeni_satir = satir.replace(eski_modul, yeni_modul)
            
            # "import X" formatı
            elif satir.strip().startswith('import '):
                if eski_modul in satir:
                    yeni_satir = satir.replace(eski_modul, yeni_modul)
            
            yeni_satirlar.append(yeni_satir)
        
        return '\n'.join(yeni_satirlar)
