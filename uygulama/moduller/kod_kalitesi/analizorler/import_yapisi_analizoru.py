# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.analizorler.import_yapisi_analizoru
# Description: Import yapısı ve mimari uyumluluk analizi
# Changelog:
# - İlk versiyon: ImportYapisiAnalizoru sınıfı oluşturuldu

"""
Import Yapısı Analizörü

Katmanlı mimari kurallarına uygunluğu kontrol eder.
"""

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List


class KatmanTuru(Enum):
    """Mimari katman türleri"""
    UI = "ui"
    SERVIS = "servis"
    REPOSITORY = "repository"
    DATABASE = "database"
    ORTAK = "ortak"
    BILINMEYEN = "bilinmeyen"


@dataclass
class ImportBilgisi:
    """Import bilgisi"""
    modul_adi: str
    kaynak_dosya: str
    satir_no: int


@dataclass
class MimariIhlal:
    """Mimari ihlal raporu"""
    kaynak_dosya: str
    hedef_dosya: str
    ihlal_turu: str
    cozum_onerisi: str


class ImportYapisiAnalizoru:
    """
    Import yapısı analizi yapan sınıf.
    
    Katmanlı mimari kurallarına uygunluğu kontrol eder:
    - UI katmanı repository/database import edemez
    - Servis katmanı UI import edemez
    - Repository katmanı servis/UI import edemez
    """
    
    def __init__(self, proje_kok_yolu: str = None):
        """
        Args:
            proje_kok_yolu: Proje kök dizini
        """
        self.proje_kok_yolu = proje_kok_yolu or "."

    def mimari_ihlalleri_tespit_et(
        self,
        proje_yolu: str = None
    ) -> List[MimariIhlal]:
        """
        Projede mimari ihlalleri tespit eder.
        
        Args:
            proje_yolu: Taranacak proje yolu
            
        Returns:
            Mimari ihlal listesi
        """
        if proje_yolu is None:
            proje_yolu = self.proje_kok_yolu
        
        ihlaller = []
        proje = Path(proje_yolu)
        
        for py_dosya in proje.rglob('*.py'):
            if '__pycache__' in py_dosya.parts:
                continue
            
            kaynak_katman = self.katman_belirle(str(py_dosya))
            importlar = self.import_bagimlilikları_analiz_et(str(py_dosya))
            
            for imp in importlar:
                hedef_katman = self._modul_katmani_belirle(imp.modul_adi)
                
                ihlal = self._ihlal_kontrol_et(
                    kaynak_katman, hedef_katman,
                    str(py_dosya), imp.modul_adi
                )
                
                if ihlal:
                    ihlaller.append(ihlal)
        
        return ihlaller
    
    def katman_belirle(self, dosya_yolu: str) -> KatmanTuru:
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
        elif 'cekirdek' in yol_parcalari or 'ortak' in yol_parcalari:
            return KatmanTuru.ORTAK
        else:
            return KatmanTuru.BILINMEYEN

    def import_bagimlilikları_analiz_et(
        self,
        dosya_yolu: str
    ) -> List[ImportBilgisi]:
        """
        Dosyadaki import ifadelerini analiz eder.
        
        Args:
            dosya_yolu: Analiz edilecek dosya
            
        Returns:
            Import bilgileri listesi
        """
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
            agac = ast.parse(icerik)
        except Exception:
            return []
        
        importlar = []
        
        for node in ast.walk(agac):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    importlar.append(ImportBilgisi(
                        modul_adi=alias.name,
                        kaynak_dosya=dosya_yolu,
                        satir_no=node.lineno
                    ))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    importlar.append(ImportBilgisi(
                        modul_adi=node.module,
                        kaynak_dosya=dosya_yolu,
                        satir_no=node.lineno
                    ))
        
        return importlar
    
    def _modul_katmani_belirle(self, modul_adi: str) -> KatmanTuru:
        """Modül adından katman türünü belirler"""
        if 'arayuz' in modul_adi or 'ui' in modul_adi:
            return KatmanTuru.UI
        elif 'servis' in modul_adi or 'service' in modul_adi:
            return KatmanTuru.SERVIS
        elif 'depo' in modul_adi or 'repository' in modul_adi:
            return KatmanTuru.REPOSITORY
        elif 'veritabani' in modul_adi or 'database' in modul_adi:
            return KatmanTuru.DATABASE
        elif 'cekirdek' in modul_adi or 'ortak' in modul_adi:
            return KatmanTuru.ORTAK
        else:
            return KatmanTuru.BILINMEYEN

    def _ihlal_kontrol_et(
        self,
        kaynak_katman: KatmanTuru,
        hedef_katman: KatmanTuru,
        kaynak_dosya: str,
        hedef_modul: str
    ) -> MimariIhlal:
        """
        İki katman arasında mimari ihlal olup olmadığını kontrol eder.
        
        Returns:
            İhlal varsa MimariIhlal, yoksa None
        """
        # UI katmanı repository veya database import edemez
        if kaynak_katman == KatmanTuru.UI:
            if hedef_katman in [KatmanTuru.REPOSITORY, KatmanTuru.DATABASE]:
                return MimariIhlal(
                    kaynak_dosya=kaynak_dosya,
                    hedef_dosya=hedef_modul,
                    ihlal_turu="UI_KATMAN_IHLALI",
                    cozum_onerisi="UI katmanı servis katmanını kullanmalı"
                )
        
        # Servis katmanı UI import edemez
        if kaynak_katman == KatmanTuru.SERVIS:
            if hedef_katman == KatmanTuru.UI:
                return MimariIhlal(
                    kaynak_dosya=kaynak_dosya,
                    hedef_dosya=hedef_modul,
                    ihlal_turu="SERVIS_KATMAN_IHLALI",
                    cozum_onerisi="Servis katmanı UI'dan bağımsız olmalı"
                )
        
        # Repository katmanı servis veya UI import edemez
        if kaynak_katman == KatmanTuru.REPOSITORY:
            if hedef_katman in [KatmanTuru.SERVIS, KatmanTuru.UI]:
                return MimariIhlal(
                    kaynak_dosya=kaynak_dosya,
                    hedef_dosya=hedef_modul,
                    ihlal_turu="REPOSITORY_KATMAN_IHLALI",
                    cozum_onerisi="Repository sadece database erişimi yapmalı"
                )
        
        return None
