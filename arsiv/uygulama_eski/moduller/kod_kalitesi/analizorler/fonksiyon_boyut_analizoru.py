# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.analizorler.fonksiyon_boyut_analizoru
# Description: Fonksiyon boyut analizi ve limit kontrolü
# Changelog:
# - İlk versiyon: FonksiyonBoyutAnalizoru sınıfı oluşturuldu

"""
Fonksiyon Boyut Analizörü

25 satır limitini aşan fonksiyonları tespit eder.
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class FonksiyonBilgisi:
    """Fonksiyon bilgisi"""
    isim: str
    baslangic_satiri: int
    bitis_satiri: int
    satir_sayisi: int


@dataclass
class FonksiyonRaporu:
    """Fonksiyon analiz raporu"""
    dosya_yolu: str
    fonksiyon_adi: str
    satir_sayisi: int
    karmasiklik_skoru: int
    bolme_onerileri: List[str]


class FonksiyonBoyutAnalizoru:
    """
    Fonksiyon boyut analizi yapan sınıf.
    
    AST kullanarak fonksiyonları analiz eder ve
    25 satır limitini aşanları tespit eder.
    """
    
    SATIR_LIMITI = 25
    
    def __init__(self, satir_limiti: int = SATIR_LIMITI):
        """
        Args:
            satir_limiti: Maksimum satır sayısı (varsayılan: 25)
        """
        self.satir_limiti = satir_limiti
    
    def buyuk_fonksiyonlari_tespit_et(
        self,
        dosya_yolu: str
    ) -> List[FonksiyonRaporu]:
        """
        Dosyadaki büyük fonksiyonları tespit eder.
        
        Args:
            dosya_yolu: Analiz edilecek dosya yolu
            
        Returns:
            Limit aşan fonksiyonların rapor listesi
        """
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
        except Exception:
            return []
        
        fonksiyonlar = self.ast_ile_fonksiyon_analizi(icerik)
        raporlar = []
        
        for fonk in fonksiyonlar:
            if fonk.satir_sayisi > self.satir_limiti:
                rapor = FonksiyonRaporu(
                    dosya_yolu=dosya_yolu,
                    fonksiyon_adi=fonk.isim,
                    satir_sayisi=fonk.satir_sayisi,
                    karmasiklik_skoru=0,
                    bolme_onerileri=[]
                )
                raporlar.append(rapor)
        
        return raporlar

    def ast_ile_fonksiyon_analizi(
        self,
        dosya_icerik: str
    ) -> List[FonksiyonBilgisi]:
        """
        AST kullanarak fonksiyonları analiz eder.
        
        Args:
            dosya_icerik: Dosya içeriği
            
        Returns:
            Fonksiyon bilgileri listesi
        """
        try:
            agac = ast.parse(dosya_icerik)
        except SyntaxError:
            return []
        
        fonksiyonlar = []
        
        for node in ast.walk(agac):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                satir_sayisi = self.fonksiyon_satirlarini_say(
                    node, dosya_icerik
                )
                
                fonk_bilgi = FonksiyonBilgisi(
                    isim=node.name,
                    baslangic_satiri=node.lineno,
                    bitis_satiri=node.end_lineno or node.lineno,
                    satir_sayisi=satir_sayisi
                )
                fonksiyonlar.append(fonk_bilgi)
        
        return fonksiyonlar
    
    def fonksiyon_satirlarini_say(
        self,
        fonksiyon_node: ast.FunctionDef,
        dosya_icerik: str
    ) -> int:
        """
        Fonksiyonun gerçek kod satırlarını sayar.
        
        Args:
            fonksiyon_node: AST fonksiyon node'u
            dosya_icerik: Dosya içeriği
            
        Returns:
            Gerçek kod satır sayısı
        """
        baslangic = fonksiyon_node.lineno
        bitis = fonksiyon_node.end_lineno or baslangic
        
        satirlar = dosya_icerik.split('\n')
        fonksiyon_satirlari = satirlar[baslangic - 1:bitis]
        
        kod_satir_sayisi = 0
        coklu_yorum = False
        
        for satir in fonksiyon_satirlari:
            temiz_satir = satir.strip()
            
            if not temiz_satir:
                continue
            
            if '"""' in temiz_satir or "'''" in temiz_satir:
                tirnak_sayisi = temiz_satir.count('"""') + temiz_satir.count("'''")
                if tirnak_sayisi == 1:
                    coklu_yorum = not coklu_yorum
                    continue
                elif tirnak_sayisi == 2:
                    continue
            
            if coklu_yorum:
                continue
            
            if temiz_satir.startswith('#'):
                continue
            
            kod_satir_sayisi += 1
        
        return kod_satir_sayisi
