# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kod_kalitesi.analizorler.kod_tekrari_analizoru
# Description: Kod tekrarı tespiti ve benzerlik analizi
# Changelog:
# - İlk versiyon: KodTekrariAnalizoru sınıfı oluşturuldu

"""
Kod Tekrarı Analizörü

Kod tabanındaki benzer kod bloklarını tespit eder ve
ortak modül önerileri üretir.
"""

import ast
import hashlib
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class KodBlogu:
    """Kod bloğu bilgisi"""
    dosya_yolu: str
    baslangic_satir: int
    bitis_satir: int
    icerik: str
    hash_degeri: str
    fonksiyon_adi: str = ""


@dataclass
class BenzerlikRaporu:
    """Benzerlik raporu"""
    blok1: KodBlogu
    blok2: KodBlogu
    benzerlik_orani: float
    ortak_modul_onerisi: str


@dataclass
class OrtakModulOnerisi:
    """Ortak modül önerisi"""
    modul_adi: str
    modul_yolu: str
    benzer_bloklar: List[KodBlogu]
    ortak_kod: str
    etkilenen_dosyalar: Set[str]


class KodTekrariAnalizoru:
    """
    Kod tekrarı analizi yapan sınıf.
    
    Benzer kod bloklarını tespit eder ve ortak modül
    önerileri üretir.
    """
    
    VARSAYILAN_ESIK = 0.85  # %85 benzerlik
    MIN_SATIR_SAYISI = 5    # Minimum 5 satır
    
    def __init__(
        self, 
        benzerlik_esigi: float = VARSAYILAN_ESIK,
        min_satir: int = MIN_SATIR_SAYISI
    ):
        """
        Args:
            benzerlik_esigi: Benzerlik eşik değeri (0.0-1.0)
            min_satir: Minimum satır sayısı
        """
        self.benzerlik_esigi = benzerlik_esigi
        self.min_satir = min_satir
        self.kod_bloklari: List[KodBlogu] = []
    
    def kod_tekrarlarini_tara(
        self,
        klasor_yolu: str,
        hariç_tutulacaklar: List[str] = None
    ) -> List[BenzerlikRaporu]:
        """
        Klasördeki kod tekrarlarını tarar.
        
        Args:
            klasor_yolu: Taranacak klasör
            hariç_tutulacaklar: Hariç tutulacak klasörler
            
        Returns:
            Benzerlik raporları listesi
        """
        if hariç_tutulacaklar is None:
            hariç_tutulacaklar = [
                '__pycache__', '.git', '.pytest_cache',
                'venv', 'env', '.hypothesis', 'tests'
            ]
        
        # Kod bloklarını topla
        self.kod_bloklari = []
        klasor = Path(klasor_yolu)
        
        for py_dosya in klasor.rglob('*.py'):
            if any(ht in py_dosya.parts for ht in hariç_tutulacaklar):
                continue
            
            bloklar = self._dosyadan_blok_cikar(str(py_dosya))
            self.kod_bloklari.extend(bloklar)
        
        # Benzerlikleri tespit et
        return self._benzerlikleri_bul()

    def _dosyadan_blok_cikar(self, dosya_yolu: str) -> List[KodBlogu]:
        """
        Dosyadan fonksiyon bloklarını çıkarır.
        
        Args:
            dosya_yolu: Python dosya yolu
            
        Returns:
            Kod blokları listesi
        """
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            agac = ast.parse(icerik)
            bloklar = []
            
            for node in ast.walk(agac):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    blok = self._fonksiyon_blogu_olustur(
                        dosya_yolu, node, icerik
                    )
                    if blok and self._blok_gecerli_mi(blok):
                        bloklar.append(blok)
            
            return bloklar
        except Exception:
            return []
    
    def _fonksiyon_blogu_olustur(
        self,
        dosya_yolu: str,
        node: ast.FunctionDef,
        icerik: str
    ) -> KodBlogu:
        """Fonksiyon düğümünden kod bloğu oluşturur."""
        satirlar = icerik.split('\n')
        baslangic = node.lineno - 1
        bitis = node.end_lineno
        
        blok_icerik = '\n'.join(satirlar[baslangic:bitis])
        
        # Normalize edilmiş içerik (boşluklar ve yorumlar temizlenir)
        normalize_icerik = self._normalize_et(blok_icerik)
        hash_degeri = hashlib.md5(
            normalize_icerik.encode()
        ).hexdigest()
        
        return KodBlogu(
            dosya_yolu=dosya_yolu,
            baslangic_satir=node.lineno,
            bitis_satir=node.end_lineno,
            icerik=blok_icerik,
            hash_degeri=hash_degeri,
            fonksiyon_adi=node.name
        )
    
    def _normalize_et(self, kod: str) -> str:
        """
        Kodu normalize eder (boşluklar, yorumlar temizlenir).
        
        Args:
            kod: Ham kod
            
        Returns:
            Normalize edilmiş kod
        """
        satirlar = []
        for satir in kod.split('\n'):
            temiz = satir.strip()
            # Yorumları ve boş satırları atla
            if temiz and not temiz.startswith('#'):
                satirlar.append(temiz)
        return '\n'.join(satirlar)
    
    def _blok_gecerli_mi(self, blok: KodBlogu) -> bool:
        """Bloğun analiz için geçerli olup olmadığını kontrol eder."""
        satir_sayisi = blok.bitis_satir - blok.baslangic_satir + 1
        return satir_sayisi >= self.min_satir

    def _benzerlikleri_bul(self) -> List[BenzerlikRaporu]:
        """
        Kod blokları arasındaki benzerlikleri bulur.
        
        Returns:
            Benzerlik raporları
        """
        raporlar = []
        islenmis_ciftler: Set[Tuple[str, str]] = set()
        
        for i, blok1 in enumerate(self.kod_bloklari):
            for blok2 in self.kod_bloklari[i+1:]:
                # Aynı dosyadaki fonksiyonları atla
                if blok1.dosya_yolu == blok2.dosya_yolu:
                    continue
                
                # Daha önce işlenmiş mi?
                cift = tuple(sorted([blok1.hash_degeri, blok2.hash_degeri]))
                if cift in islenmis_ciftler:
                    continue
                
                benzerlik = self._benzerlik_hesapla(blok1, blok2)
                
                if benzerlik >= self.benzerlik_esigi:
                    islenmis_ciftler.add(cift)
                    rapor = BenzerlikRaporu(
                        blok1=blok1,
                        blok2=blok2,
                        benzerlik_orani=benzerlik,
                        ortak_modul_onerisi=self._modul_adi_olustur(blok1)
                    )
                    raporlar.append(rapor)
        
        return raporlar
    
    def _benzerlik_hesapla(self, blok1: KodBlogu, blok2: KodBlogu) -> float:
        """
        İki kod bloğu arasındaki benzerliği hesaplar.
        
        Args:
            blok1: İlk kod bloğu
            blok2: İkinci kod bloğu
            
        Returns:
            Benzerlik oranı (0.0-1.0)
        """
        # Hash eşleşmesi varsa %100 benzer
        if blok1.hash_degeri == blok2.hash_degeri:
            return 1.0
        
        # Sequence matcher ile benzerlik hesapla
        normalize1 = self._normalize_et(blok1.icerik)
        normalize2 = self._normalize_et(blok2.icerik)
        
        matcher = SequenceMatcher(None, normalize1, normalize2)
        return matcher.ratio()
    
    def _modul_adi_olustur(self, blok: KodBlogu) -> str:
        """
        Ortak modül için isim önerisi oluşturur.
        
        Args:
            blok: Kod bloğu
            
        Returns:
            Modül adı önerisi
        """
        fonk_adi = blok.fonksiyon_adi
        if '_' in fonk_adi:
            # İlk kelimeyi al
            ilk_kelime = fonk_adi.split('_')[0]
            return f"{ilk_kelime}_yardimcilari"
        return "ortak_yardimcilar"

    def ortak_modul_onerileri_olustur(
        self,
        benzerlik_raporlari: List[BenzerlikRaporu]
    ) -> List[OrtakModulOnerisi]:
        """
        Benzerlik raporlarından ortak modül önerileri oluşturur.
        
        Args:
            benzerlik_raporlari: Benzerlik raporları
            
        Returns:
            Ortak modül önerileri
        """
        # Benzerlikleri modül adına göre grupla
        modul_gruplari: Dict[str, List[BenzerlikRaporu]] = {}
        
        for rapor in benzerlik_raporlari:
            modul_adi = rapor.ortak_modul_onerisi
            if modul_adi not in modul_gruplari:
                modul_gruplari[modul_adi] = []
            modul_gruplari[modul_adi].append(rapor)
        
        # Her grup için öneri oluştur
        oneriler = []
        for modul_adi, raporlar in modul_gruplari.items():
            oneri = self._grup_icin_oneri_olustur(modul_adi, raporlar)
            oneriler.append(oneri)
        
        return oneriler
    
    def _grup_icin_oneri_olustur(
        self,
        modul_adi: str,
        raporlar: List[BenzerlikRaporu]
    ) -> OrtakModulOnerisi:
        """Bir grup benzerlik raporu için ortak modül önerisi oluşturur."""
        benzer_bloklar = []
        etkilenen_dosyalar = set()
        
        for rapor in raporlar:
            benzer_bloklar.append(rapor.blok1)
            benzer_bloklar.append(rapor.blok2)
            etkilenen_dosyalar.add(rapor.blok1.dosya_yolu)
            etkilenen_dosyalar.add(rapor.blok2.dosya_yolu)
        
        # En yaygın kodu ortak kod olarak seç
        ortak_kod = benzer_bloklar[0].icerik if benzer_bloklar else ""
        
        # Modül yolu önerisi
        modul_yolu = f"uygulama/moduller/ortak/{modul_adi}.py"
        
        return OrtakModulOnerisi(
            modul_adi=modul_adi,
            modul_yolu=modul_yolu,
            benzer_bloklar=benzer_bloklar,
            ortak_kod=ortak_kod,
            etkilenen_dosyalar=etkilenen_dosyalar
        )
