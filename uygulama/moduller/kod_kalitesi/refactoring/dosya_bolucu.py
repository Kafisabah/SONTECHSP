# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.refactoring.dosya_bolucu
# Description: Büyük dosyaları mantıklı alt dosyalara bölen sistem
# Changelog:
# - İlk versiyon: DosyaBolucu sınıfı oluşturuldu

"""
Dosya Bölücü

Büyük Python dosyalarını fonksiyonel gruplara göre
mantıklı alt dosyalara böler ve import yapısını korur.
"""

import ast
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set


class BolmeStratejisi(Enum):
    """Dosya bölme stratejileri"""
    FONKSIYONEL = "fonksiyonel"  # Fonksiyonel gruplara göre
    SINIF_BAZLI = "sinif_bazli"  # Her sınıf ayrı dosya
    BOYUT_BAZLI = "boyut_bazli"  # Eşit boyutlarda böl


@dataclass
class FonksiyonelGrup:
    """Fonksiyonel grup bilgisi"""
    isim: str
    icerik: List[str] = field(default_factory=list)
    bagimliliklari: Set[str] = field(default_factory=set)
    satirlar: List[int] = field(default_factory=list)


@dataclass
class YeniDosya:
    """Yeni oluşturulacak dosya bilgisi"""
    dosya_adi: str
    dosya_yolu: str
    icerik: str
    import_listesi: List[str] = field(default_factory=list)


class DosyaBolucu:
    """
    Dosya bölme işlemlerini yöneten sınıf.
    
    Büyük dosyaları analiz eder, fonksiyonel gruplara ayırır
    ve yeni dosyalar oluşturur. Import yapısını korur ve
    __init__.py dosyalarını günceller.
    """
    
    def __init__(self, strateji: BolmeStratejisi = BolmeStratejisi.FONKSIYONEL):
        """
        Args:
            strateji: Kullanılacak bölme stratejisi
        """
        self.strateji = strateji
    
    def dosyayi_bol(
        self,
        dosya_yolu: str,
        hedef_klasor: str = None
    ) -> List[YeniDosya]:
        """
        Dosyayı belirtilen stratejiye göre böler.
        
        Args:
            dosya_yolu: Bölünecek dosya yolu
            hedef_klasor: Yeni dosyaların oluşturulacağı klasör
            
        Returns:
            Oluşturulan yeni dosyaların listesi
        """
        # Dosyayı oku
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        # Hedef klasörü belirle
        if hedef_klasor is None:
            hedef_klasor = str(Path(dosya_yolu).parent)
        
        # Fonksiyonel grupları tespit et
        gruplar = self.fonksiyonel_gruplari_tespit_et(icerik, dosya_yolu)
        
        # Yeni dosyalar oluştur
        yeni_dosyalar = []
        dosya_adi_taban = Path(dosya_yolu).stem
        
        for grup in gruplar:
            yeni_dosya = self._grup_icin_dosya_olustur(
                grup, dosya_adi_taban, hedef_klasor, icerik
            )
            yeni_dosyalar.append(yeni_dosya)
        
        return yeni_dosyalar

    def fonksiyonel_gruplari_tespit_et(
        self,
        dosya_icerik: str,
        dosya_yolu: str
    ) -> List[FonksiyonelGrup]:
        """
        Dosyadaki fonksiyonel grupları tespit eder.
        
        Fonksiyonları ve sınıfları analiz ederek mantıklı
        gruplara ayırır. Örnek gruplar:
        - _yardimcilari: Yardımcı fonksiyonlar
        - _dogrulama: Doğrulama fonksiyonları
        - _veri_islemleri: Veri işleme fonksiyonları
        
        Args:
            dosya_icerik: Dosya içeriği
            dosya_yolu: Dosya yolu
            
        Returns:
            Fonksiyonel grup listesi
        """
        try:
            agac = ast.parse(dosya_icerik)
        except SyntaxError:
            return []
        
        gruplar_dict = {}
        satirlar = dosya_icerik.split('\n')
        
        for node in ast.walk(agac):
            if isinstance(node, ast.FunctionDef):
                grup_adi = self._fonksiyon_grubu_belirle(node.name)
                
                if grup_adi not in gruplar_dict:
                    gruplar_dict[grup_adi] = FonksiyonelGrup(isim=grup_adi)
                
                # Fonksiyon kodunu al
                baslangic = node.lineno - 1
                bitis = node.end_lineno if node.end_lineno else baslangic + 1
                fonk_kodu = '\n'.join(satirlar[baslangic:bitis])
                
                gruplar_dict[grup_adi].icerik.append(fonk_kodu)
                gruplar_dict[grup_adi].satirlar.extend(range(baslangic, bitis))
                
                # Bağımlılıkları tespit et
                bagimliliklari = self._fonksiyon_bagimlilikları_bul(node)
                gruplar_dict[grup_adi].bagimliliklari.update(bagimliliklari)
            
            elif isinstance(node, ast.ClassDef):
                grup_adi = f"sinif_{node.name.lower()}"
                
                if grup_adi not in gruplar_dict:
                    gruplar_dict[grup_adi] = FonksiyonelGrup(isim=grup_adi)
                
                baslangic = node.lineno - 1
                bitis = node.end_lineno if node.end_lineno else baslangic + 1
                sinif_kodu = '\n'.join(satirlar[baslangic:bitis])
                
                gruplar_dict[grup_adi].icerik.append(sinif_kodu)
                gruplar_dict[grup_adi].satirlar.extend(range(baslangic, bitis))
        
        return list(gruplar_dict.values())
    
    def _fonksiyon_grubu_belirle(self, fonksiyon_adi: str) -> str:
        """
        Fonksiyon adından grup adını belirler.
        
        Args:
            fonksiyon_adi: Fonksiyon adı
            
        Returns:
            Grup adı
        """
        adi_kucuk = fonksiyon_adi.lower()
        
        # Doğrulama fonksiyonları
        if any(k in adi_kucuk for k in ['dogrula', 'validate', 'kontrol', 'check']):
            return 'dogrulama'
        
        # Yardımcı fonksiyonlar
        if adi_kucuk.startswith('_') and not adi_kucuk.startswith('__'):
            return 'yardimcilar'
        
        # Veri işleme
        if any(k in adi_kucuk for k in ['isle', 'process', 'donustur', 'convert']):
            return 'veri_islemleri'
        
        # Hesaplama
        if any(k in adi_kucuk for k in ['hesapla', 'calculate', 'compute']):
            return 'hesaplamalar'
        
        # Varsayılan
        return 'ana'
    
    def _fonksiyon_bagimlilikları_bul(self, fonksiyon_node: ast.FunctionDef) -> Set[str]:
        """
        Fonksiyonun bağımlılıklarını bulur.
        
        Args:
            fonksiyon_node: AST fonksiyon node'u
            
        Returns:
            Bağımlılık isimleri
        """
        bagimliliklari = set()
        
        for node in ast.walk(fonksiyon_node):
            if isinstance(node, ast.Name):
                bagimliliklari.add(node.id)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    bagimliliklari.add(node.func.id)
        
        return bagimliliklari

    def _grup_icin_dosya_olustur(
        self,
        grup: FonksiyonelGrup,
        dosya_adi_taban: str,
        hedef_klasor: str,
        orijinal_icerik: str
    ) -> YeniDosya:
        """
        Fonksiyonel grup için yeni dosya oluşturur.
        
        Args:
            grup: Fonksiyonel grup
            dosya_adi_taban: Orijinal dosya adı (uzantısız)
            hedef_klasor: Hedef klasör
            orijinal_icerik: Orijinal dosya içeriği
            
        Returns:
            Yeni dosya bilgisi
        """
        # Dosya adını oluştur
        if grup.isim == 'ana':
            yeni_dosya_adi = f"{dosya_adi_taban}.py"
        else:
            yeni_dosya_adi = f"{dosya_adi_taban}_{grup.isim}.py"
        
        yeni_dosya_yolu = os.path.join(hedef_klasor, yeni_dosya_adi)
        
        # Import listesini çıkar
        import_listesi = self._import_listesi_cikart(orijinal_icerik)
        
        # Dosya içeriğini oluştur
        icerik_parcalari = []
        
        # Başlık ekle
        icerik_parcalari.append(self._dosya_basligi_olustur(
            dosya_adi_taban, grup.isim
        ))
        
        # Import'ları ekle
        if import_listesi:
            icerik_parcalari.append('\n'.join(import_listesi))
            icerik_parcalari.append('')
        
        # Grup içeriğini ekle
        icerik_parcalari.extend(grup.icerik)
        
        yeni_icerik = '\n\n'.join(icerik_parcalari)
        
        return YeniDosya(
            dosya_adi=yeni_dosya_adi,
            dosya_yolu=yeni_dosya_yolu,
            icerik=yeni_icerik,
            import_listesi=import_listesi
        )
    
    def _import_listesi_cikart(self, dosya_icerik: str) -> List[str]:
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
                import_satirlari.append(satirlar[satir_no])
        
        return import_satirlari
    
    def _dosya_basligi_olustur(self, dosya_adi: str, grup_adi: str) -> str:
        """
        Yeni dosya için başlık oluşturur.
        
        Args:
            dosya_adi: Dosya adı
            grup_adi: Grup adı
            
        Returns:
            Başlık metni
        """
        from datetime import date
        
        return f"""# Version: 0.1.0
# Last Update: {date.today().isoformat()}
# Module: {dosya_adi}_{grup_adi}
# Description: {grup_adi.replace('_', ' ').title()} modülü
# Changelog:
# - Otomatik bölme ile oluşturuldu
"""
    
    def init_dosyasini_guncelle(
        self,
        modul_yolu: str,
        yeni_dosyalar: List[YeniDosya]
    ) -> None:
        """
        __init__.py dosyasını yeni dosyalarla günceller.
        
        Args:
            modul_yolu: Modül klasör yolu
            yeni_dosyalar: Oluşturulan yeni dosyalar
        """
        init_yolu = os.path.join(modul_yolu, '__init__.py')
        
        # Mevcut __init__.py'yi oku (varsa)
        mevcut_icerik = ""
        if os.path.exists(init_yolu):
            with open(init_yolu, 'r', encoding='utf-8') as f:
                mevcut_icerik = f.read()
        
        # Yeni import'ları oluştur
        yeni_importlar = []
        for dosya in yeni_dosyalar:
            modul_adi = Path(dosya.dosya_adi).stem
            yeni_importlar.append(f"from .{modul_adi} import *")
        
        # __init__.py içeriğini oluştur
        if not mevcut_icerik:
            # Yeni __init__.py oluştur
            icerik = self._yeni_init_olustur(yeni_importlar)
        else:
            # Mevcut __init__.py'yi güncelle
            icerik = self._mevcut_init_guncelle(mevcut_icerik, yeni_importlar)
        
        # Dosyayı yaz
        with open(init_yolu, 'w', encoding='utf-8') as f:
            f.write(icerik)
    
    def _yeni_init_olustur(self, import_listesi: List[str]) -> str:
        """Yeni __init__.py içeriği oluşturur"""
        from datetime import date
        
        return f"""# Version: 0.1.0
# Last Update: {date.today().isoformat()}
# Module: __init__
# Description: Modül başlatma dosyası
# Changelog:
# - Otomatik oluşturuldu

{chr(10).join(import_listesi)}
"""
    
    def _mevcut_init_guncelle(
        self,
        mevcut_icerik: str,
        yeni_importlar: List[str]
    ) -> str:
        """Mevcut __init__.py'yi günceller"""
        satirlar = mevcut_icerik.split('\n')
        
        # Import bölümünü bul
        import_baslangic = -1
        for i, satir in enumerate(satirlar):
            if satir.strip().startswith('from .') or satir.strip().startswith('import '):
                if import_baslangic == -1:
                    import_baslangic = i
        
        # Yeni import'ları ekle
        if import_baslangic != -1:
            # Mevcut import'lardan sonra ekle
            satirlar = satirlar[:import_baslangic] + yeni_importlar + satirlar[import_baslangic:]
        else:
            # Başlıktan sonra ekle
            satirlar.extend([''] + yeni_importlar)
        
        return '\n'.join(satirlar)
