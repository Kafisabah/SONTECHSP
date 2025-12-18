# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.offline_kuyruk_repository.monitoring
# Description: Kuyruk izleme ve temizlik işlemleri
# Changelog:
# - Refactoring: Ana dosyadan monitoring işlemleri ayrıldı

"""
Kuyruk İzleme ve Temizlik İşlemleri

Bu modül offline kuyruk izleme, istatistik ve temizlik işlemlerini yönetir.
Kuyruk istatistikleri, temizlik ve bakım operasyonları sağlar.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_

from sontechsp.uygulama.veritabani.baglanti import sqlite_session
from sontechsp.uygulama.moduller.pos.arayuzler import KuyrukDurum, IslemTuru
from sontechsp.uygulama.moduller.pos.database.models.offline_kuyruk import OfflineKuyruk
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi, SontechHatasi
)


class Monitoring:
    """
    Kuyruk izleme ve temizlik işlemleri sınıfı
    
    Kuyruk istatistikleri ve bakım operasyonlarını yönetir.
    """
    
    def kuyruk_temizle(self, gun_sayisi: int = 30) -> int:
        """
        Tamamlanan eski kuyruk kayıtlarını temizler
        
        Args:
            gun_sayisi: Kaç gün önceki kayıtlar temizlenecek
            
        Returns:
            Temizlenen kayıt sayısı
            
        Raises:
            DogrulamaHatasi: Geçersiz gün sayısı
            VeritabaniHatasi: Veritabanı hatası
        """
        if gun_sayisi <= 0:
            raise DogrulamaHatasi("Gün sayısı pozitif olmalıdır")
        
        with sqlite_session() as session:
            try:
                # Belirtilen gün sayısından eski tarihi hesapla
                eski_tarih = datetime.now() - timedelta(days=gun_sayisi)
                
                # Tamamlanan eski kayıtları sil
                silinen_sayisi = session.query(OfflineKuyruk).filter(
                    and_(
                        OfflineKuyruk.durum == KuyrukDurum.TAMAMLANDI,
                        OfflineKuyruk.tamamlanma_tarihi < eski_tarih
                    )
                ).delete()
                
                session.commit()
                return silinen_sayisi
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Kuyruk temizleme hatası: {str(e)}")
    
    def kuyruk_istatistikleri(self, terminal_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Kuyruk istatistiklerini getirir
        
        Args:
            terminal_id: Terminal kimliği (opsiyonel)
            
        Returns:
            Kuyruk istatistikleri
            
        Raises:
            VeritabaniHatasi: Veritabanı hatası
        """
        with sqlite_session() as session:
            try:
                query = session.query(OfflineKuyruk)
                
                if terminal_id:
                    query = query.filter(OfflineKuyruk.terminal_id == terminal_id)
                
                tum_kuyruklar = query.all()
                
                # Durum bazında sayılar
                durum_sayilari = {}
                for durum in KuyrukDurum:
                    durum_sayilari[durum.value] = 0
                
                # İşlem türü bazında sayılar
                islem_turu_sayilari = {}
                for turu in IslemTuru:
                    islem_turu_sayilari[turu.value] = 0
                
                # Sayıları hesapla
                for kuyruk in tum_kuyruklar:
                    durum_sayilari[kuyruk.durum.value] += 1
                    islem_turu_sayilari[kuyruk.islem_turu.value] += 1
                
                # Ortalama bekleme süresi (bekleyen kayıtlar için)
                bekleyen_kuyruklar = [k for k in tum_kuyruklar if k.durum == KuyrukDurum.BEKLEMEDE]
                ortalama_bekleme_suresi = 0
                if bekleyen_kuyruklar:
                    toplam_bekleme = sum(
                        (datetime.now() - kuyruk.islem_tarihi).total_seconds()
                        for kuyruk in bekleyen_kuyruklar
                    )
                    ortalama_bekleme_suresi = toplam_bekleme / len(bekleyen_kuyruklar)
                
                return {
                    'toplam_kayit': len(tum_kuyruklar),
                    'durum_sayilari': durum_sayilari,
                    'islem_turu_sayilari': islem_turu_sayilari,
                    'ortalama_bekleme_suresi_saniye': int(ortalama_bekleme_suresi),
                    'terminal_id': terminal_id,
                    'rapor_tarihi': datetime.now().isoformat()
                }
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Kuyruk istatistikleri hatası: {str(e)}")
    
    def kuyruk_temizle_alternatif(self, gun_sayisi: int = 7) -> bool:
        """
        Eski kuyruk kayıtlarını temizler (alternatif metod)
        
        Args:
            gun_sayisi: Kaç gün önceki kayıtları temizleyeceği
            
        Returns:
            İşlem başarılı ise True
            
        Raises:
            VeritabaniHatasi: Veritabanı hatası
        """
        try:
            with sqlite_session() as session:
                temizlik_tarihi = datetime.now() - timedelta(days=gun_sayisi)
                
                # Tamamlanmış ve hatalı kayıtları temizle
                silinen_sayisi = session.query(OfflineKuyruk).filter(
                    and_(
                        OfflineKuyruk.guncelleme_tarihi < temizlik_tarihi,
                        or_(
                            OfflineKuyruk.durum == KuyrukDurum.TAMAMLANDI,
                            OfflineKuyruk.durum == KuyrukDurum.HATA
                        )
                    )
                ).delete()
                
                session.commit()
                return True
                
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Kuyruk temizleme hatası: {str(e)}")
        except Exception as e:
            raise SontechHatasi(f"Kuyruk temizleme işlemi başarısız: {str(e)}")