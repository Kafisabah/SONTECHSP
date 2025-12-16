# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.monitoring
# Description: POS modülü monitoring ve performans izleme sistemi
# Changelog:
# - İlk oluşturma

"""
POS Modülü Monitoring ve Performans İzleme Sistemi

Bu modül POS işlemlerinin detaylı izlenmesi ve performans metriklerinin toplanması için:
- İşlem süre ölçümü
- Başarı/hata oranları
- Günlük işlem istatistikleri
- Performans metrikleri
- Kritik işlem uyarıları
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict, deque
from functools import wraps

from sontechsp.uygulama.cekirdek.kayit import kayit_sistemi_al


@dataclass
class IslemMetrigi:
    """İşlem metrik bilgileri"""
    islem_adi: str
    baslangic_zamani: datetime
    bitis_zamani: Optional[datetime] = None
    sure: Optional[float] = None
    basarili: Optional[bool] = None
    hata_mesaji: Optional[str] = None
    ek_bilgi: Dict[str, Any] = field(default_factory=dict)
    
    def tamamla(self, basarili: bool = True, hata_mesaji: str = None, **ek_bilgi):
        """İşlemi tamamlar ve süreyi hesaplar"""
        self.bitis_zamani = datetime.now()
        self.sure = (self.bitis_zamani - self.baslangic_zamani).total_seconds()
        self.basarili = basarili
        self.hata_mesaji = hata_mesaji
        self.ek_bilgi.update(ek_bilgi)


@dataclass
class PerformansIstatistigi:
    """Performans istatistik bilgileri"""
    islem_adi: str
    toplam_islem: int = 0
    basarili_islem: int = 0
    basarisiz_islem: int = 0
    toplam_sure: float = 0.0
    min_sure: float = float('inf')
    max_sure: float = 0.0
    ortalama_sure: float = 0.0
    son_guncelleme: datetime = field(default_factory=datetime.now)
    
    def guncelle(self, metrik: IslemMetrigi):
        """Metrik ile istatistikleri günceller"""
        self.toplam_islem += 1
        
        if metrik.basarili:
            self.basarili_islem += 1
        else:
            self.basarisiz_islem += 1
        
        if metrik.sure is not None:
            self.toplam_sure += metrik.sure
            self.min_sure = min(self.min_sure, metrik.sure)
            self.max_sure = max(self.max_sure, metrik.sure)
            self.ortalama_sure = self.toplam_sure / self.toplam_islem
        
        self.son_guncelleme = datetime.now()
    
    @property
    def basari_orani(self) -> float:
        """Başarı oranını döndürür"""
        if self.toplam_islem == 0:
            return 0.0
        return (self.basarili_islem / self.toplam_islem) * 100


class POSMonitoring:
    """
    POS Modülü Monitoring Sistemi
    
    POS işlemlerinin performans izleme ve metrik toplama sistemi
    """
    
    def __init__(self, max_metrik_sayisi: int = 1000):
        self.max_metrik_sayisi = max_metrik_sayisi
        self.logger = kayit_sistemi_al()
        
        # Thread-safe koleksiyonlar
        self._lock = threading.RLock()
        
        # Aktif işlemler (thread-safe)
        self._aktif_islemler: Dict[str, IslemMetrigi] = {}
        
        # Tamamlanan işlem metrikleri (son N işlem)
        self._metrikler: deque = deque(maxlen=max_metrik_sayisi)
        
        # İşlem istatistikleri
        self._istatistikler: Dict[str, PerformansIstatistigi] = defaultdict(
            lambda: PerformansIstatistigi("")
        )
        
        # Günlük sayaçlar
        self._gunluk_sayaclar: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        
        # Kritik eşik değerleri (saniye)
        self._kritik_esikler = {
            'sepet_islemleri': 2.0,
            'odeme_islemleri': 5.0,
            'iade_islemleri': 3.0,
            'fis_islemleri': 1.0,
            'stok_islemleri': 1.5
        }
        
        self.logger.info("POS Monitoring sistemi başlatıldı")
    
    def islem_baslat(self, islem_adi: str, **ek_bilgi) -> str:
        """
        İşlem izlemeyi başlatır
        
        Args:
            islem_adi: İşlem adı
            **ek_bilgi: Ek bilgi parametreleri
            
        Returns:
            İşlem ID'si
        """
        islem_id = f"{islem_adi}_{int(time.time() * 1000000)}"
        
        metrik = IslemMetrigi(
            islem_adi=islem_adi,
            baslangic_zamani=datetime.now(),
            ek_bilgi=ek_bilgi
        )
        
        with self._lock:
            self._aktif_islemler[islem_id] = metrik
        
        self.logger.debug(f"İşlem başlatıldı: {islem_adi} (ID: {islem_id})")
        return islem_id
    
    def islem_bitir(self, islem_id: str, basarili: bool = True, 
                   hata_mesaji: str = None, **ek_bilgi) -> Optional[IslemMetrigi]:
        """
        İşlem izlemeyi bitirir
        
        Args:
            islem_id: İşlem ID'si
            basarili: İşlem başarılı mı
            hata_mesaji: Hata mesajı (varsa)
            **ek_bilgi: Ek bilgi parametreleri
            
        Returns:
            Tamamlanan metrik bilgisi
        """
        with self._lock:
            metrik = self._aktif_islemler.pop(islem_id, None)
        
        if metrik is None:
            self.logger.warning(f"Bilinmeyen işlem ID'si: {islem_id}")
            return None
        
        # İşlemi tamamla
        metrik.tamamla(basarili, hata_mesaji, **ek_bilgi)
        
        # Metrikleri kaydet
        with self._lock:
            self._metrikler.append(metrik)
            self._istatistikler[metrik.islem_adi].guncelle(metrik)
            
            # Günlük sayaçları güncelle
            bugun = datetime.now().strftime('%Y-%m-%d')
            self._gunluk_sayaclar[bugun][metrik.islem_adi] += 1
            if basarili:
                self._gunluk_sayaclar[bugun][f"{metrik.islem_adi}_basarili"] += 1
            else:
                self._gunluk_sayaclar[bugun][f"{metrik.islem_adi}_basarisiz"] += 1
        
        # Performans kontrolü
        self._performans_kontrol(metrik)
        
        # Log kaydı
        durum = "BAŞARILI" if basarili else "BAŞARISIZ"
        self.logger.info(
            f"İşlem tamamlandı: {metrik.islem_adi} - {durum} - "
            f"Süre: {metrik.sure:.3f}s"
        )
        
        if not basarili and hata_mesaji:
            self.logger.error(f"İşlem hatası: {metrik.islem_adi} - {hata_mesaji}")
        
        return metrik
    
    def _performans_kontrol(self, metrik: IslemMetrigi):
        """Performans eşik kontrolü yapar"""
        if metrik.sure is None:
            return
        
        # İşlem kategorisini belirle
        kategori = None
        for kat, esik in self._kritik_esikler.items():
            if kat.replace('_islemleri', '') in metrik.islem_adi.lower():
                kategori = kat
                break
        
        if kategori and metrik.sure > self._kritik_esikler[kategori]:
            self.logger.warning(
                f"YAVAŞ İŞLEM UYARISI: {metrik.islem_adi} - "
                f"Süre: {metrik.sure:.3f}s (Eşik: {self._kritik_esikler[kategori]}s)"
            )
    
    def islem_istatistikleri(self, islem_adi: str = None) -> Dict[str, Any]:
        """
        İşlem istatistiklerini döndürür
        
        Args:
            islem_adi: Belirli işlem adı (None ise tümü)
            
        Returns:
            İstatistik bilgileri
        """
        with self._lock:
            if islem_adi:
                if islem_adi in self._istatistikler:
                    stat = self._istatistikler[islem_adi]
                    return {
                        'islem_adi': stat.islem_adi,
                        'toplam_islem': stat.toplam_islem,
                        'basarili_islem': stat.basarili_islem,
                        'basarisiz_islem': stat.basarisiz_islem,
                        'basari_orani': stat.basari_orani,
                        'ortalama_sure': stat.ortalama_sure,
                        'min_sure': stat.min_sure if stat.min_sure != float('inf') else 0,
                        'max_sure': stat.max_sure,
                        'son_guncelleme': stat.son_guncelleme.isoformat()
                    }
                else:
                    return {}
            else:
                # Tüm istatistikler
                return {
                    islem: {
                        'islem_adi': stat.islem_adi,
                        'toplam_islem': stat.toplam_islem,
                        'basarili_islem': stat.basarili_islem,
                        'basarisiz_islem': stat.basarisiz_islem,
                        'basari_orani': stat.basari_orani,
                        'ortalama_sure': stat.ortalama_sure,
                        'min_sure': stat.min_sure if stat.min_sure != float('inf') else 0,
                        'max_sure': stat.max_sure,
                        'son_guncelleme': stat.son_guncelleme.isoformat()
                    }
                    for islem, stat in self._istatistikler.items()
                }
    
    def gunluk_rapor(self, tarih: str = None) -> Dict[str, Any]:
        """
        Günlük işlem raporunu döndürür
        
        Args:
            tarih: Rapor tarihi (YYYY-MM-DD formatında, None ise bugün)
            
        Returns:
            Günlük rapor bilgileri
        """
        if tarih is None:
            tarih = datetime.now().strftime('%Y-%m-%d')
        
        with self._lock:
            gunluk_veri = self._gunluk_sayaclar.get(tarih, {})
        
        # İşlem türlerini grupla
        islem_turleri = set()
        for anahtar in gunluk_veri.keys():
            if not anahtar.endswith(('_basarili', '_basarisiz')):
                islem_turleri.add(anahtar)
        
        rapor = {
            'tarih': tarih,
            'toplam_islem': sum(
                gunluk_veri.get(islem, 0) for islem in islem_turleri
            ),
            'islem_detaylari': {}
        }
        
        for islem in islem_turleri:
            toplam = gunluk_veri.get(islem, 0)
            basarili = gunluk_veri.get(f"{islem}_basarili", 0)
            basarisiz = gunluk_veri.get(f"{islem}_basarisiz", 0)
            
            rapor['islem_detaylari'][islem] = {
                'toplam': toplam,
                'basarili': basarili,
                'basarisiz': basarisiz,
                'basari_orani': (basarili / toplam * 100) if toplam > 0 else 0
            }
        
        return rapor
    
    def performans_raporu(self, son_dakika: int = 60) -> Dict[str, Any]:
        """
        Son N dakikanın performans raporunu döndürür
        
        Args:
            son_dakika: Son kaç dakika
            
        Returns:
            Performans rapor bilgileri
        """
        simdi = datetime.now()
        baslangic = simdi - timedelta(minutes=son_dakika)
        
        # Son N dakikadaki metrikleri filtrele
        son_metrikler = []
        with self._lock:
            for metrik in self._metrikler:
                if metrik.baslangic_zamani >= baslangic:
                    son_metrikler.append(metrik)
        
        if not son_metrikler:
            return {
                'zaman_araligi': f"Son {son_dakika} dakika",
                'toplam_islem': 0,
                'islem_detaylari': {}
            }
        
        # İşlem türlerine göre grupla
        islem_gruplari = defaultdict(list)
        for metrik in son_metrikler:
            islem_gruplari[metrik.islem_adi].append(metrik)
        
        rapor = {
            'zaman_araligi': f"Son {son_dakika} dakika",
            'baslangic_zamani': baslangic.isoformat(),
            'bitis_zamani': simdi.isoformat(),
            'toplam_islem': len(son_metrikler),
            'islem_detaylari': {}
        }
        
        for islem_adi, metrikler in islem_gruplari.items():
            basarili_sayisi = sum(1 for m in metrikler if m.basarili)
            basarisiz_sayisi = len(metrikler) - basarili_sayisi
            
            sureler = [m.sure for m in metrikler if m.sure is not None]
            
            rapor['islem_detaylari'][islem_adi] = {
                'toplam': len(metrikler),
                'basarili': basarili_sayisi,
                'basarisiz': basarisiz_sayisi,
                'basari_orani': (basarili_sayisi / len(metrikler) * 100),
                'ortalama_sure': sum(sureler) / len(sureler) if sureler else 0,
                'min_sure': min(sureler) if sureler else 0,
                'max_sure': max(sureler) if sureler else 0
            }
        
        return rapor
    
    def aktif_islemler(self) -> List[Dict[str, Any]]:
        """
        Aktif işlemleri döndürür
        
        Returns:
            Aktif işlem listesi
        """
        with self._lock:
            return [
                {
                    'islem_id': islem_id,
                    'islem_adi': metrik.islem_adi,
                    'baslangic_zamani': metrik.baslangic_zamani.isoformat(),
                    'gecen_sure': (datetime.now() - metrik.baslangic_zamani).total_seconds(),
                    'ek_bilgi': metrik.ek_bilgi
                }
                for islem_id, metrik in self._aktif_islemler.items()
            ]
    
    def esik_degerlerini_guncelle(self, yeni_esikler: Dict[str, float]):
        """
        Kritik eşik değerlerini günceller
        
        Args:
            yeni_esikler: Yeni eşik değerleri
        """
        self._kritik_esikler.update(yeni_esikler)
        self.logger.info(f"Kritik eşik değerleri güncellendi: {yeni_esikler}")
    
    def istatistikleri_sifirla(self):
        """Tüm istatistikleri sıfırlar"""
        with self._lock:
            self._metrikler.clear()
            self._istatistikler.clear()
            self._gunluk_sayaclar.clear()
        
        self.logger.info("POS Monitoring istatistikleri sıfırlandı")
    
    def sistem_durumu(self) -> Dict[str, Any]:
        """
        Sistem durumu bilgilerini döndürür
        
        Returns:
            Sistem durumu bilgileri
        """
        with self._lock:
            aktif_islem_sayisi = len(self._aktif_islemler)
            toplam_metrik_sayisi = len(self._metrikler)
            
            # Son 5 dakikadaki işlemler
            son_5dk = datetime.now() - timedelta(minutes=5)
            son_islemler = sum(
                1 for metrik in self._metrikler 
                if metrik.baslangic_zamani >= son_5dk
            )
        
        return {
            'aktif_islem_sayisi': aktif_islem_sayisi,
            'toplam_metrik_sayisi': toplam_metrik_sayisi,
            'son_5dk_islem_sayisi': son_islemler,
            'max_metrik_kapasitesi': self.max_metrik_sayisi,
            'kritik_esikler': self._kritik_esikler.copy(),
            'sistem_zamani': datetime.now().isoformat()
        }


def islem_izle(islem_adi: str = None):
    """
    Decorator: Fonksiyon çalışma süresini izler
    
    Args:
        islem_adi: İşlem adı (None ise fonksiyon adı kullanılır)
    
    Usage:
        @islem_izle("sepet_urun_ekleme")
        def urun_ekle(self, barkod):
            # kod
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # İşlem adını belirle
            adi = islem_adi or f"{func.__module__}.{func.__name__}"
            
            # Monitoring instance'ını al
            monitoring = get_pos_monitoring()
            
            # İşlemi başlat
            islem_id = monitoring.islem_baslat(adi)
            
            try:
                # Fonksiyonu çalıştır
                sonuc = func(*args, **kwargs)
                
                # Başarılı olarak bitir
                monitoring.islem_bitir(islem_id, basarili=True)
                
                return sonuc
                
            except Exception as e:
                # Hata ile bitir
                monitoring.islem_bitir(
                    islem_id, 
                    basarili=False, 
                    hata_mesaji=str(e)
                )
                raise
        
        return wrapper
    return decorator


# Global monitoring instance
_pos_monitoring: Optional[POSMonitoring] = None


def get_pos_monitoring() -> POSMonitoring:
    """Global POS monitoring instance'ını döndürür"""
    global _pos_monitoring
    if _pos_monitoring is None:
        _pos_monitoring = POSMonitoring()
    return _pos_monitoring


def pos_monitoring_baslat(max_metrik_sayisi: int = 1000) -> POSMonitoring:
    """
    POS monitoring sistemini başlatır
    
    Args:
        max_metrik_sayisi: Maksimum metrik sayısı
        
    Returns:
        POSMonitoring instance'ı
    """
    global _pos_monitoring
    _pos_monitoring = POSMonitoring(max_metrik_sayisi)
    return _pos_monitoring