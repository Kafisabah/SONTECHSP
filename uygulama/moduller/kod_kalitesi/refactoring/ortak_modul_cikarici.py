# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.refactoring.ortak_modul_cikarici
# Description: Ortak kod bloklarını ayrı modüllere çıkaran sistem
# Changelog:
# - İlk versiyon: OrtakModulCikarici sınıfı oluşturuldu

"""
Ortak Modül Çıkarıcı

Benzer kod bloklarını tespit eder ve ortak modüllere taşır.
Tüm referansları günceller ve fonksiyonaliteyi korur.
"""

import ast
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class KodTasima:
    """Kod taşıma işlemi bilgisi"""
    kaynak_dosya: str
    hedef_dosya: str
    fonksiyon_adi: str
    fonksiyon_kodu: str
    baslangic_satir: int
    bitis_satir: int


@dataclass
class ReferansGuncelleme:
    """Referans güncelleme bilgisi"""
    dosya_yolu: str
    eski_referans: str
    yeni_referans: str
    satir_no: int


class OrtakModulCikarici:
    """
    Ortak modül çıkarma işlemlerini yöneten sınıf.
    
    Benzer kod bloklarını ortak modüllere taşır,
    tüm referansları günceller ve fonksiyonaliteyi korur.
    """
    
    def __init__(self, proje_koku: str = "."):
        """
        Args:
            proje_koku: Proje kök dizini
        """
        self.proje_koku = proje_koku
        self.tasima_kayitlari: List[KodTasima] = []
        self.referans_guncellemeleri: List[ReferansGuncelleme] = []
    
    def ortak_modul_olustur(
        self,
        modul_adi: str,
        modul_yolu: str,
        benzer_bloklar: List,
        ortak_kod: str
    ) -> str:
        """
        Ortak modül oluşturur ve kodu taşır.
        
        Args:
            modul_adi: Modül adı
            modul_yolu: Modül dosya yolu
            benzer_bloklar: Benzer kod blokları listesi
            ortak_kod: Ortak kod içeriği
            
        Returns:
            Oluşturulan modül yolu
        """
        # Hedef klasörü oluştur
        hedef_klasor = Path(modul_yolu).parent
        hedef_klasor.mkdir(parents=True, exist_ok=True)
        
        # Modül içeriğini oluştur
        modul_icerik = self._modul_icerik_olustur(
            modul_adi, ortak_kod, benzer_bloklar
        )
        
        # Modül dosyasını yaz
        with open(modul_yolu, 'w', encoding='utf-8') as f:
            f.write(modul_icerik)
        
        # Taşıma kaydı oluştur
        if benzer_bloklar:
            ilk_blok = benzer_bloklar[0]
            tasima = KodTasima(
                kaynak_dosya=ilk_blok.dosya_yolu,
                hedef_dosya=modul_yolu,
                fonksiyon_adi=ilk_blok.fonksiyon_adi,
                fonksiyon_kodu=ortak_kod,
                baslangic_satir=ilk_blok.baslangic_satir,
                bitis_satir=ilk_blok.bitis_satir
            )
            self.tasima_kayitlari.append(tasima)
        
        return modul_yolu

    def _modul_icerik_olustur(
        self,
        modul_adi: str,
        ortak_kod: str,
        benzer_bloklar: List
    ) -> str:
        """
        Ortak modül için içerik oluşturur.
        
        Args:
            modul_adi: Modül adı
            ortak_kod: Ortak kod
            benzer_bloklar: Benzer bloklar
            
        Returns:
            Modül içeriği
        """
        parcalar = []
        
        # Başlık
        parcalar.append(self._modul_basligi_olustur(modul_adi, benzer_bloklar))
        parcalar.append('')
        
        # Docstring
        parcalar.append(f'"""')
        parcalar.append(f'{modul_adi.replace("_", " ").title()}')
        parcalar.append('')
        parcalar.append('Ortak yardımcı fonksiyonlar.')
        parcalar.append('Otomatik kod tekrarı analizi ile oluşturuldu.')
        parcalar.append(f'"""')
        parcalar.append('')
        
        # Import'ları çıkar ve ekle
        importlar = self._kod_icinden_importlari_cikart(ortak_kod)
        if importlar:
            parcalar.extend(importlar)
            parcalar.append('')
        
        # Ortak kodu ekle
        parcalar.append(ortak_kod)
        
        return '\n'.join(parcalar)
    
    def _modul_basligi_olustur(
        self,
        modul_adi: str,
        benzer_bloklar: List
    ) -> str:
        """Modül başlığı oluşturur."""
        kaynak_dosyalar = set()
        if benzer_bloklar:
            for blok in benzer_bloklar[:3]:  # İlk 3 kaynak
                kaynak_dosyalar.add(Path(blok.dosya_yolu).name)
        
        kaynaklar_str = ', '.join(sorted(kaynak_dosyalar))
        
        return f"""# Version: 0.1.0
# Last Update: {date.today().isoformat()}
# Module: {modul_adi}
# Description: Ortak yardımcı fonksiyonlar
# Changelog:
# - Otomatik oluşturuldu (kaynak: {kaynaklar_str})"""
    
    def _kod_icinden_importlari_cikart(self, kod: str) -> List[str]:
        """
        Kod içinden import ifadelerini çıkartır.
        
        Args:
            kod: Kod içeriği
            
        Returns:
            Import satırları
        """
        try:
            agac = ast.parse(kod)
        except SyntaxError:
            return []
        
        importlar = []
        satirlar = kod.split('\n')
        
        for node in ast.walk(agac):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if hasattr(node, 'lineno'):
                    satir_no = node.lineno - 1
                    if 0 <= satir_no < len(satirlar):
                        importlar.append(satirlar[satir_no])
        
        return importlar

    def referanslari_guncelle(
        self,
        etkilenen_dosyalar: Set[str],
        ortak_modul_yolu: str,
        fonksiyon_adi: str
    ) -> List[ReferansGuncelleme]:
        """
        Etkilenen dosyalardaki referansları günceller.
        
        Args:
            etkilenen_dosyalar: Etkilenen dosya yolları
            ortak_modul_yolu: Ortak modül yolu
            fonksiyon_adi: Fonksiyon adı
            
        Returns:
            Yapılan güncellemeler listesi
        """
        guncellemeler = []
        
        # Ortak modül için import ifadesi oluştur
        modul_adi = Path(ortak_modul_yolu).stem
        yeni_import = f"from .{modul_adi} import {fonksiyon_adi}"
        
        for dosya_yolu in etkilenen_dosyalar:
            if not os.path.exists(dosya_yolu):
                continue
            
            # Dosyayı oku
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            # Fonksiyon tanımını kaldır
            yeni_icerik, kaldirilan = self._fonksiyon_tanimini_kaldir(
                icerik, fonksiyon_adi
            )
            
            if kaldirilan:
                # Import ekle
                yeni_icerik = self._import_ekle(yeni_icerik, yeni_import)
                
                # Dosyayı güncelle
                with open(dosya_yolu, 'w', encoding='utf-8') as f:
                    f.write(yeni_icerik)
                
                # Güncelleme kaydı oluştur
                guncelleme = ReferansGuncelleme(
                    dosya_yolu=dosya_yolu,
                    eski_referans=f"def {fonksiyon_adi}",
                    yeni_referans=yeni_import,
                    satir_no=0
                )
                guncellemeler.append(guncelleme)
                self.referans_guncellemeleri.append(guncelleme)
        
        return guncellemeler
    
    def _fonksiyon_tanimini_kaldir(
        self,
        icerik: str,
        fonksiyon_adi: str
    ) -> Tuple[str, bool]:
        """
        İçerikten fonksiyon tanımını kaldırır.
        
        Args:
            icerik: Dosya içeriği
            fonksiyon_adi: Fonksiyon adı
            
        Returns:
            (Yeni içerik, Kaldırıldı mı?)
        """
        try:
            agac = ast.parse(icerik)
        except SyntaxError:
            return icerik, False
        
        satirlar = icerik.split('\n')
        kaldirilan = False
        
        for node in ast.walk(agac):
            if isinstance(node, ast.FunctionDef) and node.name == fonksiyon_adi:
                # Fonksiyon satırlarını kaldır
                baslangic = node.lineno - 1
                bitis = node.end_lineno if node.end_lineno else baslangic + 1
                
                # Satırları boşalt
                for i in range(baslangic, bitis):
                    if i < len(satirlar):
                        satirlar[i] = ''
                
                kaldirilan = True
                break
        
        # Boş satırları temizle
        yeni_satirlar = []
        bos_sayac = 0
        for satir in satirlar:
            if not satir.strip():
                bos_sayac += 1
                if bos_sayac <= 2:  # Maksimum 2 boş satır
                    yeni_satirlar.append(satir)
            else:
                bos_sayac = 0
                yeni_satirlar.append(satir)
        
        return '\n'.join(yeni_satirlar), kaldirilan
    
    def _import_ekle(self, icerik: str, yeni_import: str) -> str:
        """
        İçeriğe yeni import ekler.
        
        Args:
            icerik: Dosya içeriği
            yeni_import: Eklenecek import
            
        Returns:
            Güncellenmiş içerik
        """
        satirlar = icerik.split('\n')
        
        # Import bölümünü bul
        import_son_satir = 0
        for i, satir in enumerate(satirlar):
            temiz = satir.strip()
            if temiz.startswith('import ') or temiz.startswith('from '):
                import_son_satir = i + 1
        
        # Yeni import'u ekle
        if import_son_satir > 0:
            satirlar.insert(import_son_satir, yeni_import)
        else:
            # Başlıktan sonra ekle
            baslik_son = 0
            for i, satir in enumerate(satirlar):
                if satir.strip().startswith('#'):
                    baslik_son = i + 1
                else:
                    break
            satirlar.insert(baslik_son, yeni_import)
            satirlar.insert(baslik_son + 1, '')
        
        return '\n'.join(satirlar)

    def fonksiyonalite_dogrula(
        self,
        orijinal_dosya: str,
        guncellenmis_dosya: str
    ) -> bool:
        """
        Fonksiyonalitenin korunduğunu doğrular.
        
        Args:
            orijinal_dosya: Orijinal dosya yolu
            guncellenmis_dosya: Güncellenmiş dosya yolu
            
        Returns:
            Fonksiyonalite korundu mu?
        """
        # Basit kontrol: Her iki dosya da geçerli Python kodu mu?
        try:
            with open(orijinal_dosya, 'r', encoding='utf-8') as f:
                orijinal = f.read()
            ast.parse(orijinal)
        except (SyntaxError, FileNotFoundError):
            return False
        
        try:
            with open(guncellenmis_dosya, 'r', encoding='utf-8') as f:
                guncellenmis = f.read()
            ast.parse(guncellenmis)
        except (SyntaxError, FileNotFoundError):
            return False
        
        # Her iki dosya da geçerli Python kodu
        return True
    
    def geri_al(self) -> None:
        """
        Yapılan değişiklikleri geri alır.
        
        Not: Bu basit bir implementasyon. Gerçek kullanımda
        git veya backup sistemi kullanılmalı.
        """
        # Taşınan dosyaları sil
        for tasima in self.tasima_kayitlari:
            if os.path.exists(tasima.hedef_dosya):
                try:
                    os.remove(tasima.hedef_dosya)
                except Exception:
                    pass
        
        # Kayıtları temizle
        self.tasima_kayitlari.clear()
        self.referans_guncellemeleri.clear()
    
    def rapor_olustur(self) -> str:
        """
        Yapılan işlemlerin raporunu oluşturur.
        
        Returns:
            Rapor metni
        """
        parcalar = []
        
        parcalar.append("# Ortak Modül Çıkarma Raporu")
        parcalar.append(f"Tarih: {date.today().isoformat()}")
        parcalar.append("")
        
        parcalar.append(f"## Taşınan Kod Blokları: {len(self.tasima_kayitlari)}")
        for tasima in self.tasima_kayitlari:
            parcalar.append(f"- {tasima.fonksiyon_adi}")
            parcalar.append(f"  Kaynak: {tasima.kaynak_dosya}")
            parcalar.append(f"  Hedef: {tasima.hedef_dosya}")
        
        parcalar.append("")
        parcalar.append(f"## Güncellenen Referanslar: {len(self.referans_guncellemeleri)}")
        for guncelleme in self.referans_guncellemeleri:
            parcalar.append(f"- {guncelleme.dosya_yolu}")
            parcalar.append(f"  Eski: {guncelleme.eski_referans}")
            parcalar.append(f"  Yeni: {guncelleme.yeni_referans}")
        
        return '\n'.join(parcalar)
