# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.refactoring.modul_tutarlilik_koruyucu
# Description: Modül tutarlılığı ve public API koruma sistemi
# Changelog:
# - İlk versiyon: ModulTutarlilikKoruyucu sınıfı oluşturuldu

"""
Modül Tutarlılık Koruyucu

Refactoring işlemleri sırasında modül içi tutarlılığı korur
ve public API değişikliklerini tespit eder.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class APIBilgisi:
    """Public API bilgisi"""
    fonksiyonlar: Set[str] = field(default_factory=set)
    siniflar: Set[str] = field(default_factory=set)
    degiskenler: Set[str] = field(default_factory=set)
    __all__: List[str] = field(default_factory=list)


@dataclass
class APIFarki:
    """API değişiklik bilgisi"""
    eklenen_fonksiyonlar: Set[str] = field(default_factory=set)
    silinen_fonksiyonlar: Set[str] = field(default_factory=set)
    eklenen_siniflar: Set[str] = field(default_factory=set)
    silinen_siniflar: Set[str] = field(default_factory=set)
    degisen_imzalar: Dict[str, Tuple[str, str]] = field(default_factory=dict)


@dataclass
class TutarlilikSonucu:
    """Tutarlılık kontrol sonucu"""
    tutarli: bool
    hatalar: List[str] = field(default_factory=list)
    uyarilar: List[str] = field(default_factory=list)


class ModulTutarlilikKoruyucu:
    """
    Modül tutarlılığı ve public API koruma sistemi.
    
    Refactoring işlemleri sırasında:
    - Modül içi tutarlılığı kontrol eder
    - Public API değişikliklerini tespit eder
    - Geriye dönük uyumluluk kontrolü yapar
    """
    
    def __init__(self):
        """Koruyucuyu başlatır"""
        self.onceki_api: Dict[str, APIBilgisi] = {}
        self.sonraki_api: Dict[str, APIBilgisi] = {}
    
    def api_bilgisi_cikart(self, dosya_yolu: str) -> APIBilgisi:
        """
        Dosyanın public API bilgisini çıkartır.
        
        Public API:
        - Alt çizgi ile başlamayan fonksiyonlar
        - Alt çizgi ile başlamayan sınıflar
        - __all__ listesindeki öğeler
        
        Args:
            dosya_yolu: Analiz edilecek dosya
            
        Returns:
            API bilgisi
        """
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        try:
            agac = ast.parse(icerik)
        except SyntaxError:
            return APIBilgisi()
        
        api = APIBilgisi()
        
        for node in agac.body:
            # Fonksiyonlar
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    api.fonksiyonlar.add(node.name)
            
            # Sınıflar
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith('_'):
                    api.siniflar.add(node.name)
            
            # Değişkenler
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if not target.id.startswith('_'):
                            api.degiskenler.add(target.id)
                        
                        # __all__ kontrolü
                        if target.id == '__all__':
                            if isinstance(node.value, ast.List):
                                api.__all__ = [
                                    elt.s for elt in node.value.elts
                                    if isinstance(elt, ast.Constant)
                                ]
        
        return api
    
    def api_farklarini_tespit_et(
        self,
        onceki_dosya: str,
        sonraki_dosya: str
    ) -> APIFarki:
        """
        İki dosya versiyonu arasındaki API farklarını tespit eder.
        
        Args:
            onceki_dosya: Önceki dosya yolu
            sonraki_dosya: Sonraki dosya yolu
            
        Returns:
            API farkları
        """
        onceki_api = self.api_bilgisi_cikart(onceki_dosya)
        sonraki_api = self.api_bilgisi_cikart(sonraki_dosya)
        
        fark = APIFarki()
        
        # Fonksiyon farkları
        fark.eklenen_fonksiyonlar = (
            sonraki_api.fonksiyonlar - onceki_api.fonksiyonlar
        )
        fark.silinen_fonksiyonlar = (
            onceki_api.fonksiyonlar - sonraki_api.fonksiyonlar
        )
        
        # Sınıf farkları
        fark.eklenen_siniflar = (
            sonraki_api.siniflar - onceki_api.siniflar
        )
        fark.silinen_siniflar = (
            onceki_api.siniflar - sonraki_api.siniflar
        )
        
        # İmza değişiklikleri
        fark.degisen_imzalar = self._imza_farklarini_bul(
            onceki_dosya, sonraki_dosya
        )
        
        return fark
    
    def _imza_farklarini_bul(
        self,
        onceki_dosya: str,
        sonraki_dosya: str
    ) -> Dict[str, Tuple[str, str]]:
        """
        Fonksiyon imza değişikliklerini bulur.
        
        Args:
            onceki_dosya: Önceki dosya yolu
            sonraki_dosya: Sonraki dosya yolu
            
        Returns:
            {fonksiyon_adi: (onceki_imza, yeni_imza)}
        """
        onceki_imzalar = self._fonksiyon_imzalarini_cikart(onceki_dosya)
        sonraki_imzalar = self._fonksiyon_imzalarini_cikart(sonraki_dosya)
        
        degisen_imzalar = {}
        
        for fonk_adi in onceki_imzalar:
            if fonk_adi in sonraki_imzalar:
                if onceki_imzalar[fonk_adi] != sonraki_imzalar[fonk_adi]:
                    degisen_imzalar[fonk_adi] = (
                        onceki_imzalar[fonk_adi],
                        sonraki_imzalar[fonk_adi]
                    )
        
        return degisen_imzalar
    
    def _fonksiyon_imzalarini_cikart(
        self,
        dosya_yolu: str
    ) -> Dict[str, str]:
        """
        Dosyadaki fonksiyon imzalarını çıkartır.
        
        Args:
            dosya_yolu: Dosya yolu
            
        Returns:
            {fonksiyon_adi: imza}
        """
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        try:
            agac = ast.parse(icerik)
        except SyntaxError:
            return {}
        
        imzalar = {}
        
        for node in ast.walk(agac):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    imza = self._imza_olustur(node)
                    imzalar[node.name] = imza
        
        return imzalar
    
    def _imza_olustur(self, fonksiyon_node: ast.FunctionDef) -> str:
        """
        Fonksiyon node'undan imza oluşturur.
        
        Args:
            fonksiyon_node: Fonksiyon node'u
            
        Returns:
            Fonksiyon imzası
        """
        args = fonksiyon_node.args
        
        # Parametreleri topla
        parametreler = []
        
        # Pozisyonel parametreler
        for arg in args.args:
            param = arg.arg
            if arg.annotation:
                param += f": {ast.unparse(arg.annotation)}"
            parametreler.append(param)
        
        # Varsayılan değerler
        defaults_offset = len(args.args) - len(args.defaults)
        for i, default in enumerate(args.defaults):
            param_index = defaults_offset + i
            parametreler[param_index] += f" = {ast.unparse(default)}"
        
        # Dönüş tipi
        donus_tipi = ""
        if fonksiyon_node.returns:
            donus_tipi = f" -> {ast.unparse(fonksiyon_node.returns)}"
        
        return f"{fonksiyon_node.name}({', '.join(parametreler)}){donus_tipi}"
    
    def modul_tutarliligini_kontrol_et(
        self,
        modul_yolu: str
    ) -> TutarlilikSonucu:
        """
        Modül içi tutarlılığı kontrol eder.
        
        Kontroller:
        - Import tutarlılığı
        - İsimlendirme tutarlılığı
        - Bağımlılık tutarlılığı
        
        Args:
            modul_yolu: Modül klasör yolu
            
        Returns:
            Tutarlılık sonucu
        """
        sonuc = TutarlilikSonucu(tutarli=True)
        
        # Modüldeki tüm Python dosyalarını bul
        modul_path = Path(modul_yolu)
        py_dosyalari = list(modul_path.glob('*.py'))
        
        if not py_dosyalari:
            sonuc.hatalar.append(f"Modülde Python dosyası bulunamadı: {modul_yolu}")
            sonuc.tutarli = False
            return sonuc
        
        # Import tutarlılığını kontrol et
        import_hatalari = self._import_tutarliligini_kontrol_et(py_dosyalari)
        if import_hatalari:
            sonuc.hatalar.extend(import_hatalari)
            sonuc.tutarli = False
        
        # İsimlendirme tutarlılığını kontrol et
        isimlendirme_uyarilari = self._isimlendirme_tutarliligini_kontrol_et(
            py_dosyalari
        )
        if isimlendirme_uyarilari:
            sonuc.uyarilar.extend(isimlendirme_uyarilari)
        
        # Bağımlılık tutarlılığını kontrol et
        bagimliliklari_hatalari = self._bagimliliklari_kontrol_et(py_dosyalari)
        if bagimliliklari_hatalari:
            sonuc.hatalar.extend(bagimliliklari_hatalari)
            sonuc.tutarli = False
        
        return sonuc
    
    def _import_tutarliligini_kontrol_et(
        self,
        dosyalar: List[Path]
    ) -> List[str]:
        """
        Import tutarlılığını kontrol eder.
        
        Args:
            dosyalar: Kontrol edilecek dosyalar
            
        Returns:
            Hata mesajları
        """
        hatalar = []
        
        for dosya in dosyalar:
            with open(dosya, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            try:
                agac = ast.parse(icerik)
            except SyntaxError:
                hatalar.append(f"Syntax hatası: {dosya}")
                continue
            
            # Import'ları kontrol et
            for node in agac.body:
                if isinstance(node, ast.ImportFrom):
                    # Göreceli import kontrolü
                    if node.level > 0:
                        # Modül içi import olmalı
                        if node.module and not node.module.startswith('.'):
                            hatalar.append(
                                f"Tutarsız göreceli import: {dosya} - "
                                f"from {node.module} import ..."
                            )
        
        return hatalar
    
    def _isimlendirme_tutarliligini_kontrol_et(
        self,
        dosyalar: List[Path]
    ) -> List[str]:
        """
        İsimlendirme tutarlılığını kontrol eder.
        
        Args:
            dosyalar: Kontrol edilecek dosyalar
            
        Returns:
            Uyarı mesajları
        """
        uyarilar = []
        
        # Dosya isimlendirme kontrolü
        for dosya in dosyalar:
            dosya_adi = dosya.stem
            
            # snake_case kontrolü
            if dosya_adi != dosya_adi.lower():
                uyarilar.append(
                    f"Dosya adı küçük harf olmalı: {dosya.name}"
                )
            
            # CamelCase kontrolü
            if any(c.isupper() for c in dosya_adi):
                uyarilar.append(
                    f"Dosya adı CamelCase içermemeli: {dosya.name}"
                )
            
            # Tire kontrolü
            if '-' in dosya_adi:
                uyarilar.append(
                    f"Dosya adında tire yerine alt çizgi kullanın: {dosya.name}"
                )
        
        return uyarilar
    
    def _bagimliliklari_kontrol_et(
        self,
        dosyalar: List[Path]
    ) -> List[str]:
        """
        Bağımlılık tutarlılığını kontrol eder.
        
        Circular dependency ve eksik import kontrolü yapar.
        
        Args:
            dosyalar: Kontrol edilecek dosyalar
            
        Returns:
            Hata mesajları
        """
        hatalar = []
        
        # Her dosyanın import ettiği modülleri topla
        import_grafigi: Dict[str, Set[str]] = {}
        
        for dosya in dosyalar:
            dosya_adi = dosya.stem
            import_grafigi[dosya_adi] = set()
            
            with open(dosya, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            try:
                agac = ast.parse(icerik)
            except SyntaxError:
                continue
            
            # Import'ları topla
            for node in agac.body:
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Modül içi import
                        if node.module.startswith('.'):
                            modul_adi = node.module.lstrip('.')
                            if modul_adi:
                                import_grafigi[dosya_adi].add(modul_adi)
        
        # Circular dependency kontrolü
        circular_deps = self._circular_dependency_bul(import_grafigi)
        if circular_deps:
            for dep in circular_deps:
                hatalar.append(
                    f"Circular dependency tespit edildi: {' -> '.join(dep)}"
                )
        
        return hatalar
    
    def _circular_dependency_bul(
        self,
        graf: Dict[str, Set[str]]
    ) -> List[List[str]]:
        """
        Circular dependency'leri bulur.
        
        Args:
            graf: Import grafiği
            
        Returns:
            Circular dependency listesi
        """
        circular_deps = []
        ziyaret_edilenler = set()
        yol = []
        
        def dfs(node: str):
            if node in yol:
                # Circular dependency bulundu
                cycle_start = yol.index(node)
                circular_deps.append(yol[cycle_start:] + [node])
                return
            
            if node in ziyaret_edilenler:
                return
            
            ziyaret_edilenler.add(node)
            yol.append(node)
            
            if node in graf:
                for komsu in graf[node]:
                    dfs(komsu)
            
            yol.pop()
        
        for node in graf:
            if node not in ziyaret_edilenler:
                dfs(node)
        
        return circular_deps
    
    def public_api_korunuyor_mu(
        self,
        onceki_dosya: str,
        sonraki_dosya: str
    ) -> Tuple[bool, List[str]]:
        """
        Public API'nin korunup korunmadığını kontrol eder.
        
        Args:
            onceki_dosya: Önceki dosya yolu
            sonraki_dosya: Sonraki dosya yolu
            
        Returns:
            (korunuyor_mu, hata_mesajlari) tuple'ı
        """
        fark = self.api_farklarini_tespit_et(onceki_dosya, sonraki_dosya)
        
        hatalar = []
        
        # Silinen fonksiyonlar
        if fark.silinen_fonksiyonlar:
            hatalar.append(
                f"Public fonksiyonlar silindi: "
                f"{', '.join(fark.silinen_fonksiyonlar)}"
            )
        
        # Silinen sınıflar
        if fark.silinen_siniflar:
            hatalar.append(
                f"Public sınıflar silindi: "
                f"{', '.join(fark.silinen_siniflar)}"
            )
        
        # Değişen imzalar
        if fark.degisen_imzalar:
            for fonk, (onceki, yeni) in fark.degisen_imzalar.items():
                hatalar.append(
                    f"Fonksiyon imzası değişti: {fonk}\n"
                    f"  Önceki: {onceki}\n"
                    f"  Yeni: {yeni}"
                )
        
        return len(hatalar) == 0, hatalar
