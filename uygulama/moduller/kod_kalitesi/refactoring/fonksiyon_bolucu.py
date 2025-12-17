# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.refactoring.fonksiyon_bolucu
# Description: Büyük fonksiyonları yardımcı fonksiyonlara bölen sistem
# Changelog:
# - İlk versiyon: FonksiyonBolucu sınıfı oluşturuldu

"""
Fonksiyon Bölücü

Büyük fonksiyonları analiz eder ve mantıklı
yardımcı fonksiyonlara böler.
"""

import ast
import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class YardimciFonksiyon:
    """Yardımcı fonksiyon bilgisi"""
    isim: str
    kod: str
    parametreler: List[str]
    donus_degeri: str


class FonksiyonBolucu:
    """
    Fonksiyon bölme işlemlerini yöneten sınıf.
    
    Büyük fonksiyonları analiz eder, mantıklı kod bloklarını
    tespit eder ve yardımcı fonksiyonlar oluşturur.
    """
    
    def __init__(self, satir_limiti: int = 25):
        """
        Args:
            satir_limiti: Maksimum fonksiyon satır sayısı
        """
        self.satir_limiti = satir_limiti
    
    def fonksiyonu_bol(
        self,
        fonksiyon_kodu: str,
        fonksiyon_adi: str = None
    ) -> Tuple[str, List[YardimciFonksiyon]]:
        """
        Fonksiyonu yardımcı fonksiyonlara böler.
        
        Args:
            fonksiyon_kodu: Fonksiyon kodu
            fonksiyon_adi: Fonksiyon adı (opsiyonel)
            
        Returns:
            (Güncellenmiş ana fonksiyon, Yardımcı fonksiyonlar listesi)
        """
        try:
            agac = ast.parse(fonksiyon_kodu)
        except SyntaxError:
            return fonksiyon_kodu, []
        
        # Fonksiyon node'unu bul
        fonksiyon_node = None
        for node in ast.walk(agac):
            if isinstance(node, ast.FunctionDef):
                if fonksiyon_adi is None or node.name == fonksiyon_adi:
                    fonksiyon_node = node
                    break
        
        if fonksiyon_node is None:
            return fonksiyon_kodu, []
        
        # Bölünebilir kod bloklarını tespit et
        bolunebilir_bloklar = self._bolunebilir_bloklari_tespit_et(fonksiyon_node)
        
        # Yardımcı fonksiyonlar oluştur
        yardimci_fonksiyonlar = []
        for i, blok in enumerate(bolunebilir_bloklar):
            yardimci = self.yardimci_fonksiyon_olustur(
                blok, f"_{fonksiyon_node.name}_yardimci_{i+1}"
            )
            yardimci_fonksiyonlar.append(yardimci)
        
        # Ana fonksiyonu güncelle
        if yardimci_fonksiyonlar:
            guncellenmis_ana = self.ana_fonksiyonu_guncelle(
                fonksiyon_kodu, yardimci_fonksiyonlar
            )
            return guncellenmis_ana, yardimci_fonksiyonlar
        
        return fonksiyon_kodu, []

    def _bolunebilir_bloklari_tespit_et(
        self,
        fonksiyon_node: ast.FunctionDef
    ) -> List[str]:
        """
        Fonksiyon içinde bölünebilir kod bloklarını tespit eder.
        
        Bölünebilir bloklar:
        - For/while döngüleri
        - Try-except blokları
        - If-else blokları (karmaşık olanlar)
        - Ardışık işlem grupları
        
        Args:
            fonksiyon_node: AST fonksiyon node'u
            
        Returns:
            Bölünebilir kod blokları listesi
        """
        bloklar = []
        
        for node in fonksiyon_node.body:
            # Döngüler
            if isinstance(node, (ast.For, ast.While)):
                if len(node.body) > 5:  # Yeterince büyükse
                    blok_kodu = ast.unparse(node)
                    bloklar.append(blok_kodu)
            
            # Try-except blokları
            elif isinstance(node, ast.Try):
                if len(node.body) > 5:
                    blok_kodu = ast.unparse(node)
                    bloklar.append(blok_kodu)
            
            # Karmaşık if-else blokları
            elif isinstance(node, ast.If):
                if len(node.body) + len(node.orelse) > 5:
                    blok_kodu = ast.unparse(node)
                    bloklar.append(blok_kodu)
        
        return bloklar
    
    def yardimci_fonksiyon_olustur(
        self,
        kod_blogu: str,
        isim: str
    ) -> YardimciFonksiyon:
        """
        Kod bloğundan yardımcı fonksiyon oluşturur.
        
        Args:
            kod_blogu: Kod bloğu
            isim: Fonksiyon ismi
            
        Returns:
            Yardımcı fonksiyon bilgisi
        """
        # Kod bloğunu analiz et
        try:
            agac = ast.parse(kod_blogu)
        except SyntaxError:
            # Parse edilemezse basit wrapper oluştur
            return YardimciFonksiyon(
                isim=isim,
                kod=f"def {isim}():\n    {kod_blogu}",
                parametreler=[],
                donus_degeri="None"
            )
        
        # Kullanılan değişkenleri tespit et
        kullanilan_degiskenler = self._kullanilan_degiskenleri_bul(agac)
        
        # Fonksiyon kodunu oluştur
        parametreler = list(kullanilan_degiskenler)
        fonksiyon_kodu = self._fonksiyon_kodu_olustur(
            isim, parametreler, kod_blogu
        )
        
        return YardimciFonksiyon(
            isim=isim,
            kod=fonksiyon_kodu,
            parametreler=parametreler,
            donus_degeri="None"
        )
    
    def _kullanilan_degiskenleri_bul(self, agac: ast.AST) -> set:
        """
        Kod bloğunda kullanılan değişkenleri bulur.
        
        Args:
            agac: AST ağacı
            
        Returns:
            Değişken isimleri
        """
        degiskenler = set()
        
        for node in ast.walk(agac):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    degiskenler.add(node.id)
        
        # Yerleşik fonksiyonları çıkar
        yerlesikler = {'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict'}
        degiskenler = degiskenler - yerlesikler
        
        return degiskenler
    
    def _fonksiyon_kodu_olustur(
        self,
        isim: str,
        parametreler: List[str],
        kod_blogu: str
    ) -> str:
        """
        Fonksiyon kodu oluşturur.
        
        Args:
            isim: Fonksiyon ismi
            parametreler: Parametre listesi
            kod_blogu: Fonksiyon gövdesi
            
        Returns:
            Tam fonksiyon kodu
        """
        param_str = ', '.join(parametreler) if parametreler else ''
        
        # Kod bloğunu girintile
        kod_satirlari = kod_blogu.split('\n')
        girintili_kod = '\n'.join('    ' + satir for satir in kod_satirlari)
        
        return f"""def {isim}({param_str}):
    \"\"\"Yardımcı fonksiyon\"\"\"
{girintili_kod}
"""

    def ana_fonksiyonu_guncelle(
        self,
        ana_fonksiyon: str,
        yardimcilar: List[YardimciFonksiyon]
    ) -> str:
        """
        Ana fonksiyonu yardımcı fonksiyon çağrılarıyla günceller.
        
        Args:
            ana_fonksiyon: Orijinal ana fonksiyon kodu
            yardimcilar: Yardımcı fonksiyonlar listesi
            
        Returns:
            Güncellenmiş ana fonksiyon kodu
        """
        guncellenmis = ana_fonksiyon
        
        # Her yardımcı fonksiyon için
        for yardimci in yardimcilar:
            # Orijinal kod bloğunu bul ve yardımcı çağrısıyla değiştir
            # Bu basitleştirilmiş bir yaklaşım - gerçek uygulamada
            # daha sofistike bir eşleştirme gerekebilir
            
            # Yardımcı fonksiyon çağrısı oluştur
            param_str = ', '.join(yardimci.parametreler)
            cagri = f"{yardimci.isim}({param_str})"
            
            # Not: Gerçek uygulamada kod bloğunu tam olarak eşleştirmek
            # ve değiştirmek için daha gelişmiş bir yöntem kullanılmalı
            # Şimdilik basit bir placeholder kullanıyoruz
            
        return guncellenmis
