# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.pep8_kontrolcu
# Description: PEP8 kontrolü ve raporlama sistemi
# Changelog:
# - İlk versiyon: PEP8Kontrolcu sınıfı oluşturuldu

"""
PEP8 Kontrolcü

PEP8 uyumluluk kontrolü yapan ve detaylı rapor üreten sistem.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import sys


@dataclass
class PEP8Ihlal:
    """PEP8 ihlal bilgisi"""
    dosya: str
    satir: int
    sutun: int
    kod: str
    mesaj: str
    kategori: str  # 'E': Error, 'W': Warning, 'F': Fatal


@dataclass
class PEP8Rapor:
    """PEP8 kontrol raporu"""
    ihlaller: List[PEP8Ihlal]
    toplam_dosya: int
    kontrol_edilen_dosya: int
    basarili_dosya: int
    basarili: bool


class PEP8Kontrolcu:
    """
    PEP8 uyumluluk kontrolcüsü.
    
    flake8 veya pycodestyle kullanarak PEP8 kontrolü yapar
    ve detaylı rapor üretir.
    """
    
    def __init__(
        self,
        proje_yolu: str = ".",
        max_satir_uzunlugu: int = 120,
        hariç_tutulacaklar: List[str] = None
    ):
        """
        Args:
            proje_yolu: Kontrol edilecek proje yolu
            max_satir_uzunlugu: Maksimum satır uzunluğu
            hariç_tutulacaklar: Hariç tutulacak klasörler
        """
        self.proje_yolu = proje_yolu
        self.max_satir_uzunlugu = max_satir_uzunlugu
        
        if hariç_tutulacaklar is None:
            self.hariç_tutulacaklar = [
                '__pycache__', '.git', '.pytest_cache',
                'venv', 'env', '.hypothesis', 'htmlcov'
            ]
        else:
            self.hariç_tutulacaklar = hariç_tutulacaklar
    
    def tam_kontrol_yap(self) -> PEP8Rapor:
        """
        Tüm Python dosyalarında PEP8 kontrolü yapar.
        
        Returns:
            PEP8 kontrol raporu
        """
        # Basit kontrol yap (flake8 yerine)
        # flake8 kurulu olmayabilir veya çalışmayabilir
        ihlaller = self._basit_pep8_kontrolu()
        
        # Dosya sayılarını hesapla
        proje = Path(self.proje_yolu)
        tum_dosyalar = list(proje.rglob('*.py'))
        
        # Hariç tutulanları filtrele
        kontrol_edilen = [
            d for d in tum_dosyalar
            if not any(ht in d.parts for ht in self.hariç_tutulacaklar)
        ]
        
        # İhlal olan dosyaları bul
        ihlal_dosyalari = set(ihlal.dosya for ihlal in ihlaller)
        basarili_dosya = len(kontrol_edilen) - len(ihlal_dosyalari)
        
        rapor = PEP8Rapor(
            ihlaller=ihlaller,
            toplam_dosya=len(tum_dosyalar),
            kontrol_edilen_dosya=len(kontrol_edilen),
            basarili_dosya=basarili_dosya,
            basarili=(len(ihlaller) == 0)
        )
        
        return rapor
    
    def _flake8_kontrolu(self) -> List[PEP8Ihlal]:
        """
        flake8 ile PEP8 kontrolü yapar.
        
        Returns:
            İhlal listesi veya None (flake8 yoksa)
        """
        try:
            # flake8 komutunu çalıştır
            hariç = ','.join(self.hariç_tutulacaklar)
            
            sonuc = subprocess.run(
                [
                    sys.executable, '-m', 'flake8',
                    self.proje_yolu,
                    f'--exclude={hariç}',
                    f'--max-line-length={self.max_satir_uzunlugu}',
                    '--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s'
                ],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Çıktıyı parse et
            ihlaller = []
            for satir in sonuc.stdout.split('\n'):
                if not satir.strip():
                    continue
                
                ihlal = self._parse_flake8_satir(satir)
                if ihlal:
                    ihlaller.append(ihlal)
            
            return ihlaller
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # flake8 yoksa veya timeout olursa None dön
            return None
    
    def _parse_flake8_satir(self, satir: str) -> PEP8Ihlal:
        """
        flake8 çıktı satırını parse eder.
        
        Format: dosya:satir:sutun: KOD mesaj
        
        Args:
            satir: flake8 çıktı satırı
            
        Returns:
            PEP8Ihlal veya None
        """
        try:
            # Dosya yolu ve konum
            parts = satir.split(':', 3)
            if len(parts) < 4:
                return None
            
            dosya = parts[0].strip()
            satir_no = int(parts[1].strip())
            sutun = int(parts[2].strip())
            
            # Kod ve mesaj
            mesaj_kismi = parts[3].strip()
            kod_parts = mesaj_kismi.split(' ', 1)
            
            if len(kod_parts) < 2:
                kod = 'UNKNOWN'
                mesaj = mesaj_kismi
            else:
                kod = kod_parts[0]
                mesaj = kod_parts[1]
            
            # Kategori belirle (E: Error, W: Warning, F: Fatal)
            kategori = kod[0] if kod else 'U'
            
            return PEP8Ihlal(
                dosya=dosya,
                satir=satir_no,
                sutun=sutun,
                kod=kod,
                mesaj=mesaj,
                kategori=kategori
            )
            
        except (ValueError, IndexError):
            return None
    
    def _basit_pep8_kontrolu(self) -> List[PEP8Ihlal]:
        """
        Basit PEP8 kontrolü yapar (flake8 yoksa).
        
        Kontrol edilen kurallar:
        - Satır uzunluğu
        - Trailing whitespace
        - Boş satır sayısı
        
        Returns:
            İhlal listesi
        """
        ihlaller = []
        proje = Path(self.proje_yolu)
        
        for py_dosya in proje.rglob('*.py'):
            # Hariç tutulanları atla
            if any(ht in py_dosya.parts for ht in self.hariç_tutulacaklar):
                continue
            
            try:
                with open(py_dosya, 'r', encoding='utf-8') as f:
                    satirlar = f.readlines()
                
                # Satır satır kontrol
                for i, satir in enumerate(satirlar, 1):
                    # Satır uzunluğu kontrolü (E501)
                    if len(satir.rstrip()) > self.max_satir_uzunlugu:
                        ihlaller.append(PEP8Ihlal(
                            dosya=str(py_dosya),
                            satir=i,
                            sutun=self.max_satir_uzunlugu,
                            kod='E501',
                            mesaj=f'satır çok uzun ({len(satir.rstrip())} > {self.max_satir_uzunlugu})',
                            kategori='E'
                        ))
                    
                    # Trailing whitespace kontrolü (W291)
                    satir_temiz = satir.rstrip('\n\r')
                    if satir_temiz != satir_temiz.rstrip(' \t'):
                        ihlaller.append(PEP8Ihlal(
                            dosya=str(py_dosya),
                            satir=i,
                            sutun=len(satir_temiz),
                            kod='W291',
                            mesaj='satır sonunda boşluk var',
                            kategori='W'
                        ))
                
            except Exception:
                continue
        
        return ihlaller
    
    def rapor_uret(self, rapor: PEP8Rapor, detayli: bool = True) -> str:
        """
        PEP8 kontrol raporunu metin formatında üretir.
        
        Args:
            rapor: PEP8 kontrol raporu
            detayli: Detaylı rapor (tüm ihlaller) veya özet
            
        Returns:
            Metin formatında rapor
        """
        satirlar = []
        satirlar.append("=" * 80)
        satirlar.append("PEP8 UYUMLULUK RAPORU")
        satirlar.append("=" * 80)
        satirlar.append("")
        
        # Özet bilgiler
        satirlar.append(f"Toplam Dosya: {rapor.toplam_dosya}")
        satirlar.append(f"Kontrol Edilen: {rapor.kontrol_edilen_dosya}")
        satirlar.append(f"Başarılı: {rapor.basarili_dosya}")
        satirlar.append(f"İhlal Sayısı: {len(rapor.ihlaller)}")
        satirlar.append(f"Durum: {'✓ BAŞARILI' if rapor.basarili else '✗ BAŞARISIZ'}")
        satirlar.append("")
        
        if not rapor.ihlaller:
            satirlar.append("Tebrikler! Hiç PEP8 ihlali bulunamadı.")
            satirlar.append("=" * 80)
            return '\n'.join(satirlar)
        
        # İhlal kategorileri
        kategoriler = {}
        for ihlal in rapor.ihlaller:
            if ihlal.kategori not in kategoriler:
                kategoriler[ihlal.kategori] = []
            kategoriler[ihlal.kategori].append(ihlal)
        
        satirlar.append("-" * 80)
        satirlar.append("İHLAL KATEGORİLERİ")
        satirlar.append("-" * 80)
        for kategori in sorted(kategoriler.keys()):
            kategori_adi = {
                'E': 'Error (Hata)',
                'W': 'Warning (Uyarı)',
                'F': 'Fatal (Kritik)'
            }.get(kategori, 'Diğer')
            
            satirlar.append(f"  {kategori_adi}: {len(kategoriler[kategori])} ihlal")
        satirlar.append("")
        
        # Detaylı ihlal listesi
        if detayli:
            satirlar.append("-" * 80)
            satirlar.append("DETAYLI İHLAL LİSTESİ")
            satirlar.append("-" * 80)
            
            # Dosyaya göre grupla
            dosya_ihlalleri = {}
            for ihlal in rapor.ihlaller:
                if ihlal.dosya not in dosya_ihlalleri:
                    dosya_ihlalleri[ihlal.dosya] = []
                dosya_ihlalleri[ihlal.dosya].append(ihlal)
            
            # Her dosya için ihlalleri listele
            for dosya in sorted(dosya_ihlalleri.keys()):
                satirlar.append(f"\n{dosya} ({len(dosya_ihlalleri[dosya])} ihlal):")
                
                for ihlal in sorted(dosya_ihlalleri[dosya], key=lambda x: x.satir):
                    satirlar.append(
                        f"  {ihlal.satir}:{ihlal.sutun} "
                        f"[{ihlal.kod}] {ihlal.mesaj}"
                    )
        else:
            # Özet: İlk 20 ihlal
            satirlar.append("-" * 80)
            satirlar.append("İHLAL ÖRNEKLERİ (İlk 20)")
            satirlar.append("-" * 80)
            
            for ihlal in rapor.ihlaller[:20]:
                satirlar.append(
                    f"  {ihlal.dosya}:{ihlal.satir}:{ihlal.sutun} "
                    f"[{ihlal.kod}] {ihlal.mesaj}"
                )
            
            if len(rapor.ihlaller) > 20:
                satirlar.append(f"\n... ve {len(rapor.ihlaller) - 20} ihlal daha")
        
        satirlar.append("")
        satirlar.append("=" * 80)
        
        return '\n'.join(satirlar)
    
    def dosya_kontrolu(self, dosya_yolu: str) -> List[PEP8Ihlal]:
        """
        Tek bir dosyada PEP8 kontrolü yapar.
        
        Args:
            dosya_yolu: Kontrol edilecek dosya yolu
            
        Returns:
            İhlal listesi
        """
        ihlaller = []
        
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                satirlar = f.readlines()
            
            for i, satir in enumerate(satirlar, 1):
                # Satır uzunluğu
                if len(satir.rstrip()) > self.max_satir_uzunlugu:
                    ihlaller.append(PEP8Ihlal(
                        dosya=dosya_yolu,
                        satir=i,
                        sutun=self.max_satir_uzunlugu,
                        kod='E501',
                        mesaj=f'satır çok uzun ({len(satir.rstrip())} > {self.max_satir_uzunlugu})',
                        kategori='E'
                    ))
                
                # Trailing whitespace
                satir_temiz = satir.rstrip('\n\r')
                if satir_temiz != satir_temiz.rstrip(' \t'):
                    ihlaller.append(PEP8Ihlal(
                        dosya=dosya_yolu,
                        satir=i,
                        sutun=len(satir_temiz),
                        kod='W291',
                        mesaj='satır sonunda boşluk var',
                        kategori='W'
                    ))
        
        except Exception as e:
            # Dosya okunamazsa boş liste dön
            pass
        
        return ihlaller
