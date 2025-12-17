# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.refactoring_altyapi.import_guncelleme_sistemi
# Description: Import yapısını analiz eden ve güncelleyen sistem
# Changelog:
# - İlk versiyon: ImportGuncellemeSistemi sınıfı oluşturuldu

"""
Import Güncelleme Sistemi

Refactoring sırasında import yapısını analiz eder ve günceller:
- Bağımlılık analizi
- Döngüsel import tespiti
- Import güncelleme algoritmaları
- Mimari uyumluluk kontrolü
"""

import ast
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import re


class ImportTuru(Enum):
    """Import türleri"""
    DIRECT = "direct"          # import module
    FROM = "from"              # from module import item
    RELATIVE = "relative"      # from .module import item
    ABSOLUTE = "absolute"      # from package.module import item


class BagimlilikTuru(Enum):
    """Bağımlılık türleri"""
    INTERNAL = "internal"      # Proje içi
    EXTERNAL = "external"      # Harici kütüphane
    STANDARD = "standard"      # Python standart kütüphanesi


@dataclass
class ImportBilgisi:
    """Import bilgisi"""
    dosya_yolu: str
    satir_no: int
    import_turu: ImportTuru
    modul_adi: str
    import_edilen: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    bagimlilik_turu: BagimlilikTuru = BagimlilikTuru.INTERNAL


@dataclass
class BagimlilikGrafi:
    """Bağımlılık grafı"""
    dugumler: Set[str] = field(default_factory=set)
    kenarlar: Dict[str, Set[str]] = field(default_factory=dict)
    dongular: List[List[str]] = field(default_factory=list)


@dataclass
class ImportGuncellemePlani:
    """Import güncelleme planı"""
    eklenecek_importlar: Dict[str, List[ImportBilgisi]] = field(default_factory=dict)
    silinecek_importlar: Dict[str, List[ImportBilgisi]] = field(default_factory=dict)
    guncellenecek_importlar: Dict[str, List[Tuple[ImportBilgisi, ImportBilgisi]]] = field(default_factory=dict)
    yeniden_organize_edilecek_dosyalar: List[str] = field(default_factory=list)


class ImportGuncellemeSistemi:
    """
    Import Güncelleme Sistemi
    
    Refactoring sırasında import yapısını yönetir:
    - Mevcut import'ları analiz eder
    - Bağımlılık grafı oluşturur
    - Döngüsel import'ları tespit eder
    - Import güncelleme planı oluşturur
    - Güncelleme planını uygular
    """
    
    def __init__(
        self,
        proje_yolu: str,
        proje_paketi: str = "sontechsp",
        log_seviyesi: int = logging.INFO
    ):
        """
        Args:
            proje_yolu: Proje ana yolu
            proje_paketi: Ana proje paketi adı
            log_seviyesi: Log seviyesi
        """
        self.proje_yolu = Path(proje_yolu)
        self.proje_paketi = proje_paketi
        
        # Logger kurulumu
        self.logger = self._logger_kurulumu(log_seviyesi)
        
        # Analiz sonuçları
        self.import_bilgileri: Dict[str, List[ImportBilgisi]] = {}
        self.bagimlilik_grafi = BagimlilikGrafi()
        
        # Python standart kütüphaneleri (temel liste)
        self.standart_kutuphaneler = {
            'os', 'sys', 'json', 're', 'ast', 'logging', 'datetime',
            'pathlib', 'typing', 'dataclasses', 'enum', 'collections',
            'itertools', 'functools', 'operator', 'math', 'random',
            'string', 'io', 'subprocess', 'threading', 'multiprocessing',
            'sqlite3', 'unittest', 'pytest', 'hypothesis'
        }
        
        self.logger.info(f"ImportGuncellemeSistemi başlatıldı: {self.proje_yolu}")
    
    def _logger_kurulumu(self, log_seviyesi: int) -> logging.Logger:
        """Logger kurulumu yapar"""
        logger = logging.getLogger(f"ImportGuncellemeSistemi_{id(self)}")
        logger.setLevel(log_seviyesi)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def proje_importlarini_analiz_et(self) -> Dict[str, List[ImportBilgisi]]:
        """
        Proje genelinde import'ları analiz eder.
        
        Returns:
            Dosya bazında import bilgileri
        """
        self.logger.info("Proje import'ları analiz ediliyor...")
        
        self.import_bilgileri.clear()
        
        # Python dosyalarını bul
        python_dosyalari = list(self.proje_yolu.rglob('*.py'))
        
        for dosya in python_dosyalari:
            # Test dosyalarını ve __pycache__ klasörünü atla
            if '__pycache__' in str(dosya) or dosya.name.startswith('.'):
                continue
            
            dosya_importlari = self._dosya_importlarini_analiz_et(dosya)
            if dosya_importlari:
                self.import_bilgileri[str(dosya)] = dosya_importlari
        
        self.logger.info(f"{len(self.import_bilgileri)} dosya analiz edildi")
        return self.import_bilgileri
    
    def _dosya_importlarini_analiz_et(self, dosya_yolu: Path) -> List[ImportBilgisi]:
        """
        Tek bir dosyanın import'larını analiz eder.
        
        Args:
            dosya_yolu: Dosya yolu
            
        Returns:
            Import bilgileri listesi
        """
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            tree = ast.parse(icerik)
            importlar = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_bilgisi = ImportBilgisi(
                            dosya_yolu=str(dosya_yolu),
                            satir_no=node.lineno,
                            import_turu=ImportTuru.DIRECT,
                            modul_adi=alias.name,
                            alias=alias.asname,
                            bagimlilik_turu=self._bagimlilik_turunu_belirle(alias.name)
                        )
                        importlar.append(import_bilgisi)
                
                elif isinstance(node, ast.ImportFrom):
                    modul_adi = node.module or ""
                    import_turu = ImportTuru.RELATIVE if node.level > 0 else ImportTuru.FROM
                    
                    if node.level > 0:
                        # Relative import
                        modul_adi = "." * node.level + (modul_adi if modul_adi else "")
                    
                    import_edilen = []
                    for alias in node.names:
                        import_edilen.append(alias.name)
                    
                    import_bilgisi = ImportBilgisi(
                        dosya_yolu=str(dosya_yolu),
                        satir_no=node.lineno,
                        import_turu=import_turu,
                        modul_adi=modul_adi,
                        import_edilen=import_edilen,
                        bagimlilik_turu=self._bagimlilik_turunu_belirle(modul_adi)
                    )
                    importlar.append(import_bilgisi)
            
            return importlar
            
        except Exception as e:
            self.logger.warning(f"Dosya import analiz hatası {dosya_yolu}: {e}")
            return []
    
    def _bagimlilik_turunu_belirle(self, modul_adi: str) -> BagimlilikTuru:
        """Modülün bağımlılık türünü belirler"""
        if not modul_adi:
            return BagimlilikTuru.INTERNAL
        
        # Relative import
        if modul_adi.startswith('.'):
            return BagimlilikTuru.INTERNAL
        
        # Proje paketi
        if modul_adi.startswith(self.proje_paketi):
            return BagimlilikTuru.INTERNAL
        
        # Standart kütüphane
        ana_modul = modul_adi.split('.')[0]
        if ana_modul in self.standart_kutuphaneler:
            return BagimlilikTuru.STANDARD
        
        # Harici kütüphane
        return BagimlilikTuru.EXTERNAL
    
    def bagimlilik_grafi_olustur(self) -> BagimlilikGrafi:
        """
        Bağımlılık grafı oluşturur.
        
        Returns:
            Bağımlılık grafı
        """
        self.logger.info("Bağımlılık grafı oluşturuluyor...")
        
        self.bagimlilik_grafi = BagimlilikGrafi()
        
        # Tüm dosyaları düğüm olarak ekle
        for dosya_yolu in self.import_bilgileri.keys():
            modul_adi = self._dosya_yolundan_modul_adi_cikart(dosya_yolu)
            self.bagimlilik_grafi.dugumler.add(modul_adi)
            self.bagimlilik_grafi.kenarlar[modul_adi] = set()
        
        # Import'lara göre kenarları ekle
        for dosya_yolu, importlar in self.import_bilgileri.items():
            kaynak_modul = self._dosya_yolundan_modul_adi_cikart(dosya_yolu)
            
            for import_bilgisi in importlar:
                if import_bilgisi.bagimlilik_turu == BagimlilikTuru.INTERNAL:
                    hedef_modul = self._import_modul_adini_normalize_et(
                        import_bilgisi.modul_adi, dosya_yolu
                    )
                    
                    if hedef_modul and hedef_modul in self.bagimlilik_grafi.dugumler:
                        self.bagimlilik_grafi.kenarlar[kaynak_modul].add(hedef_modul)
        
        return self.bagimlilik_grafi
    
    def _dosya_yolundan_modul_adi_cikart(self, dosya_yolu: str) -> str:
        """Dosya yolundan modül adı çıkarır"""
        yol = Path(dosya_yolu)
        
        # Proje yoluna göre relative yol
        try:
            relative_yol = yol.relative_to(self.proje_yolu)
        except ValueError:
            relative_yol = yol
        
        # .py uzantısını kaldır
        if relative_yol.suffix == '.py':
            relative_yol = relative_yol.with_suffix('')
        
        # Path'i modül adına çevir
        modul_adi = str(relative_yol).replace(os.sep, '.')
        
        return modul_adi
    
    def _import_modul_adini_normalize_et(self, modul_adi: str, kaynak_dosya: str) -> Optional[str]:
        """Import modül adını normalize eder"""
        if not modul_adi:
            return None
        
        # Relative import'ları çözümle
        if modul_adi.startswith('.'):
            kaynak_modul = self._dosya_yolundan_modul_adi_cikart(kaynak_dosya)
            kaynak_paketler = kaynak_modul.split('.')
            
            # Nokta sayısına göre yukarı çık
            nokta_sayisi = len(modul_adi) - len(modul_adi.lstrip('.'))
            
            if nokta_sayisi >= len(kaynak_paketler):
                return None
            
            hedef_paketler = kaynak_paketler[:-nokta_sayisi]
            
            # Kalan modül adını ekle
            kalan_modul = modul_adi.lstrip('.')
            if kalan_modul:
                hedef_paketler.append(kalan_modul)
            
            return '.'.join(hedef_paketler)
        
        # Absolute import
        return modul_adi
    
    def donguleri_tespit_et(self) -> List[List[str]]:
        """
        Döngüsel import'ları tespit eder.
        
        Returns:
            Döngü listesi
        """
        self.logger.info("Döngüsel import'lar tespit ediliyor...")
        
        dongular = []
        ziyaret_edilenler = set()
        yigit = []
        yigit_seti = set()
        
        def dfs(dugum: str):
            if dugum in yigit_seti:
                # Döngü bulundu
                dongu_baslangici = yigit.index(dugum)
                dongu = yigit[dongu_baslangici:] + [dugum]
                dongular.append(dongu)
                return
            
            if dugum in ziyaret_edilenler:
                return
            
            ziyaret_edilenler.add(dugum)
            yigit.append(dugum)
            yigit_seti.add(dugum)
            
            for komsu in self.bagimlilik_grafi.kenarlar.get(dugum, set()):
                dfs(komsu)
            
            yigit.pop()
            yigit_seti.remove(dugum)
        
        # Tüm düğümler için DFS çalıştır
        for dugum in self.bagimlilik_grafi.dugumler:
            if dugum not in ziyaret_edilenler:
                dfs(dugum)
        
        self.bagimlilik_grafi.dongular = dongular
        
        if dongular:
            self.logger.warning(f"{len(dongular)} döngüsel import tespit edildi")
        else:
            self.logger.info("Döngüsel import bulunamadı")
        
        return dongular
    
    def refactoring_sonrasi_import_guncelleme_plani_olustur(
        self,
        dosya_degisiklikleri: Dict[str, str],  # eski_yol -> yeni_yol
        yeni_dosyalar: List[str] = None,
        silinen_dosyalar: List[str] = None
    ) -> ImportGuncellemePlani:
        """
        Refactoring sonrası import güncelleme planı oluşturur.
        
        Args:
            dosya_degisiklikleri: Dosya yolu değişiklikleri
            yeni_dosyalar: Yeni oluşturulan dosyalar
            silinen_dosyalar: Silinen dosyalar
            
        Returns:
            Import güncelleme planı
        """
        self.logger.info("Import güncelleme planı oluşturuluyor...")
        
        plan = ImportGuncellemePlani()
        
        if yeni_dosyalar is None:
            yeni_dosyalar = []
        if silinen_dosyalar is None:
            silinen_dosyalar = []
        
        # Dosya yolu değişiklikleri için import'ları güncelle
        for eski_yol, yeni_yol in dosya_degisiklikleri.items():
            eski_modul = self._dosya_yolundan_modul_adi_cikart(eski_yol)
            yeni_modul = self._dosya_yolundan_modul_adi_cikart(yeni_yol)
            
            # Bu modülü import eden dosyaları bul ve güncelle
            for dosya_yolu, importlar in self.import_bilgileri.items():
                guncellenecekler = []
                
                for import_bilgisi in importlar:
                    if self._import_etkileniyor_mu(import_bilgisi, eski_modul):
                        yeni_import = self._import_guncelle(import_bilgisi, eski_modul, yeni_modul)
                        guncellenecekler.append((import_bilgisi, yeni_import))
                
                if guncellenecekler:
                    plan.guncellenecek_importlar[dosya_yolu] = guncellenecekler
        
        # Silinen dosyalar için import'ları kaldır
        for silinen_dosya in silinen_dosyalar:
            silinen_modul = self._dosya_yolundan_modul_adi_cikart(silinen_dosya)
            
            for dosya_yolu, importlar in self.import_bilgileri.items():
                silinecekler = []
                
                for import_bilgisi in importlar:
                    if self._import_etkileniyor_mu(import_bilgisi, silinen_modul):
                        silinecekler.append(import_bilgisi)
                
                if silinecekler:
                    plan.silinecek_importlar[dosya_yolu] = silinecekler
        
        # Yeniden organize edilecek dosyaları belirle
        etkilenen_dosyalar = set()
        etkilenen_dosyalar.update(plan.guncellenecek_importlar.keys())
        etkilenen_dosyalar.update(plan.silinecek_importlar.keys())
        
        plan.yeniden_organize_edilecek_dosyalar = list(etkilenen_dosyalar)
        
        return plan
    
    def _import_etkileniyor_mu(self, import_bilgisi: ImportBilgisi, hedef_modul: str) -> bool:
        """Import'un belirli bir modül değişikliğinden etkilenip etkilenmediğini kontrol eder"""
        if import_bilgisi.bagimlilik_turu != BagimlilikTuru.INTERNAL:
            return False
        
        # Normalize edilmiş modül adını al
        normalize_modul = self._import_modul_adini_normalize_et(
            import_bilgisi.modul_adi, import_bilgisi.dosya_yolu
        )
        
        if not normalize_modul:
            return False
        
        # Tam eşleşme veya alt modül eşleşmesi
        return (normalize_modul == hedef_modul or 
                normalize_modul.startswith(hedef_modul + '.') or
                hedef_modul.startswith(normalize_modul + '.'))
    
    def _import_guncelle(
        self,
        import_bilgisi: ImportBilgisi,
        eski_modul: str,
        yeni_modul: str
    ) -> ImportBilgisi:
        """Import bilgisini günceller"""
        yeni_import = ImportBilgisi(
            dosya_yolu=import_bilgisi.dosya_yolu,
            satir_no=import_bilgisi.satir_no,
            import_turu=import_bilgisi.import_turu,
            modul_adi=import_bilgisi.modul_adi.replace(eski_modul, yeni_modul),
            import_edilen=import_bilgisi.import_edilen.copy(),
            alias=import_bilgisi.alias,
            bagimlilik_turu=import_bilgisi.bagimlilik_turu
        )
        
        return yeni_import
    
    def import_guncelleme_planini_uygula(self, plan: ImportGuncellemePlani) -> bool:
        """
        Import güncelleme planını uygular.
        
        Args:
            plan: Import güncelleme planı
            
        Returns:
            Başarı durumu
        """
        self.logger.info("Import güncelleme planı uygulanıyor...")
        
        try:
            # Her dosya için güncellemeleri uygula
            for dosya_yolu in plan.yeniden_organize_edilecek_dosyalar:
                self._dosya_importlarini_guncelle(dosya_yolu, plan)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Import güncelleme planı uygulama hatası: {e}")
            return False
    
    def _dosya_importlarini_guncelle(self, dosya_yolu: str, plan: ImportGuncellemePlani):
        """Dosyanın import'larını günceller"""
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            satirlar = icerik.split('\n')
            
            # Silinecek import'ları işaretle
            silinecek_satirlar = set()
            if dosya_yolu in plan.silinecek_importlar:
                for import_bilgisi in plan.silinecek_importlar[dosya_yolu]:
                    silinecek_satirlar.add(import_bilgisi.satir_no - 1)  # 0-indexed
            
            # Güncellenecek import'ları uygula
            if dosya_yolu in plan.guncellenecek_importlar:
                for eski_import, yeni_import in plan.guncellenecek_importlar[dosya_yolu]:
                    satir_index = eski_import.satir_no - 1
                    if satir_index < len(satirlar):
                        yeni_satir = self._import_satirini_olustur(yeni_import)
                        satirlar[satir_index] = yeni_satir
            
            # Silinecek satırları kaldır
            yeni_satirlar = []
            for i, satir in enumerate(satirlar):
                if i not in silinecek_satirlar:
                    yeni_satirlar.append(satir)
            
            # Import'ları yeniden organize et
            yeni_satirlar = self._importlari_yeniden_organize_et(yeni_satirlar)
            
            # Dosyayı güncelle
            yeni_icerik = '\n'.join(yeni_satirlar)
            with open(dosya_yolu, 'w', encoding='utf-8') as f:
                f.write(yeni_icerik)
            
            self.logger.info(f"Import'lar güncellendi: {dosya_yolu}")
            
        except Exception as e:
            self.logger.error(f"Dosya import güncelleme hatası {dosya_yolu}: {e}")
    
    def _import_satirini_olustur(self, import_bilgisi: ImportBilgisi) -> str:
        """Import bilgisinden import satırı oluşturur"""
        if import_bilgisi.import_turu == ImportTuru.DIRECT:
            satir = f"import {import_bilgisi.modul_adi}"
            if import_bilgisi.alias:
                satir += f" as {import_bilgisi.alias}"
        else:
            satir = f"from {import_bilgisi.modul_adi} import "
            satir += ", ".join(import_bilgisi.import_edilen)
        
        return satir
    
    def _importlari_yeniden_organize_et(self, satirlar: List[str]) -> List[str]:
        """Import'ları yeniden organize eder"""
        # Import satırlarını ve diğer satırları ayır
        import_satirlari = []
        diger_satirlar = []
        import_bitti = False
        
        for satir in satirlar:
            satir_temiz = satir.strip()
            
            if not import_bitti and (
                satir_temiz.startswith('import ') or 
                satir_temiz.startswith('from ')
            ):
                import_satirlari.append(satir)
            else:
                if satir_temiz and not satir_temiz.startswith('#'):
                    import_bitti = True
                diger_satirlar.append(satir)
        
        # Import'ları sırala: standart -> harici -> internal
        standart_importlar = []
        harici_importlar = []
        internal_importlar = []
        
        for satir in import_satirlari:
            satir_temiz = satir.strip()
            if not satir_temiz:
                continue
            
            # Modül adını çıkar
            if satir_temiz.startswith('import '):
                modul = satir_temiz[7:].split()[0]
            elif satir_temiz.startswith('from '):
                modul = satir_temiz[5:].split()[0]
            else:
                continue
            
            bagimlilik_turu = self._bagimlilik_turunu_belirle(modul)
            
            if bagimlilik_turu == BagimlilikTuru.STANDARD:
                standart_importlar.append(satir)
            elif bagimlilik_turu == BagimlilikTuru.EXTERNAL:
                harici_importlar.append(satir)
            else:
                internal_importlar.append(satir)
        
        # Sırala
        standart_importlar.sort()
        harici_importlar.sort()
        internal_importlar.sort()
        
        # Birleştir
        organize_importlar = []
        
        if standart_importlar:
            organize_importlar.extend(standart_importlar)
            organize_importlar.append("")  # Boş satır
        
        if harici_importlar:
            organize_importlar.extend(harici_importlar)
            organize_importlar.append("")  # Boş satır
        
        if internal_importlar:
            organize_importlar.extend(internal_importlar)
            organize_importlar.append("")  # Boş satır
        
        # Son boş satırı kaldır
        if organize_importlar and organize_importlar[-1] == "":
            organize_importlar.pop()
        
        return organize_importlar + diger_satirlar
    
    def import_analiz_raporu_olustur(self) -> Dict[str, any]:
        """
        Import analiz raporu oluşturur.
        
        Returns:
            Import analiz raporu
        """
        toplam_import = sum(len(importlar) for importlar in self.import_bilgileri.values())
        
        # Bağımlılık türlerine göre dağılım
        bagimlilik_dagilimi = {
            'internal': 0,
            'external': 0,
            'standard': 0
        }
        
        # Import türlerine göre dağılım
        import_turu_dagilimi = {
            'direct': 0,
            'from': 0,
            'relative': 0
        }
        
        for importlar in self.import_bilgileri.values():
            for import_bilgisi in importlar:
                bagimlilik_dagilimi[import_bilgisi.bagimlilik_turu.value] += 1
                import_turu_dagilimi[import_bilgisi.import_turu.value] += 1
        
        rapor = {
            'toplam_dosya': len(self.import_bilgileri),
            'toplam_import': toplam_import,
            'ortalama_import_per_dosya': toplam_import / len(self.import_bilgileri) if self.import_bilgileri else 0,
            'bagimlilik_dagilimi': bagimlilik_dagilimi,
            'import_turu_dagilimi': import_turu_dagilimi,
            'dongular': {
                'sayisi': len(self.bagimlilik_grafi.dongular),
                'detaylar': self.bagimlilik_grafi.dongular
            },
            'en_cok_import_eden_dosyalar': self._en_cok_import_eden_dosyalari_bul(),
            'en_cok_import_edilen_moduller': self._en_cok_import_edilen_modulleri_bul()
        }
        
        return rapor
    
    def _en_cok_import_eden_dosyalari_bul(self, limit: int = 5) -> List[Tuple[str, int]]:
        """En çok import eden dosyaları bulur"""
        dosya_import_sayilari = [
            (dosya, len(importlar))
            for dosya, importlar in self.import_bilgileri.items()
        ]
        
        dosya_import_sayilari.sort(key=lambda x: x[1], reverse=True)
        return dosya_import_sayilari[:limit]
    
    def _en_cok_import_edilen_modulleri_bul(self, limit: int = 5) -> List[Tuple[str, int]]:
        """En çok import edilen modülleri bulur"""
        modul_sayilari = {}
        
        for importlar in self.import_bilgileri.values():
            for import_bilgisi in importlar:
                if import_bilgisi.bagimlilik_turu == BagimlilikTuru.INTERNAL:
                    modul = import_bilgisi.modul_adi
                    modul_sayilari[modul] = modul_sayilari.get(modul, 0) + 1
        
        modul_listesi = list(modul_sayilari.items())
        modul_listesi.sort(key=lambda x: x[1], reverse=True)
        
        return modul_listesi[:limit]