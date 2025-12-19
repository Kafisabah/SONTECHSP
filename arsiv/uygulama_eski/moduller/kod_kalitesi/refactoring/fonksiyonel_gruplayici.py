# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.refactoring.fonksiyonel_gruplayici
# Description: Fonksiyonel gruplama ve isimlendirme kuralları uygulayıcıuralları uygulayıcı
# Changelog:
# - İlk versiyon: FonksiyonelGruplayici sınıfı oluşturuldu

"""
Fonksiyonel Gruplayıcı

Kod tabanındaki fonksiyonları ve sınıfları semantic analiz
ile gruplar ve uygun isimlendirme kurallarını uygular.
"""

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Tuple


class GrupTuru(Enum):
    """Fonksiyonel grup türleri"""
    DOGRULAMA = "dogrulama"
    YARDIMCILAR = "yardimcilar"
    VERI_ISLEMLERI = "veri_islemleri"
    HESAPLAMALAR = "hesaplamalar"
    VERITABANI = "veritabani"
    API = "api"
    RAPORLAMA = "raporlama"
    ANA = "ana"


@dataclass
class FonksiyonBilgisi:
    """Fonksiyon bilgisi"""
    isim: str
    satir_baslangic: int
    satir_bitis: int
    kod: str
    grup: GrupTuru = GrupTuru.ANA
    bagimliliklari: Set[str] = field(default_factory=set)
    cagrildiği_yerler: Set[str] = field(default_factory=set)


@dataclass
class SinifBilgisi:
    """Sınıf bilgisi"""
    isim: str
    satir_baslangic: int
    satir_bitis: int
    kod: str
    metotlar: List[str] = field(default_factory=list)
    bagimliliklari: Set[str] = field(default_factory=set)


@dataclass
class GruplamaSonucu:
    """Gruplama sonucu"""
    gruplar: Dict[GrupTuru, List[FonksiyonBilgisi]]
    siniflar: List[SinifBilgisi]
    onerilen_dosya_isimleri: Dict[GrupTuru, str]


class FonksiyonelGruplayici:
    """
    Fonksiyonel gruplama ve isimlendirme sistemi.
    
    Kod tabanındaki fonksiyonları semantic analiz ile gruplar,
    uygun isimlendirme kurallarını uygular ve modül tutarlılığını
    sağlar.
    """
    
    # Anahtar kelime eşlemeleri
    DOGRULAMA_ANAHTAR_KELIMELER = {
        'dogrula', 'validate', 'kontrol', 'check', 'verify',
        'test', 'assert', 'ensure', 'gecerli', 'valid'
    }
    
    VERI_ISLEMLERI_ANAHTAR_KELIMELER = {
        'isle', 'process', 'donustur', 'convert', 'transform',
        'parse', 'format', 'serialize', 'deserialize', 'yukle',
        'load', 'kaydet', 'save', 'oku', 'read', 'yaz', 'write'
    }
    
    HESAPLAMA_ANAHTAR_KELIMELER = {
        'hesapla', 'calculate', 'compute', 'topla', 'sum',
        'ort', 'average', 'mean', 'max', 'min', 'count', 'say'
    }
    
    VERITABANI_ANAHTAR_KELIMELER = {
        'ekle', 'add', 'insert', 'guncelle', 'update', 'sil',
        'delete', 'bul', 'find', 'getir', 'get', 'fetch',
        'query', 'sorgu', 'liste', 'list', 'all'
    }
    
    API_ANAHTAR_KELIMELER = {
        'api', 'endpoint', 'request', 'response', 'http',
        'get', 'post', 'put', 'delete', 'patch', 'istek', 'cevap'
    }
    
    RAPORLAMA_ANAHTAR_KELIMELER = {
        'rapor', 'report', 'export', 'print', 'generate',
        'olustur', 'create', 'pdf', 'csv', 'excel'
    }
    
    def __init__(self):
        """Gruplayıcıyı başlatır"""
        self.fonksiyonlar: List[FonksiyonBilgisi] = []
        self.siniflar: List[SinifBilgisi] = []
    
    def dosyayi_grupla(self, dosya_yolu: str) -> GruplamaSonucu:
        """
        Dosyadaki fonksiyonları ve sınıfları gruplar.
        
        Args:
            dosya_yolu: Analiz edilecek dosya yolu
            
        Returns:
            Gruplama sonucu
        """
        # Dosyayı oku
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        # AST analizi yap
        try:
            agac = ast.parse(icerik)
        except SyntaxError:
            return GruplamaSonucu(
                gruplar={},
                siniflar=[],
                onerilen_dosya_isimleri={}
            )
        
        satirlar = icerik.split('\n')
        
        # Fonksiyonları ve sınıfları analiz et
        self._fonksiyonlari_analiz_et(agac, satirlar)
        self._siniflari_analiz_et(agac, satirlar)
        
        # Fonksiyonları grupla
        gruplar = self._fonksiyonlari_grupla()
        
        # Dosya isimlerini öner
        dosya_isimleri = self._dosya_isimlerini_olustur(
            Path(dosya_yolu).stem
        )
        
        return GruplamaSonucu(
            gruplar=gruplar,
            siniflar=self.siniflar,
            onerilen_dosya_isimleri=dosya_isimleri
        )
    
    def _fonksiyonlari_analiz_et(
        self,
        agac: ast.AST,
        satirlar: List[str]
    ) -> None:
        """
        Fonksiyonları analiz eder ve bilgilerini toplar.
        
        Args:
            agac: AST ağacı
            satirlar: Dosya satırları
        """
        for node in ast.walk(agac):
            if isinstance(node, ast.FunctionDef):
                # Sınıf metodu değilse
                if not self._sinif_metodu_mu(node, agac):
                    fonksiyon = self._fonksiyon_bilgisi_olustur(
                        node, satirlar
                    )
                    self.fonksiyonlar.append(fonksiyon)
    
    def _siniflari_analiz_et(
        self,
        agac: ast.AST,
        satirlar: List[str]
    ) -> None:
        """
        Sınıfları analiz eder ve bilgilerini toplar.
        
        Args:
            agac: AST ağacı
            satirlar: Dosya satırları
        """
        for node in ast.walk(agac):
            if isinstance(node, ast.ClassDef):
                sinif = self._sinif_bilgisi_olustur(node, satirlar)
                self.siniflar.append(sinif)
    
    def _sinif_metodu_mu(
        self,
        fonksiyon_node: ast.FunctionDef,
        agac: ast.AST
    ) -> bool:
        """
        Fonksiyonun bir sınıf metodu olup olmadığını kontrol eder.
        
        Args:
            fonksiyon_node: Fonksiyon node'u
            agac: AST ağacı
            
        Returns:
            True ise sınıf metodu
        """
        for node in ast.walk(agac):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if item == fonksiyon_node:
                        return True
        return False
    
    def _fonksiyon_bilgisi_olustur(
        self,
        node: ast.FunctionDef,
        satirlar: List[str]
    ) -> FonksiyonBilgisi:
        """
        Fonksiyon bilgisi oluşturur.
        
        Args:
            node: Fonksiyon node'u
            satirlar: Dosya satırları
            
        Returns:
            Fonksiyon bilgisi
        """
        baslangic = node.lineno - 1
        bitis = node.end_lineno if node.end_lineno else baslangic + 1
        kod = '\n'.join(satirlar[baslangic:bitis])
        
        # Grup belirle
        grup = self._fonksiyon_grubu_belirle(node.name, kod)
        
        # Bağımlılıkları bul
        bagimliliklari = self._bagimlilikları_bul(node)
        
        return FonksiyonBilgisi(
            isim=node.name,
            satir_baslangic=baslangic,
            satir_bitis=bitis,
            kod=kod,
            grup=grup,
            bagimliliklari=bagimliliklari
        )
    
    def _sinif_bilgisi_olustur(
        self,
        node: ast.ClassDef,
        satirlar: List[str]
    ) -> SinifBilgisi:
        """
        Sınıf bilgisi oluşturur.
        
        Args:
            node: Sınıf node'u
            satirlar: Dosya satırları
            
        Returns:
            Sınıf bilgisi
        """
        baslangic = node.lineno - 1
        bitis = node.end_lineno if node.end_lineno else baslangic + 1
        kod = '\n'.join(satirlar[baslangic:bitis])
        
        # Metotları topla
        metotlar = [
            item.name for item in node.body
            if isinstance(item, ast.FunctionDef)
        ]
        
        # Bağımlılıkları bul
        bagimliliklari = self._bagimlilikları_bul(node)
        
        return SinifBilgisi(
            isim=node.name,
            satir_baslangic=baslangic,
            satir_bitis=bitis,
            kod=kod,
            metotlar=metotlar,
            bagimliliklari=bagimliliklari
        )
    
    def _fonksiyon_grubu_belirle(
        self,
        fonksiyon_adi: str,
        kod: str
    ) -> GrupTuru:
        """
        Fonksiyonun hangi gruba ait olduğunu belirler.
        
        Semantic analiz kullanarak fonksiyon adı ve kodunu
        inceler, uygun grubu belirler.
        
        Args:
            fonksiyon_adi: Fonksiyon adı
            kod: Fonksiyon kodu
            
        Returns:
            Grup türü
        """
        adi_kucuk = fonksiyon_adi.lower()
        kod_kucuk = kod.lower()
        
        # Doğrulama kontrolü
        if self._anahtar_kelime_var_mi(
            adi_kucuk, self.DOGRULAMA_ANAHTAR_KELIMELER
        ):
            return GrupTuru.DOGRULAMA
        
        # Veritabanı kontrolü
        if self._anahtar_kelime_var_mi(
            adi_kucuk, self.VERITABANI_ANAHTAR_KELIMELER
        ) or 'session' in kod_kucuk or 'query' in kod_kucuk:
            return GrupTuru.VERITABANI
        
        # API kontrolü
        if self._anahtar_kelime_var_mi(
            adi_kucuk, self.API_ANAHTAR_KELIMELER
        ):
            return GrupTuru.API
        
        # Raporlama kontrolü
        if self._anahtar_kelime_var_mi(
            adi_kucuk, self.RAPORLAMA_ANAHTAR_KELIMELER
        ):
            return GrupTuru.RAPORLAMA
        
        # Hesaplama kontrolü
        if self._anahtar_kelime_var_mi(
            adi_kucuk, self.HESAPLAMA_ANAHTAR_KELIMELER
        ):
            return GrupTuru.HESAPLAMALAR
        
        # Veri işlemleri kontrolü
        if self._anahtar_kelime_var_mi(
            adi_kucuk, self.VERI_ISLEMLERI_ANAHTAR_KELIMELER
        ):
            return GrupTuru.VERI_ISLEMLERI
        
        # Yardımcı fonksiyon kontrolü
        if adi_kucuk.startswith('_') and not adi_kucuk.startswith('__'):
            return GrupTuru.YARDIMCILAR
        
        # Varsayılan
        return GrupTuru.ANA
    
    def _anahtar_kelime_var_mi(
        self,
        metin: str,
        anahtar_kelimeler: Set[str]
    ) -> bool:
        """
        Metinde anahtar kelime var mı kontrol eder.
        
        Args:
            metin: Kontrol edilecek metin
            anahtar_kelimeler: Anahtar kelime seti
            
        Returns:
            True ise anahtar kelime var
        """
        return any(kelime in metin for kelime in anahtar_kelimeler)
    
    def _bagimlilikları_bul(self, node: ast.AST) -> Set[str]:
        """
        Node'un bağımlılıklarını bulur.
        
        Args:
            node: AST node'u
            
        Returns:
            Bağımlılık isimleri
        """
        bagimliliklari = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                bagimliliklari.add(child.id)
            elif isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    bagimliliklari.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        bagimliliklari.add(child.func.value.id)
        
        return bagimliliklari
    
    def _fonksiyonlari_grupla(self) -> Dict[GrupTuru, List[FonksiyonBilgisi]]:
        """
        Fonksiyonları gruplarına göre organize eder.
        
        Returns:
            Grup türüne göre fonksiyon listesi
        """
        gruplar: Dict[GrupTuru, List[FonksiyonBilgisi]] = {}
        
        for fonksiyon in self.fonksiyonlar:
            if fonksiyon.grup not in gruplar:
                gruplar[fonksiyon.grup] = []
            gruplar[fonksiyon.grup].append(fonksiyon)
        
        return gruplar
    
    def _dosya_isimlerini_olustur(
        self,
        taban_isim: str
    ) -> Dict[GrupTuru, str]:
        """
        Gruplar için uygun dosya isimleri oluşturur.
        
        İsimlendirme kuralları:
        - {taban}_dogrulama.py
        - {taban}_yardimcilar.py
        - {taban}_veri_islemleri.py
        - vb.
        
        Args:
            taban_isim: Taban dosya ismi
            
        Returns:
            Grup türüne göre dosya isimleri
        """
        dosya_isimleri = {}
        
        for grup in GrupTuru:
            if grup == GrupTuru.ANA:
                dosya_isimleri[grup] = f"{taban_isim}.py"
            else:
                dosya_isimleri[grup] = f"{taban_isim}_{grup.value}.py"
        
        return dosya_isimleri
    
    def isimlendirme_kurallari_uygula(
        self,
        dosya_adi: str
    ) -> Tuple[bool, str]:
        """
        Dosya adının isimlendirme kurallarına uygun olup olmadığını
        kontrol eder ve gerekirse düzeltir.
        
        Kurallar:
        - Küçük harf kullanımı
        - Alt çizgi ile kelime ayırma
        - Anlamlı isimler (_yardimcilari, _dogrulama, vb.)
        
        Args:
            dosya_adi: Kontrol edilecek dosya adı
            
        Returns:
            (uygun_mu, duzeltilmis_isim) tuple'ı
        """
        # .py uzantısını çıkar
        if dosya_adi.endswith('.py'):
            dosya_adi = dosya_adi[:-3]
        
        # Kuralları kontrol et
        uygun = True
        duzeltilmis = dosya_adi
        
        # Büyük harf kontrolü
        if dosya_adi != dosya_adi.lower():
            uygun = False
            duzeltilmis = dosya_adi.lower()
        
        # CamelCase'i snake_case'e çevir
        if re.search(r'[A-Z]', dosya_adi):
            uygun = False
            duzeltilmis = self._camel_to_snake(dosya_adi)
        
        # Tire yerine alt çizgi
        if '-' in duzeltilmis:
            uygun = False
            duzeltilmis = duzeltilmis.replace('-', '_')
        
        # Boşluk kontrolü
        if ' ' in duzeltilmis:
            uygun = False
            duzeltilmis = duzeltilmis.replace(' ', '_')
        
        return uygun, f"{duzeltilmis}.py"
    
    def _camel_to_snake(self, isim: str) -> str:
        """
        CamelCase'i snake_case'e çevirir.
        
        Args:
            isim: CamelCase isim
            
        Returns:
            snake_case isim
        """
        # İlk büyük harften önce alt çizgi ekle
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', isim)
        # Ardışık büyük harfler arasına alt çizgi ekle
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
