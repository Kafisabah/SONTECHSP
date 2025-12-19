# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.refactoring.import_duzenleyici
# Description: Import yapısını düzenleyen ve mimari kuralları uygulayan sistem
# Changelog:
# - İlk versiyon: ImportDuzenleyici sınıfı oluşturuldu

"""
Import Düzenleyici

Import yapısını düzenler, mimari kuralları uygular
ve dependency injection pattern'ini destekler.
"""

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set


class KatmanTuru(Enum):
    """Mimari katman türleri"""
    UI = "ui"
    SERVIS = "servis"
    REPOSITORY = "repository"
    DATABASE = "database"
    ORTAK = "ortak"


@dataclass
class ImportDuzeltmePlani:
    """Import düzeltme planı"""
    dosya_yolu: str
    eski_importlar: List[str]
    yeni_importlar: List[str]
    katman: KatmanTuru
    ihlaller: List[str]


class ImportDuzenleyici:
    """
    Import yapısını düzenleyen sınıf.
    
    Mimari kuralları uygular:
    - UI katmanı sadece servis katmanını import eder
    - Servis katmanı sadece repository katmanını import eder
    - Repository katmanı sadece database katmanını import eder
    
    Dependency injection pattern'ini destekler.
    """
    
    def __init__(self):
        """Import düzenleyici başlatıcı"""
        self.katman_hiyerarsisi = {
            KatmanTuru.UI: [KatmanTuru.SERVIS, KatmanTuru.ORTAK],
            KatmanTuru.SERVIS: [KatmanTuru.REPOSITORY, KatmanTuru.ORTAK],
            KatmanTuru.REPOSITORY: [KatmanTuru.DATABASE, KatmanTuru.ORTAK],
            KatmanTuru.DATABASE: [KatmanTuru.ORTAK],
            KatmanTuru.ORTAK: []
        }
    
    def import_yapisini_duzenle(
        self,
        dosya_yolu: str
    ) -> ImportDuzeltmePlani:
        """
        Dosyanın import yapısını düzenler.
        
        Args:
            dosya_yolu: Düzenlenecek dosya yolu
            
        Returns:
            Import düzeltme planı
        """
        # Dosyayı oku
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        # Katmanı belirle
        katman = self._katman_belirle(dosya_yolu)
        
        # Mevcut import'ları analiz et
        mevcut_importlar = self._importlari_cikart(icerik)
        
        # İhlalleri tespit et
        ihlaller = self._ihlalleri_tespit_et(mevcut_importlar, katman)
        
        # Yeni import yapısı oluştur
        yeni_importlar = self._yeni_import_yapisi_olustur(
            mevcut_importlar, katman, ihlaller
        )
        
        return ImportDuzeltmePlani(
            dosya_yolu=dosya_yolu,
            eski_importlar=mevcut_importlar,
            yeni_importlar=yeni_importlar,
            katman=katman,
            ihlaller=ihlaller
        )

    def _katman_belirle(self, dosya_yolu: str) -> KatmanTuru:
        """
        Dosya yolundan katman türünü belirler.
        
        Args:
            dosya_yolu: Dosya yolu
            
        Returns:
            Katman türü
        """
        yol_parcalari = Path(dosya_yolu).parts
        
        if 'arayuz' in yol_parcalari or 'ui' in yol_parcalari:
            return KatmanTuru.UI
        elif 'servisler' in yol_parcalari or 'services' in yol_parcalari:
            return KatmanTuru.SERVIS
        elif 'depolar' in yol_parcalari or 'repositories' in yol_parcalari:
            return KatmanTuru.REPOSITORY
        elif 'veritabani' in yol_parcalari or 'database' in yol_parcalari:
            return KatmanTuru.DATABASE
        else:
            return KatmanTuru.ORTAK
    
    def _importlari_cikart(self, dosya_icerik: str) -> List[str]:
        """
        Dosyadaki import ifadelerini çıkartır.
        
        Args:
            dosya_icerik: Dosya içeriği
            
        Returns:
            Import satırları listesi
        """
        try:
            agac = ast.parse(dosya_icerik)
        except SyntaxError:
            return []
        
        import_satirlari = []
        satirlar = dosya_icerik.split('\n')
        
        for node in agac.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                satir_no = node.lineno - 1
                if satir_no < len(satirlar):
                    import_satirlari.append(satirlar[satir_no])
        
        return import_satirlari
    
    def _ihlalleri_tespit_et(
        self,
        importlar: List[str],
        katman: KatmanTuru
    ) -> List[str]:
        """
        Import ihlallerini tespit eder.
        
        Args:
            importlar: Import listesi
            katman: Dosyanın katmanı
            
        Returns:
            İhlal mesajları listesi
        """
        ihlaller = []
        izin_verilen_katmanlar = self.katman_hiyerarsisi.get(katman, [])
        
        for imp in importlar:
            hedef_katman = self._import_katmani_belirle(imp)
            
            if hedef_katman not in izin_verilen_katmanlar:
                if hedef_katman != KatmanTuru.ORTAK:
                    ihlaller.append(
                        f"{katman.value} katmanı {hedef_katman.value} "
                        f"katmanını import edemez: {imp}"
                    )
        
        return ihlaller
    
    def _import_katmani_belirle(self, import_satiri: str) -> KatmanTuru:
        """
        Import satırından hedef katmanı belirler.
        
        Args:
            import_satiri: Import satırı
            
        Returns:
            Hedef katman türü
        """
        satir_kucuk = import_satiri.lower()
        
        if 'arayuz' in satir_kucuk or 'ui' in satir_kucuk:
            return KatmanTuru.UI
        elif 'servis' in satir_kucuk or 'service' in satir_kucuk:
            return KatmanTuru.SERVIS
        elif 'depo' in satir_kucuk or 'repository' in satir_kucuk:
            return KatmanTuru.REPOSITORY
        elif 'veritabani' in satir_kucuk or 'database' in satir_kucuk:
            return KatmanTuru.DATABASE
        else:
            return KatmanTuru.ORTAK

    def _yeni_import_yapisi_olustur(
        self,
        mevcut_importlar: List[str],
        katman: KatmanTuru,
        ihlaller: List[str]
    ) -> List[str]:
        """
        Yeni import yapısı oluşturur.
        
        İhlalleri düzeltir ve dependency injection pattern'ini uygular.
        
        Args:
            mevcut_importlar: Mevcut import'lar
            katman: Dosyanın katmanı
            ihlaller: Tespit edilen ihlaller
            
        Returns:
            Düzeltilmiş import listesi
        """
        yeni_importlar = []
        izin_verilen_katmanlar = self.katman_hiyerarsisi.get(katman, [])
        
        for imp in mevcut_importlar:
            hedef_katman = self._import_katmani_belirle(imp)
            
            # İzin verilen import'ları koru
            if hedef_katman in izin_verilen_katmanlar or hedef_katman == KatmanTuru.ORTAK:
                yeni_importlar.append(imp)
            else:
                # İhlal eden import'ları düzelt
                duzeltilmis = self._import_duzelt(imp, katman, hedef_katman)
                if duzeltilmis:
                    yeni_importlar.append(duzeltilmis)
        
        # Import'ları sırala: standart kütüphane, üçüncü parti, yerel
        return self._importlari_sirala(yeni_importlar)
    
    def _import_duzelt(
        self,
        import_satiri: str,
        kaynak_katman: KatmanTuru,
        hedef_katman: KatmanTuru
    ) -> str:
        """
        İhlal eden import'ı düzeltir.
        
        Args:
            import_satiri: Orijinal import satırı
            kaynak_katman: Kaynak katman
            hedef_katman: Hedef katman
            
        Returns:
            Düzeltilmiş import satırı veya None
        """
        # UI katmanı repository/database import ediyorsa
        if kaynak_katman == KatmanTuru.UI:
            if hedef_katman in [KatmanTuru.REPOSITORY, KatmanTuru.DATABASE]:
                # Servis katmanına yönlendir
                return import_satiri.replace('depolar', 'servisler').replace('veritabani', 'servisler')
        
        # Servis katmanı UI import ediyorsa
        if kaynak_katman == KatmanTuru.SERVIS:
            if hedef_katman == KatmanTuru.UI:
                # Bu import'u kaldır (servis UI'dan bağımsız olmalı)
                return None
        
        # Repository katmanı servis/UI import ediyorsa
        if kaynak_katman == KatmanTuru.REPOSITORY:
            if hedef_katman in [KatmanTuru.SERVIS, KatmanTuru.UI]:
                # Bu import'u kaldır
                return None
        
        return import_satiri
    
    def _importlari_sirala(self, importlar: List[str]) -> List[str]:
        """
        Import'ları standart sıraya göre düzenler.
        
        Sıralama:
        1. Standart kütüphane import'ları
        2. Üçüncü parti import'ları
        3. Yerel import'lar
        
        Args:
            importlar: Import listesi
            
        Returns:
            Sıralanmış import listesi
        """
        standart = []
        ucuncu_parti = []
        yerel = []
        
        standart_kutuphaneler = {
            'os', 'sys', 'ast', 'pathlib', 'typing', 'dataclasses',
            'enum', 'datetime', 're', 'json', 'collections'
        }
        
        for imp in importlar:
            # Import edilen modülü bul
            if imp.startswith('from '):
                modul = imp.split()[1].split('.')[0]
            elif imp.startswith('import '):
                modul = imp.split()[1].split('.')[0]
            else:
                modul = ''
            
            if modul in standart_kutuphaneler:
                standart.append(imp)
            elif modul.startswith('uygulama') or modul.startswith('sontechsp'):
                yerel.append(imp)
            else:
                ucuncu_parti.append(imp)
        
        # Sırala ve birleştir
        sonuc = []
        if standart:
            sonuc.extend(sorted(standart))
            sonuc.append('')
        if ucuncu_parti:
            sonuc.extend(sorted(ucuncu_parti))
            sonuc.append('')
        if yerel:
            sonuc.extend(sorted(yerel))
        
        return sonuc
    
    def dependency_injection_uygula(
        self,
        dosya_yolu: str,
        bagimliliklari: List[str]
    ) -> str:
        """
        Dependency injection pattern'ini uygular.
        
        Args:
            dosya_yolu: Dosya yolu
            bagimliliklari: Bağımlılık listesi
            
        Returns:
            Güncellenmiş dosya içeriği
        """
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        # Sınıf tanımlarını bul
        try:
            agac = ast.parse(icerik)
        except SyntaxError:
            return icerik
        
        # Her sınıf için __init__ metodunu güncelle
        # Bu basitleştirilmiş bir yaklaşım
        # Gerçek uygulamada daha sofistike bir yöntem gerekir
        
        return icerik
