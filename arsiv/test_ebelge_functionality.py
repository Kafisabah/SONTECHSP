# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_ebelge_functionality
# Description: E-Belge refactoring sonrası fonksiyonalite testi
# Changelog:
# - İlk sürüm oluşturuldu

"""E-Belge modülü fonksiyonalite testi"""

import os
import sys
from typing import List, Tuple
from unittest.mock import Mock

from PyQt6.QtWidgets import QApplication


def test_ebelge_import() -> bool:
    """E-Belge modülünün import edilebilirliğini test et"""
    try:
        from uygulama.arayuz.ekranlar.ebelge import Ebelge, EbelgeEkrani
        print("✓ E-Belge modülü başarıyla import edildi")
        return True
    except Exception as e:
        print(f"✗ E-Belge modülü import hatası: {e}")
        return False


def test_ebelge_submodules() -> bool:
    """E-Belge alt modüllerinin import edilebilirliğini test et"""
    try:
        from uygulama.arayuz.ekranlar.ebelge import (
            EbelgeDurum, EbelgeFiltreleri, EbelgeIslemleri, 
            EbelgeTablolar, EbelgeVeriYoneticisi, EbelgeYardimcilar
        )
        print("✓ E-Belge alt modülleri başarıyla import edildi")
        return True
    except Exception as e:
        print(f"✗ E-Belge alt modülleri import hatası: {e}")
        return False


def test_ebelge_instantiation() -> bool:
    """E-Belge sınıfının örneklenebilirliğini test et"""
    try:
        # Mock servis fabrikası oluştur
        mock_servis_fabrikasi = Mock()
        
        # QApplication gerekli
        if not QApplication.instance():
            app = QApplication([])
        
        from uygulama.arayuz.ekranlar.ebelge import Ebelge
        
        # E-Belge örneği oluştur
        ebelge = Ebelge(mock_servis_fabrikasi)
        
        print("✓ E-Belge sınıfı başarıyla örneklendi")
        return True
    except Exception as e:
        print(f"✗ E-Belge sınıfı örnekleme hatası: {e}")
        return False


def test_ebelge_methods() -> bool:
    """E-Belge sınıfının temel metodlarının varlığını test et"""
    try:
        from uygulama.arayuz.ekranlar.ebelge import Ebelge
        
        # Metodların varlığını kontrol et
        required_methods = [
            'ekrani_hazirla', 'filtre_uygula', 'belge_gonder',
            'durum_sorgula', 'tekrar_dene', 'toplu_gonder',
            'xml_goruntule', 'secilenleri_gonder', 'pdf_indir',
            'hatalari_duzelt', 'bekleyen_listesi_yenile',
            'gonderilen_listesi_yenile', 'hatali_listesi_yenile'
        ]
        
        for method_name in required_methods:
            if not hasattr(Ebelge, method_name):
                print(f"✗ Eksik metod: {method_name}")
                return False
        
        print("✓ E-Belge sınıfının tüm gerekli metodları mevcut")
        return True
    except Exception as e:
        print(f"✗ E-Belge metodları kontrol hatası: {e}")
        return False


def test_file_sizes() -> bool:
    """Dosya boyutlarının hedef limitlere uygunluğunu test et"""
    try:
        ebelge_dir = "uygulama/arayuz/ekranlar/ebelge"
        
        if not os.path.exists(ebelge_dir):
            print(f"✗ E-Belge dizini bulunamadı: {ebelge_dir}")
            return False
        
        files_info: List[Tuple[str, int]] = []
        total_lines = 0
        
        for filename in os.listdir(ebelge_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                filepath = os.path.join(ebelge_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    files_info.append((filename, lines))
                    total_lines += lines
        
        print(f"\n📊 Dosya Boyutları:")
        for filename, lines in files_info:
            status = "✓" if lines <= 300 else "⚠"
            print(f"{status} {filename}: {lines} satır")
        
        if files_info:
            print(f"\n📈 Toplam satır sayısı: {total_lines}")
            print(f"📉 Ortalama dosya boyutu: {total_lines / len(files_info):.1f} satır")
        
        # Hedef: hiçbir dosya 300 satırı geçmemeli
        oversized_files = [f for f, l in files_info if l > 300]
        if oversized_files:
            print(f"⚠ Limit aşan dosyalar: {oversized_files}")
        else:
            print("✓ Tüm dosyalar boyut limitine uygun")
        
        return len(oversized_files) == 0
    except Exception as e:
        print(f"✗ Dosya boyutu kontrol hatası: {e}")
        return False


def main() -> bool:
    """Ana test fonksiyonu"""
    print("🔍 E-Belge Refactoring Doğrulama Testleri")
    print("=" * 50)
    
    tests = [
        ("Import Testi", test_ebelge_import),
        ("Alt Modül Import Testi", test_ebelge_submodules),
        ("Sınıf Örnekleme Testi", test_ebelge_instantiation),
        ("Metod Varlık Testi", test_ebelge_methods),
        ("Dosya Boyutu Testi", test_file_sizes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ Test hatası: {e}")
    
    print(f"\n📊 Test Sonuçları:")
    print(f"✓ Geçen: {passed}/{total}")
    print(f"✗ Başarısız: {total - passed}/{total}")
    print(f"📈 Başarı oranı: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Tüm testler başarılı! E-Belge refactoring doğrulandı.")
        return True
    else:
        print(f"\n⚠ {total - passed} test başarısız. İnceleme gerekli.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)