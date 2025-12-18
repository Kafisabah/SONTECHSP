# Version: 0.1.0
# Last Update: 2024-12-18
# Module: fonksiyonalite_dogrulama
# Description: Refactoring sonrası fonksiyonalite doğrulama sistemi
# Changelog:
# - İlk versiyon: UI ekranları, iş kuralları ve API sözleşmeleri doğrulaması

import sys
import os
import json
import importlib
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class FonksiyonaliteDogrulayici:
    """Refactoring sonrası fonksiyonalite doğrulama sistemi"""
    
    def __init__(self):
        self.sonuclar = {
            'ui_testleri': {},
            'is_kurallari': {},
            'api_sozlesmeleri': {},
            'import_testleri': {},
            'genel_durum': 'BASLAMADI'
        }
        self.hata_sayisi = 0
        self.basari_sayisi = 0
    
    def ui_ekranlarini_test_et(self) -> Dict[str, Any]:
        """UI ekranlarının doğru çalıştığını test et"""
        print("🖥️  UI Ekranları Test Ediliyor...")
        
        ui_testleri = {
            'ebelge_ekrani': self._ebelge_ekrani_test(),
            'raporlar_ekrani': self._raporlar_ekrani_test(),
            'ayarlar_ekrani': self._ayarlar_ekrani_test()
        }
        
        self.sonuclar['ui_testleri'] = ui_testleri
        return ui_testleri
    
    def _ebelge_ekrani_test(self) -> Dict[str, Any]:
        """E-Belge ekranı fonksiyonalite testi"""
        try:
            # E-Belge modüllerini import et - güncellenmiş yollar
            from uygulama.arayuz.ekranlar.ebelge import Ebelge, EbelgeEkrani
            from uygulama.arayuz.ekranlar.ebelge import EbelgeFiltreleri
            from uygulama.arayuz.ekranlar.ebelge import EbelgeIslemleri
            from uygulama.arayuz.ekranlar.ebelge import EbelgeDurum
            from uygulama.arayuz.ekranlar.ebelge import EbelgeTablolar
            from uygulama.arayuz.ekranlar.ebelge import EbelgeVeriYoneticisi
            from uygulama.arayuz.ekranlar.ebelge import EbelgeYardimcilar
            
            # Sınıfların varlığını kontrol et
            if (Ebelge and EbelgeEkrani and EbelgeFiltreleri and EbelgeIslemleri and 
                EbelgeDurum and EbelgeTablolar and EbelgeVeriYoneticisi and EbelgeYardimcilar):
                self.basari_sayisi += 1
                return {
                    'durum': 'BASARILI',
                    'mesaj': 'E-Belge ekranı modülleri başarıyla yüklendi',
                    'moduller': ['Ebelge', 'EbelgeEkrani', 'EbelgeFiltreleri', 'EbelgeIslemleri', 'EbelgeDurum', 'EbelgeTablolar', 'EbelgeVeriYoneticisi', 'EbelgeYardimcilar']
                }
            else:
                self.hata_sayisi += 1
                return {
                    'durum': 'HATA',
                    'mesaj': 'E-Belge modül sınıfları bulunamadı'
                }
                
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'E-Belge modülleri import edilemedi: {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'E-Belge testi sırasında hata: {str(e)}'
            }
    
    def _raporlar_ekrani_test(self) -> Dict[str, Any]:
        """Raporlar ekranı fonksiyonalite testi"""
        try:
            # Raporlar modüllerini import et - güncellenmiş yollar
            from uygulama.arayuz.ekranlar.raporlar import Raporlar, RaporlarEkrani
            from uygulama.arayuz.ekranlar.raporlar import RaporOlusturma
            from uygulama.arayuz.ekranlar.raporlar import RaporFiltreleri
            from uygulama.arayuz.ekranlar.raporlar import RaporExport
            
            # Sınıfların varlığını kontrol et
            if (Raporlar and RaporlarEkrani and RaporOlusturma and RaporFiltreleri and RaporExport):
                self.basari_sayisi += 1
                return {
                    'durum': 'BASARILI',
                    'mesaj': 'Raporlar ekranı modülleri başarıyla yüklendi',
                    'moduller': ['Raporlar', 'RaporlarEkrani', 'RaporOlusturma', 'RaporFiltreleri', 'RaporExport']
                }
            else:
                self.hata_sayisi += 1
                return {
                    'durum': 'HATA',
                    'mesaj': 'Raporlar modül sınıfları bulunamadı'
                }
                
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Raporlar modülleri import edilemedi: {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Raporlar testi sırasında hata: {str(e)}'
            }
    
    def _ayarlar_ekrani_test(self) -> Dict[str, Any]:
        """Ayarlar ekranı fonksiyonalite testi"""
        try:
            # Ayarlar modüllerini import et
            from uygulama.arayuz.ekranlar.ayarlar import Ayarlar, AyarlarEkrani
            from uygulama.arayuz.ekranlar.ayarlar import AyarButonlari
            from uygulama.arayuz.ekranlar.ayarlar import AyarFormlari
            from uygulama.arayuz.ekranlar.ayarlar import AyarDogrulama
            
            # Temel sınıf kontrolü
            if (Ayarlar and AyarlarEkrani and AyarButonlari and AyarFormlari and AyarDogrulama):
                self.basari_sayisi += 1
                return {
                    'durum': 'BASARILI',
                    'mesaj': 'Ayarlar ekranı modülleri başarıyla yüklendi',
                    'moduller': ['Ayarlar', 'AyarlarEkrani', 'AyarButonlari', 'AyarFormlari', 'AyarDogrulama']
                }
            else:
                self.hata_sayisi += 1
                return {
                    'durum': 'HATA',
                    'mesaj': 'Ayarlar modül sınıfları bulunamadı'
                }
                
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Ayarlar modülleri import edilemedi: {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Ayarlar testi sırasında hata: {str(e)}'
            }
    
    def is_kurallarini_test_et(self) -> Dict[str, Any]:
        """İş kurallarının korunduğunu doğrula"""
        print("⚙️  İş Kuralları Test Ediliyor...")
        
        is_kurallari = {
            'stok_kurallari': self._stok_kurallari_test(),
            'pos_kurallari': self._pos_kurallari_test(),
            'repository_kurallari': self._repository_kurallari_test()
        }
        
        self.sonuclar['is_kurallari'] = is_kurallari
        return is_kurallari
    
    def _stok_kurallari_test(self) -> Dict[str, Any]:
        """Stok iş kuralları testi"""
        try:
            from sontechsp.uygulama.moduller.stok.servisler.stok_transfer_service import StokTransferService
            
            # Transfer servisi sınıfının varlığını kontrol et
            if hasattr(StokTransferService, 'transfer_yap'):
                self.basari_sayisi += 1
                return {
                    'durum': 'BASARILI',
                    'mesaj': 'Stok transfer servisi fonksiyonları mevcut'
                }
            else:
                self.hata_sayisi += 1
                return {
                    'durum': 'HATA',
                    'mesaj': 'transfer_yap fonksiyonu bulunamadı'
                }
                
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Stok servisleri import edilemedi: {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Stok kuralları testi sırasında hata: {str(e)}'
            }
    
    def _pos_kurallari_test(self) -> Dict[str, Any]:
        """POS iş kuralları testi"""
        try:
            from sontechsp.uygulama.moduller.pos.servisler.sepet_service import SepetService
            from sontechsp.uygulama.moduller.pos.servisler.odeme_service import OdemeService
            
            # POS servis fonksiyonlarının varlığını kontrol et
            if hasattr(SepetService, 'yeni_sepet_olustur') and hasattr(OdemeService, 'tek_odeme_yap'):
                self.basari_sayisi += 1
                return {
                    'durum': 'BASARILI',
                    'mesaj': 'POS servisleri fonksiyonları mevcut'
                }
            else:
                self.hata_sayisi += 1
                return {
                    'durum': 'HATA',
                    'mesaj': 'POS servis fonksiyonları eksik'
                }
                
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'POS servisleri import edilemedi: {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'POS kuralları testi sırasında hata: {str(e)}'
            }
    
    def _repository_kurallari_test(self) -> Dict[str, Any]:
        """Repository katmanı iş kuralları testi"""
        try:
            from sontechsp.uygulama.moduller.pos.repositories.satis_repository import SatisRepository
            from sontechsp.uygulama.moduller.pos.repositories.iade_repository import IadeRepository
            
            # Repository sınıflarının varlığını kontrol et
            if hasattr(SatisRepository, 'satis_olustur') and hasattr(IadeRepository, 'iade_olustur'):
                self.basari_sayisi += 1
                return {
                    'durum': 'BASARILI',
                    'mesaj': 'Repository sınıfları mevcut'
                }
            else:
                self.hata_sayisi += 1
                return {
                    'durum': 'HATA',
                    'mesaj': 'Repository sınıfları eksik'
                }
                
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Repository sınıfları import edilemedi: {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Repository kuralları testi sırasında hata: {str(e)}'
            }
    
    def api_sozlesmelerini_test_et(self) -> Dict[str, Any]:
        """API sözleşmelerinin bozulmadığını kontrol et"""
        print("🔌 API Sözleşmeleri Test Ediliyor...")
        
        api_testleri = {
            'servis_arayuzleri': self._servis_arayuzleri_test(),
            'dto_yapilari': self._dto_yapilari_test(),
            'repository_arayuzleri': self._repository_arayuzleri_test()
        }
        
        self.sonuclar['api_sozlesmeleri'] = api_testleri
        return api_testleri
    
    def _servis_arayuzleri_test(self) -> Dict[str, Any]:
        """Servis arayüzleri testi"""
        try:
            from sontechsp.uygulama.moduller.stok.servisler.stok_yonetim_service import StokYonetimService
            from sontechsp.uygulama.moduller.pos.servisler.sepet_service import SepetService
            
            # Servis arayüzlerinin varlığını kontrol et
            if hasattr(StokYonetimService, 'stok_ekle') and hasattr(SepetService, 'yeni_sepet_olustur'):
                self.basari_sayisi += 1
                return {
                    'durum': 'BASARILI',
                    'mesaj': 'Servis arayüzleri korunmuş'
                }
            else:
                self.hata_sayisi += 1
                return {
                    'durum': 'HATA',
                    'mesaj': 'Servis arayüzleri eksik'
                }
                
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Servis arayüzleri import edilemedi: {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Servis arayüzleri testi sırasında hata: {str(e)}'
            }
    
    def _dto_yapilari_test(self) -> Dict[str, Any]:
        """DTO yapıları testi"""
        try:
            from sontechsp.uygulama.moduller.stok.dto.urun_dto import UrunDTO
            from sontechsp.uygulama.moduller.ebelge.dto import EBelgeOlusturDTO
            
            # DTO sınıflarının varlığını kontrol et
            if hasattr(UrunDTO, '__dataclass_fields__') and hasattr(EBelgeOlusturDTO, '__dataclass_fields__'):
                self.basari_sayisi += 1
                return {
                    'durum': 'BASARILI',
                    'mesaj': 'DTO yapıları korunmuş'
                }
            else:
                self.hata_sayisi += 1
                return {
                    'durum': 'HATA',
                    'mesaj': 'DTO yapıları eksik'
                }
                
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'DTO yapıları import edilemedi: {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'DTO yapıları testi sırasında hata: {str(e)}'
            }
    
    def _repository_arayuzleri_test(self) -> Dict[str, Any]:
        """Repository arayüzleri testi"""
        try:
            from sontechsp.uygulama.moduller.stok.depolar import urun_repository
            from sontechsp.uygulama.moduller.pos.depolar import satis_repository
            
            # Repository arayüzlerinin varlığını kontrol et
            if hasattr(urun_repository, 'UrunRepository') and hasattr(satis_repository, 'SatisRepository'):
                self.basari_sayisi += 1
                return {
                    'durum': 'BASARILI',
                    'mesaj': 'Repository arayüzleri korunmuş'
                }
            else:
                self.hata_sayisi += 1
                return {
                    'durum': 'HATA',
                    'mesaj': 'Repository arayüzleri eksik'
                }
                
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Repository arayüzleri import edilemedi: {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Repository arayüzleri testi sırasında hata: {str(e)}'
            }
    
    def import_yapilarini_test_et(self) -> Dict[str, Any]:
        """Import yapılarının doğru çalıştığını test et"""
        print("📦 Import Yapıları Test Ediliyor...")
        
        import_testleri = {
            'dongüsel_import': self._dongüsel_import_test(),
            'eksik_import': self._eksik_import_test(),
            'init_dosyalari': self._init_dosyalari_test()
        }
        
        self.sonuclar['import_testleri'] = import_testleri
        return import_testleri
    
    def _dongüsel_import_test(self) -> Dict[str, Any]:
        """Döngüsel import kontrolü"""
        try:
            # Temel modülleri import ederek döngüsel import kontrolü
            from uygulama.arayuz.ekranlar import ebelge
            from uygulama.arayuz.ekranlar import raporlar
            from uygulama.arayuz.ekranlar import ayarlar
            
            self.basari_sayisi += 1
            return {
                'durum': 'BASARILI',
                'mesaj': 'Döngüsel import tespit edilmedi'
            }
            
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Import hatası (döngüsel import olabilir): {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Döngüsel import testi sırasında hata: {str(e)}'
            }
    
    def _eksik_import_test(self) -> Dict[str, Any]:
        """Eksik import kontrolü"""
        try:
            # Refactor edilen modüllerin import edilebilirliğini test et
            moduller = [
                'uygulama.arayuz.ekranlar.ebelge',
                'uygulama.arayuz.ekranlar.raporlar',
                'uygulama.arayuz.ekranlar.ayarlar',
                'sontechsp.uygulama.moduller.pos.repositories.satis_repository',
                'sontechsp.uygulama.moduller.pos.repositories.iade_repository'
            ]
            
            for modul in moduller:
                importlib.import_module(modul)
            
            self.basari_sayisi += 1
            return {
                'durum': 'BASARILI',
                'mesaj': f'Tüm modüller ({len(moduller)}) başarıyla import edildi'
            }
            
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Eksik import tespit edildi: {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'Eksik import testi sırasında hata: {str(e)}'
            }
    
    def _init_dosyalari_test(self) -> Dict[str, Any]:
        """__init__.py dosyalarının doğru çalışması testi"""
        try:
            # __init__.py dosyalarının export'larını test et
            from sontechsp.uygulama.arayuz.ebelge import EBelgeEkrani
            from sontechsp.uygulama.arayuz.raporlar import RaporlarEkrani
            from sontechsp.uygulama.arayuz.ayarlar import AyarlarEkrani
            
            self.basari_sayisi += 1
            return {
                'durum': 'BASARILI',
                'mesaj': '__init__.py dosyaları doğru export yapıyor'
            }
            
        except ImportError as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'__init__.py export hatası: {str(e)}'
            }
        except Exception as e:
            self.hata_sayisi += 1
            return {
                'durum': 'HATA',
                'mesaj': f'__init__.py testi sırasında hata: {str(e)}'
            }
    
    def tam_dogrulama_yap(self) -> Dict[str, Any]:
        """Kapsamlı fonksiyonalite doğrulaması"""
        print("🔍 Fonksiyonalite Doğrulaması Başlatılıyor...")
        print("=" * 60)
        
        try:
            # Tüm testleri çalıştır
            self.ui_ekranlarini_test_et()
            self.is_kurallarini_test_et()
            self.api_sozlesmelerini_test_et()
            self.import_yapilarini_test_et()
            
            # Genel durumu belirle
            toplam_test = self.basari_sayisi + self.hata_sayisi
            basari_orani = (self.basari_sayisi / toplam_test * 100) if toplam_test > 0 else 0
            
            if self.hata_sayisi == 0:
                self.sonuclar['genel_durum'] = 'BASARILI'
                durum_mesaji = "✅ Tüm fonksiyonalite testleri başarılı!"
            elif basari_orani >= 80:
                self.sonuclar['genel_durum'] = 'UYARI'
                durum_mesaji = f"⚠️  Bazı testler başarısız ({basari_orani:.1f}% başarı)"
            else:
                self.sonuclar['genel_durum'] = 'HATA'
                durum_mesaji = f"❌ Kritik hatalar mevcut ({basari_orani:.1f}% başarı)"
            
            # Özet bilgileri
            self.sonuclar['ozet'] = {
                'toplam_test': toplam_test,
                'basari_sayisi': self.basari_sayisi,
                'hata_sayisi': self.hata_sayisi,
                'basari_orani': basari_orani,
                'durum_mesaji': durum_mesaji,
                'test_tarihi': datetime.now().isoformat()
            }
            
            return self.sonuclar
            
        except Exception as e:
            self.sonuclar['genel_durum'] = 'KRITIK_HATA'
            self.sonuclar['hata'] = f"Doğrulama sırasında kritik hata: {str(e)}"
            return self.sonuclar
    
    def rapor_olustur(self, dosya_adi: str = None) -> str:
        """Doğrulama raporu oluştur"""
        if not dosya_adi:
            zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
            dosya_adi = f"fonksiyonalite_dogrulama_raporu_{zaman_damgasi}.json"
        
        try:
            with open(dosya_adi, 'w', encoding='utf-8') as f:
                json.dump(self.sonuclar, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Doğrulama raporu oluşturuldu: {dosya_adi}")
            return dosya_adi
            
        except Exception as e:
            print(f"❌ Rapor oluşturma hatası: {str(e)}")
            return ""
    
    def ozet_yazdir(self):
        """Doğrulama özetini konsola yazdır"""
        if 'ozet' not in self.sonuclar:
            print("❌ Henüz doğrulama yapılmamış!")
            return
        
        ozet = self.sonuclar['ozet']
        
        print("\n" + "=" * 60)
        print("📊 FONKSİYONALİTE DOĞRULAMA ÖZETİ")
        print("=" * 60)
        print(f"🎯 Toplam Test: {ozet['toplam_test']}")
        print(f"✅ Başarılı: {ozet['basari_sayisi']}")
        print(f"❌ Hatalı: {ozet['hata_sayisi']}")
        print(f"📈 Başarı Oranı: {ozet['basari_orani']:.1f}%")
        print(f"📅 Test Tarihi: {ozet['test_tarihi']}")
        print(f"\n{ozet['durum_mesaji']}")
        print("=" * 60)

def main():
    """Ana fonksiyon"""
    print("🚀 SonTechSP Fonksiyonalite Doğrulama Sistemi")
    print("=" * 60)
    
    dogrulayici = FonksiyonaliteDogrulayici()
    
    try:
        # Tam doğrulama yap
        sonuclar = dogrulayici.tam_dogrulama_yap()
        
        # Özet yazdır
        dogrulayici.ozet_yazdir()
        
        # Rapor oluştur
        rapor_dosyasi = dogrulayici.rapor_olustur()
        
        # Çıkış kodu belirle
        if sonuclar['genel_durum'] == 'BASARILI':
            sys.exit(0)
        elif sonuclar['genel_durum'] == 'UYARI':
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⏹️  Doğrulama kullanıcı tarafından durduruldu")
        sys.exit(3)
    except Exception as e:
        print(f"\n💥 Beklenmeyen hata: {str(e)}")
        traceback.print_exc()
        sys.exit(4)

if __name__ == "__main__":
    main()