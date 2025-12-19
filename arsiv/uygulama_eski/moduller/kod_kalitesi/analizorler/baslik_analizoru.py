# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.analizorler.baslik_analizoru
# Description: Dosya başlık standardizasyonu ve analizi
# Changelog:
# - İlk versiyon: BaslikAnalizoru sınıfı oluşturuldu

"""
Başlık Analizörü

Python dosyalarındaki standart başlık formatını kontrol eder,
eksik başlıkları tespit eder ve otomatik güncelleme yapar.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class BaslikBilgisi:
    """Dosya başlık bilgileri"""
    version: Optional[str]
    last_update: Optional[str]
    module: Optional[str]
    description: Optional[str]
    changelog: List[str]
    
    def eksik_alanlar(self) -> List[str]:
        """Eksik olan başlık alanlarını döndürür"""
        eksikler = []
        if not self.version:
            eksikler.append('version')
        if not self.last_update:
            eksikler.append('last_update')
        if not self.module:
            eksikler.append('module')
        if not self.description:
            eksikler.append('description')
        if not self.changelog:
            eksikler.append('changelog')
        return eksikler


@dataclass
class BaslikRaporu:
    """Başlık analiz raporu"""
    dosya_yolu: str
    baslik_var: bool
    baslik_bilgisi: Optional[BaslikBilgisi]
    eksik_alanlar: List[str]
    standart_uyumlu: bool


class BaslikAnalizoru:
    """
    Dosya başlık analizi ve güncelleme yapan sınıf.
    
    Standart başlık formatını kontrol eder ve otomatik
    güncelleme işlemleri yapar.
    """
    
    STANDART_FORMAT = """# Version: {version}
# Last Update: {last_update}
# Module: {module}
# Description: {description}
# Changelog:
{changelog}
"""
    
    def __init__(self):
        """Başlık analizörü başlatıcı"""
        pass
    
    def dosya_basligini_analiz_et(
        self, 
        dosya_yolu: str
    ) -> BaslikRaporu:
        """
        Dosya başlığını analiz eder.
        
        Args:
            dosya_yolu: Analiz edilecek dosya yolu
            
        Returns:
            Başlık analiz raporu
        """
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
        except Exception:
            return BaslikRaporu(
                dosya_yolu=dosya_yolu,
                baslik_var=False,
                baslik_bilgisi=None,
                eksik_alanlar=[],
                standart_uyumlu=False
            )
        
        baslik_bilgisi = self._baslik_bilgisini_cikart(icerik)
        
        if baslik_bilgisi is None:
            return BaslikRaporu(
                dosya_yolu=dosya_yolu,
                baslik_var=False,
                baslik_bilgisi=None,
                eksik_alanlar=['version', 'last_update', 'module', 
                              'description', 'changelog'],
                standart_uyumlu=False
            )
        
        eksik_alanlar = baslik_bilgisi.eksik_alanlar()
        standart_uyumlu = len(eksik_alanlar) == 0
        
        return BaslikRaporu(
            dosya_yolu=dosya_yolu,
            baslik_var=True,
            baslik_bilgisi=baslik_bilgisi,
            eksik_alanlar=eksik_alanlar,
            standart_uyumlu=standart_uyumlu
        )

    def klasor_basliklarini_analiz_et(
        self,
        klasor_yolu: str,
        hariç_tutulacaklar: List[str] = None
    ) -> List[BaslikRaporu]:
        """
        Klasördeki tüm dosyaların başlıklarını analiz eder.
        
        Args:
            klasor_yolu: Taranacak klasör yolu
            hariç_tutulacaklar: Hariç tutulacak klasör/dosya isimleri
            
        Returns:
            Başlık analiz raporları listesi
        """
        if hariç_tutulacaklar is None:
            hariç_tutulacaklar = [
                '__pycache__', '.git', '.pytest_cache',
                'venv', 'env', '.hypothesis'
            ]
        
        raporlar = []
        klasor = Path(klasor_yolu)
        
        for py_dosya in klasor.rglob('*.py'):
            # Hariç tutulanları atla
            if any(ht in py_dosya.parts for ht in hariç_tutulacaklar):
                continue
            
            rapor = self.dosya_basligini_analiz_et(str(py_dosya))
            raporlar.append(rapor)
        
        return raporlar
    
    def baslik_ekle(
        self,
        dosya_yolu: str,
        modul_adi: str,
        aciklama: str,
        version: str = "0.1.0",
        changelog_maddesi: str = "İlk versiyon"
    ) -> bool:
        """
        Dosyaya standart başlık ekler.
        
        Args:
            dosya_yolu: Hedef dosya yolu
            modul_adi: Modül adı
            aciklama: Kısa açıklama
            version: Versiyon numarası
            changelog_maddesi: Changelog maddesi
            
        Returns:
            Başarılı ise True
        """
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                mevcut_icerik = f.read()
        except Exception:
            return False
        
        # Eğer başlık varsa ekleme
        if self._baslik_var_mi(mevcut_icerik):
            return False
        
        bugun = datetime.now().strftime('%Y-%m-%d')
        # Whitespace karakterlerini temizle
        changelog_satir = f"# - {changelog_maddesi.strip()}"
        
        yeni_baslik = self.STANDART_FORMAT.format(
            version=version.strip(),
            last_update=bugun,
            module=modul_adi.strip(),
            description=aciklama.strip(),
            changelog=changelog_satir
        )
        
        yeni_icerik = yeni_baslik + "\n" + mevcut_icerik
        
        try:
            with open(dosya_yolu, 'w', encoding='utf-8') as f:
                f.write(yeni_icerik)
            return True
        except Exception:
            return False
    
    def baslik_guncelle(
        self,
        dosya_yolu: str,
        yeni_changelog_maddesi: Optional[str] = None,
        yeni_version: Optional[str] = None
    ) -> bool:
        """
        Mevcut başlığı günceller.
        
        Args:
            dosya_yolu: Hedef dosya yolu
            yeni_changelog_maddesi: Eklenecek changelog maddesi
            yeni_version: Yeni versiyon numarası
            
        Returns:
            Başarılı ise True
        """
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
        except Exception:
            return False
        
        baslik_bilgisi = self._baslik_bilgisini_cikart(icerik)
        if baslik_bilgisi is None:
            return False
        
        # Tarihi güncelle
        bugun = datetime.now().strftime('%Y-%m-%d')
        
        # Version güncelle
        if yeni_version:
            baslik_bilgisi.version = yeni_version
        
        # Changelog güncelle
        if yeni_changelog_maddesi:
            baslik_bilgisi.changelog.append(yeni_changelog_maddesi)
        
        # Yeni başlık oluştur
        changelog_satirlari = "\n".join(
            [f"# - {madde}" for madde in baslik_bilgisi.changelog]
        )
        
        yeni_baslik = self.STANDART_FORMAT.format(
            version=baslik_bilgisi.version or "0.1.0",
            last_update=bugun,
            module=baslik_bilgisi.module or "",
            description=baslik_bilgisi.description or "",
            changelog=changelog_satirlari
        )
        
        # Eski başlığı çıkar ve yeni başlık ekle
        icerik_satirlari = icerik.split('\n')
        baslik_bitis = self._baslik_bitis_satirini_bul(icerik_satirlari)
        
        if baslik_bitis == -1:
            return False
        
        yeni_icerik = yeni_baslik + "\n" + "\n".join(
            icerik_satirlari[baslik_bitis + 1:]
        )
        
        try:
            with open(dosya_yolu, 'w', encoding='utf-8') as f:
                f.write(yeni_icerik)
            return True
        except Exception:
            return False

    def _baslik_bilgisini_cikart(
        self, 
        icerik: str
    ) -> Optional[BaslikBilgisi]:
        """
        İçerikten başlık bilgilerini çıkartır.
        
        Args:
            icerik: Dosya içeriği
            
        Returns:
            Başlık bilgisi veya None
        """
        satirlar = icerik.split('\n')
        
        # İlk satır # ile başlamalı
        if not satirlar or not satirlar[0].strip().startswith('#'):
            return None
        
        version = None
        last_update = None
        module = None
        description = None
        changelog = []
        
        changelog_basladi = False
        
        for satir in satirlar:
            temiz_satir = satir.strip()
            
            # Başlık bitişi
            if not temiz_satir.startswith('#'):
                break
            
            # Version
            if 'Version:' in temiz_satir:
                version = temiz_satir.split('Version:')[1].strip()
            
            # Last Update
            elif 'Last Update:' in temiz_satir:
                last_update = temiz_satir.split('Last Update:')[1].strip()
            
            # Module
            elif 'Module:' in temiz_satir:
                module = temiz_satir.split('Module:')[1].strip()
            
            # Description
            elif 'Description:' in temiz_satir:
                description = temiz_satir.split('Description:')[1].strip()
            
            # Changelog
            elif 'Changelog:' in temiz_satir:
                changelog_basladi = True
            elif changelog_basladi and temiz_satir.startswith('# -'):
                madde = temiz_satir.replace('# -', '').strip()
                changelog.append(madde)
        
        # Hiçbir alan bulunamadıysa None dön
        if not any([version, last_update, module, description, changelog]):
            return None
        
        return BaslikBilgisi(
            version=version,
            last_update=last_update,
            module=module,
            description=description,
            changelog=changelog
        )
    
    def _baslik_var_mi(self, icerik: str) -> bool:
        """
        İçerikte standart başlık var mı kontrol eder.
        
        Args:
            icerik: Dosya içeriği
            
        Returns:
            Başlık varsa True
        """
        return self._baslik_bilgisini_cikart(icerik) is not None
    
    def _baslik_bitis_satirini_bul(
        self, 
        satirlar: List[str]
    ) -> int:
        """
        Başlığın bittiği satır numarasını bulur.
        
        Args:
            satirlar: Dosya satırları
            
        Returns:
            Başlık bitiş satır numarası, bulunamazsa -1
        """
        for i, satir in enumerate(satirlar):
            temiz_satir = satir.strip()
            
            # Boş satır veya # ile başlamayan satır
            if temiz_satir and not temiz_satir.startswith('#'):
                return i - 1
        
        return -1
    
    def standart_baslik_olustur(
        self,
        modul_adi: str,
        aciklama: str,
        version: str = "0.1.0",
        changelog_maddesi: str = "İlk versiyon"
    ) -> str:
        """
        Standart başlık metni oluşturur.
        
        Args:
            modul_adi: Modül adı
            aciklama: Kısa açıklama
            version: Versiyon numarası
            changelog_maddesi: Changelog maddesi
            
        Returns:
            Standart başlık metni
        """
        bugun = datetime.now().strftime('%Y-%m-%d')
        changelog_satir = f"# - {changelog_maddesi}"
        
        return self.STANDART_FORMAT.format(
            version=version,
            last_update=bugun,
            module=modul_adi,
            description=aciklama,
            changelog=changelog_satir
        )


    def tum_dosyalari_standardize_et(
        self,
        klasor_yolu: str,
        hariç_tutulacaklar: List[str] = None
    ) -> Dict[str, bool]:
        """
        Tüm dosyaları standart başlık formatına getirir.
        
        Args:
            klasor_yolu: Taranacak klasör yolu
            hariç_tutulacaklar: Hariç tutulacak klasör/dosya isimleri
            
        Returns:
            Dosya yolu -> başarı durumu dict'i
        """
        raporlar = self.klasor_basliklarini_analiz_et(
            klasor_yolu,
            hariç_tutulacaklar
        )
        
        sonuclar = {}
        
        for rapor in raporlar:
            if rapor.standart_uyumlu:
                sonuclar[rapor.dosya_yolu] = True
                continue
            
            if not rapor.baslik_var:
                # Başlık yok, ekle
                modul_adi = self._dosya_yolundan_modul_adi_cikart(rapor.dosya_yolu)
                basari = self.baslik_ekle(
                    rapor.dosya_yolu,
                    modul_adi=modul_adi,
                    aciklama="Otomatik oluşturuldu"
                )
                sonuclar[rapor.dosya_yolu] = basari
            else:
                # Başlık var ama eksik alanlar var
                # Eksik alanları doldur
                bilgi = rapor.baslik_bilgisi
                if not bilgi.description or not bilgi.description.strip():
                    # Description eksikse, dosyayı yeniden oluştur
                    modul_adi = bilgi.module or self._dosya_yolundan_modul_adi_cikart(rapor.dosya_yolu)
                    
                    # Eski başlığı sil ve yenisini ekle
                    try:
                        with open(rapor.dosya_yolu, 'r', encoding='utf-8') as f:
                            icerik = f.read()
                        
                        # Başlık sonrasını al
                        satirlar = icerik.split('\n')
                        baslik_bitis = self._baslik_bitis_satirini_bul(satirlar)
                        kod_kismi = "\n".join(satirlar[baslik_bitis + 1:])
                        
                        # Yeni başlık oluştur
                        yeni_baslik = self.standart_baslik_olustur(
                            modul_adi=modul_adi,
                            aciklama="Otomatik oluşturuldu",
                            version=bilgi.version or "0.1.0",
                            changelog_maddesi="Başlık standardizasyonu"
                        )
                        
                        # Dosyayı yaz
                        with open(rapor.dosya_yolu, 'w', encoding='utf-8') as f:
                            f.write(yeni_baslik + "\n" + kod_kismi)
                        
                        sonuclar[rapor.dosya_yolu] = True
                    except Exception:
                        sonuclar[rapor.dosya_yolu] = False
                else:
                    # Sadece güncelle
                    basari = self.baslik_guncelle(
                        rapor.dosya_yolu,
                        yeni_changelog_maddesi="Başlık standardizasyonu"
                    )
                    sonuclar[rapor.dosya_yolu] = basari
        
        return sonuclar
    
    def _dosya_yolundan_modul_adi_cikart(self, dosya_yolu: str) -> str:
        """
        Dosya yolundan modül adı çıkartır.
        
        Args:
            dosya_yolu: Dosya yolu
            
        Returns:
            Modül adı
        """
        yol = Path(dosya_yolu)
        
        # .py uzantısını çıkar
        dosya_adi = yol.stem
        
        # Üst klasörleri al
        parcalar = list(yol.parts)
        
        # uygulama/ veya sontechsp/ sonrasını al
        try:
            if 'uygulama' in parcalar:
                baslangic = parcalar.index('uygulama')
            elif 'sontechsp' in parcalar:
                baslangic = parcalar.index('sontechsp')
            else:
                baslangic = 0
            
            modul_parcalari = parcalar[baslangic:-1] + [dosya_adi]
            return '.'.join(modul_parcalari)
        except (ValueError, IndexError):
            return dosya_adi

