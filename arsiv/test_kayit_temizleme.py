# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_kayit_temizleme
# Description: Buton eşleştirme kayıt sistemi temizleme ve tablo formatı test scripti
# Changelog:
# - İlk versiyon: Kayıt temizleme ve tablo formatı test fonksiyonları

#!/usr/bin/env python3

from uygulama.arayuz.buton_eslestirme_kaydi import (
    kayit_ekle,
    kayit_sayisi,
    kayitlari_temizle,
    tablo_formatinda_cikti,
)


def test_kayit_temizleme() -> bool:
    """
    Kayıt temizleme ve tablo formatı fonksiyonlarını test et

    Returns:
        bool: Test başarılı ise True, aksi halde False
    """
    print("🧪 Kayıt temizleme testi başlatılıyor...")

    # Önce mevcut kayıtları temizle
    kayitlari_temizle()
    print(f"📋 Başlangıç kayıt sayısı: {kayit_sayisi()}")

    # Test kayıtları ekle
    print("➕ Test kayıtları ekleniyor...")
    kayit_ekle("TestEkran", "TestButon1", "test_handler_1", "test_servis_1")
    kayit_ekle("TestEkran2", "TestButon2", "test_handler_2", "test_servis_2")
    kayit_ekle("TestEkran3", "TestButon3", "test_handler_3")  # Servis metodu olmadan

    print(f"📊 Kayıt ekleme sonrası sayı: {kayit_sayisi()}")
    print("\n📋 Tablo formatı çıktı:")
    print(tablo_formatinda_cikti())

    # Kayıtları temizle
    print("\n🧹 Kayıtları temizliyorum...")
    kayitlari_temizle()
    print(f"📊 Temizleme sonrası kayıt sayısı: {kayit_sayisi()}")

    print("\n📋 Temizleme sonrası tablo çıktı:")
    print(tablo_formatinda_cikti())

    # Başarı kontrolü
    if kayit_sayisi() == 0:
        print("\n✅ Kayıt temizleme testi başarılı!")
        return True
    else:
        print("\n❌ Kayıt temizleme testi başarısız!")
        return False


def main() -> None:
    """Ana test fonksiyonu"""
    try:
        sonuc = test_kayit_temizleme()
        exit_code = 0 if sonuc else 1
        exit(exit_code)
    except Exception as e:
        print(f"❌ Test sırasında hata oluştu: {e}")
        exit(1)


if __name__ == "__main__":
    main()
