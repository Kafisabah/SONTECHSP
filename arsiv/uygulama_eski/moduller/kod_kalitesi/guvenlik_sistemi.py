# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.guvenlik_sistemi
# Description: Güvenlik ve geri alma sistemi - backup/restore mekanizması
# Changelog:
# - İlk versiyon: GuvenlikSistemi sınıfı oluşturuldu
# - Yedek silme, hash hesaplama ve log yönetimi fonksiyonları eklendi

"""
Güvenlik Sistemi

Refactoring işlemleri için güvenlik sağlayan, backup/restore
mekanizması ve işlem logları yöneten sistem.
"""

import hashlib
import json
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class YedekBilgisi:
    """Yedek bilgi yapısı"""
    yedek_id: str
    olusturma_zamani: datetime
    proje_yolu: str
    yedek_yolu: str
    dosya_sayisi: int
    toplam_boyut: int
    aciklama: str


@dataclass
class IslemLogu:
    """İşlem log yapısı"""
    islem_id: str
    zaman: datetime
    islem_turu: str
    dosya_yolu: str
    onceki_hash: str
    sonraki_hash: str
    basarili: bool
    hata_mesaji: Optional[str] = None


class GuvenlikSistemi:
    """
    Güvenlik ve geri alma sistemi.
    
    Refactoring işlemleri için backup/restore mekanizması,
    işlem logları ve audit trail sağlar.
    """
    
    def __init__(
        self,
        proje_yolu: str = ".",
        yedek_dizini: Optional[str] = None,
        log_dosyasi: Optional[str] = None
    ):
        """
        Args:
            proje_yolu: Korunacak proje yolu
            yedek_dizini: Yedeklerin saklanacağı dizin
            log_dosyasi: İşlem loglarının yazılacağı dosya
        """
        self.proje_yolu = Path(proje_yolu)
        
        # Yedek dizini
        if yedek_dizini:
            self.yedek_dizini = Path(yedek_dizini)
        else:
            self.yedek_dizini = Path(tempfile.gettempdir()) / "kod_kalitesi_yedek"
        
        self.yedek_dizini.mkdir(parents=True, exist_ok=True)
        
        # Log dosyası
        if log_dosyasi:
            self.log_dosyasi = Path(log_dosyasi)
        else:
            self.log_dosyasi = self.yedek_dizini / "islem_loglari.json"
        
        # Hariç tutulacak dosya/klasörler
        self.hariç_tutulacaklar = [
            '__pycache__', '*.pyc', '.git', '.pytest_cache',
            'venv', 'env', '.hypothesis', 'htmlcov', '*.db'
        ]
        
        # Mevcut işlem logları
        self.islem_loglari: List[IslemLogu] = []
        self._loglari_yukle()
    
    def yedek_al(self, aciklama: str = "Otomatik yedek") -> YedekBilgisi:
        """
        Proje yedeği alır.
        
        Args:
            aciklama: Yedek açıklaması
            
        Returns:
            Yedek bilgisi
        """
        # Yedek ID oluştur
        zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
        yedek_id = f"yedek_{zaman_damgasi}"
        
        # Yedek klasörü
        yedek_klasoru = self.yedek_dizini / yedek_id
        
        # Projeyi kopyala
        shutil.copytree(
            self.proje_yolu,
            yedek_klasoru,
            ignore=shutil.ignore_patterns(*self.hariç_tutulacaklar)
        )
        
        # Yedek bilgilerini hesapla
        dosya_sayisi, toplam_boyut = self._yedek_istatistikleri_hesapla(yedek_klasoru)
        
        # Yedek bilgisi oluştur
        yedek_bilgisi = YedekBilgisi(
            yedek_id=yedek_id,
            olusturma_zamani=datetime.now(),
            proje_yolu=str(self.proje_yolu),
            yedek_yolu=str(yedek_klasoru),
            dosya_sayisi=dosya_sayisi,
            toplam_boyut=toplam_boyut,
            aciklama=aciklama
        )
        
        # Yedek bilgisini kaydet
        self._yedek_bilgisini_kaydet(yedek_bilgisi)
        
        return yedek_bilgisi
    
    def yedek_geri_yukle(self, yedek_id: str) -> bool:
        """
        Belirtilen yedeği geri yükler.
        
        Args:
            yedek_id: Geri yüklenecek yedek ID'si
            
        Returns:
            Başarılı mı?
        """
        try:
            # Yedek klasörünü bul
            yedek_klasoru = self.yedek_dizini / yedek_id
            
            if not yedek_klasoru.exists():
                raise FileNotFoundError(f"Yedek bulunamadı: {yedek_id}")
            
            # Mevcut projeyi geçici olarak yedekle
            gecici_yedek = self.yedek_al("Geri yükleme öncesi geçici yedek")
            
            try:
                # Mevcut proje dosyalarını sil
                self._proje_dosyalarini_sil()
                
                # Yedeği geri kopyala
                shutil.copytree(
                    yedek_klasoru,
                    self.proje_yolu,
                    dirs_exist_ok=True
                )
                
                # İşlem loguna kaydet
                self._islem_logu_ekle(
                    islem_turu="yedek_geri_yukle",
                    dosya_yolu=str(self.proje_yolu),
                    basarili=True
                )
                
                return True
                
            except Exception as e:
                # Hata durumunda geçici yedeği geri yükle
                self.yedek_geri_yukle(gecici_yedek.yedek_id)
                raise e
                
        except Exception as e:
            # İşlem loguna hata kaydet
            self._islem_logu_ekle(
                islem_turu="yedek_geri_yukle",
                dosya_yolu=str(self.proje_yolu),
                basarili=False,
                hata_mesaji=str(e)
            )
            return False
    
    def yedekleri_listele(self) -> List[YedekBilgisi]:
        """
        Mevcut yedekleri listeler.
        
        Returns:
            Yedek bilgileri listesi
        """
        yedekler = []
        
        # Yedek klasörlerini tara
        for yedek_klasoru in self.yedek_dizini.iterdir():
            if yedek_klasoru.is_dir() and yedek_klasoru.name.startswith("yedek_"):
                bilgi_dosyasi = yedek_klasoru / "yedek_bilgisi.json"
                
                if bilgi_dosyasi.exists():
                    try:
                        with open(bilgi_dosyasi, 'r', encoding='utf-8') as f:
                            bilgi_data = json.load(f)
                        
                        yedek_bilgisi = YedekBilgisi(
                            yedek_id=bilgi_data['yedek_id'],
                            olusturma_zamani=datetime.fromisoformat(
                                bilgi_data['olusturma_zamani']
                            ),
                            proje_yolu=bilgi_data['proje_yolu'],
                            yedek_yolu=bilgi_data['yedek_yolu'],
                            dosya_sayisi=bilgi_data['dosya_sayisi'],
                            toplam_boyut=bilgi_data['toplam_boyut'],
                            aciklama=bilgi_data['aciklama']
                        )
                        
                        yedekler.append(yedek_bilgisi)
                        
                    except Exception:
                        continue
        
        # Tarihe göre sırala (en yeni önce)
        yedekler.sort(key=lambda x: x.olusturma_zamani, reverse=True)
        
        return yedekler
    
    def yedek_sil(self, yedek_id: str) -> bool:
        """
        Belirtilen yedeği siler.
        
        Args:
            yedek_id: Silinecek yedek ID'si
            
        Returns:
            Başarılı mı?
        """
        try:
            yedek_klasoru = self.yedek_dizini / yedek_id
            
            if yedek_klasoru.exists():
                shutil.rmtree(yedek_klasoru)
                return True
            
            return False
            
        except Exception:
            return False
    
    def dosya_hash_hesapla(self, dosya_yolu: str) -> str:
        """
        Dosyanın MD5 hash'ini hesaplar.
        
        Args:
            dosya_yolu: Hash hesaplanacak dosya
            
        Returns:
            MD5 hash değeri
        """
        try:
            with open(dosya_yolu, 'rb') as f:
                dosya_icerik = f.read()
            
            return hashlib.md5(dosya_icerik).hexdigest()
            
        except Exception:
            return ""
    
    def islem_logu_ekle(
        self,
        islem_turu: str,
        dosya_yolu: str,
        onceki_hash: str = "",
        sonraki_hash: str = "",
        basarili: bool = True,
        hata_mesaji: Optional[str] = None
    ) -> None:
        """
        İşlem loguna yeni kayıt ekler.
        
        Args:
            islem_turu: İşlem türü
            dosya_yolu: İşlem yapılan dosya
            onceki_hash: İşlem öncesi hash
            sonraki_hash: İşlem sonrası hash
            basarili: İşlem başarılı mı?
            hata_mesaji: Hata mesajı (varsa)
        """
        self._islem_logu_ekle(
            islem_turu, dosya_yolu, onceki_hash,
            sonraki_hash, basarili, hata_mesaji
        )
    
    def islem_loglarini_getir(
        self,
        baslangic_tarihi: Optional[datetime] = None,
        bitis_tarihi: Optional[datetime] = None,
        islem_turu: Optional[str] = None
    ) -> List[IslemLogu]:
        """
        İşlem loglarını filtreli olarak getirir.
        
        Args:
            baslangic_tarihi: Başlangıç tarihi
            bitis_tarihi: Bitiş tarihi
            islem_turu: İşlem türü filtresi
            
        Returns:
            Filtrelenmiş işlem logları
        """
        filtreli_loglar = self.islem_loglari.copy()
        
        # Tarih filtresi
        if baslangic_tarihi:
            filtreli_loglar = [
                log for log in filtreli_loglar
                if log.zaman >= baslangic_tarihi
            ]
        
        if bitis_tarihi:
            filtreli_loglar = [
                log for log in filtreli_loglar
                if log.zaman <= bitis_tarihi
            ]
        
        # İşlem türü filtresi
        if islem_turu:
            filtreli_loglar = [
                log for log in filtreli_loglar
                if log.islem_turu == islem_turu
            ]
        
        return filtreli_loglar
    
    def _yedek_istatistikleri_hesapla(self, yedek_yolu: Path) -> tuple:
        """Yedek istatistiklerini hesaplar."""
        dosya_sayisi = 0
        toplam_boyut = 0
        
        for dosya in yedek_yolu.rglob('*'):
            if dosya.is_file():
                dosya_sayisi += 1
                try:
                    toplam_boyut += dosya.stat().st_size
                except Exception:
                    pass
        
        return dosya_sayisi, toplam_boyut
    
    def _yedek_bilgisini_kaydet(self, yedek_bilgisi: YedekBilgisi) -> None:
        """Yedek bilgisini JSON dosyasına kaydeder."""
        bilgi_dosyasi = Path(yedek_bilgisi.yedek_yolu) / "yedek_bilgisi.json"
        
        bilgi_data = {
            'yedek_id': yedek_bilgisi.yedek_id,
            'olusturma_zamani': yedek_bilgisi.olusturma_zamani.isoformat(),
            'proje_yolu': yedek_bilgisi.proje_yolu,
            'yedek_yolu': yedek_bilgisi.yedek_yolu,
            'dosya_sayisi': yedek_bilgisi.dosya_sayisi,
            'toplam_boyut': yedek_bilgisi.toplam_boyut,
            'aciklama': yedek_bilgisi.aciklama
        }
        
        with open(bilgi_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(bilgi_data, f, indent=2, ensure_ascii=False)
    
    def _proje_dosyalarini_sil(self) -> None:
        """Mevcut proje dosyalarını siler (dikkatli!)."""
        for item in self.proje_yolu.iterdir():
            # Hariç tutulanları atla
            if any(pattern in item.name for pattern in self.hariç_tutulacaklar):
                continue
            
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    
    def _islem_logu_ekle(
        self,
        islem_turu: str,
        dosya_yolu: str,
        onceki_hash: str = "",
        sonraki_hash: str = "",
        basarili: bool = True,
        hata_mesaji: Optional[str] = None
    ) -> None:
        """İşlem loguna kayıt ekler."""
        islem_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.islem_loglari)}"
        
        log = IslemLogu(
            islem_id=islem_id,
            zaman=datetime.now(),
            islem_turu=islem_turu,
            dosya_yolu=dosya_yolu,
            onceki_hash=onceki_hash,
            sonraki_hash=sonraki_hash,
            basarili=basarili,
            hata_mesaji=hata_mesaji
        )
        
        self.islem_loglari.append(log)
        self._loglari_kaydet()
    
    def _loglari_yukle(self) -> None:
        """Mevcut logları dosyadan yükler."""
        if not self.log_dosyasi.exists():
            return
        
        try:
            with open(self.log_dosyasi, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            for log_item in log_data:
                log = IslemLogu(
                    islem_id=log_item['islem_id'],
                    zaman=datetime.fromisoformat(log_item['zaman']),
                    islem_turu=log_item['islem_turu'],
                    dosya_yolu=log_item['dosya_yolu'],
                    onceki_hash=log_item['onceki_hash'],
                    sonraki_hash=log_item['sonraki_hash'],
                    basarili=log_item['basarili'],
                    hata_mesaji=log_item.get('hata_mesaji')
                )
                self.islem_loglari.append(log)
                
        except Exception:
            # Log dosyası bozuksa boş liste ile devam et
            self.islem_loglari = []
    
    def _loglari_kaydet(self) -> None:
        """Logları dosyaya kaydeder."""
        log_data = []
        
        for log in self.islem_loglari:
            log_item = {
                'islem_id': log.islem_id,
                'zaman': log.zaman.isoformat(),
                'islem_turu': log.islem_turu,
                'dosya_yolu': log.dosya_yolu,
                'onceki_hash': log.onceki_hash,
                'sonraki_hash': log.sonraki_hash,
                'basarili': log.basarili,
                'hata_mesaji': log.hata_mesaji
            }
            log_data.append(log_item)
        
        with open(self.log_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)