# Version: 1.2.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.smoke_test_calistir
# Description: UI smoke test ana modülü - komut satırı desteği ile
# Changelog:
# - main() fonksiyonu eklendi
# - Komut satırı argüman desteği eklendi
# - Standart giriş noktası entegrasyonu
# - Import düzenlemesi yapıldı
# - CSV export desteği eklendi

import argparse
import importlib
import sys
import time
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import QApplication

from .buton_eslestirme_kaydi import (
    kayitlari_temizle,
    tablo_formatinda_cikti,
    csv_formatinda_cikti,
    csv_dosyasina_kaydet,
)
from .uygulama import UygulamaBaslatici


def ekran_gecis_testi(pencere, app: QApplication, ekranlar: Optional[List[str]] = None) -> bool:
    """
    Ekranlar arası geçiş testi yapar

    Args:
        pencere: Ana pencere instance'ı
        app: QApplication instance'ı
        ekranlar: Test edilecek ekran listesi (None ise tümü)

    Returns:
        bool: Test başarılı ise True
    """
    try:
        if ekranlar is None:
            ekranlar = list(pencere.ekranlar.keys())

        print(f"Toplam {len(ekranlar)} ekran bulundu: {ekranlar}")

        for ekran_adi in ekranlar:
            print(f"Ekrana geçiliyor: {ekran_adi}")
            pencere.ekran_degistir(ekran_adi)

            # Uygulamanın görsel olarak güncellenmesi için event loop'u işlet
            app.processEvents()
            time.sleep(0.5)  # İnsan gözüyle görmek için kısa bekleme

            # Doğrulama
            aktif_widget = pencere.icerik_alani.currentWidget()
            if not aktif_widget:
                print(f"HATA: {ekran_adi} yüklenemedi!")
                return False
            else:
                print(f"BAŞARILI: {ekran_adi} aktif.")

        print("Tüm ekran geçişleri tamamlandı.")
        return True

    except Exception as e:
        print(f"Ekran geçiş testi hatası: {e}")
        return False


def standart_giris_noktasi_dogrula() -> Tuple[bool, str]:
    """
    Standart uygulama giriş noktalarını doğrular ve en uygun olanını seçer
    Gereksinim 4.1, 4.2, 4.3'e uygun olarak uygulama.py öncelikli kontrol

    Returns:
        Tuple[bool, str]: (başarılı_mı, seçilen_giriş_noktası)
    """
    try:
        # Öncelik sırası: uygulama.py (zorunlu) -> alternatifler
        # Gereksinim 4.1: Standartlaştırılmış giriş noktası sağlama
        # Gereksinim 4.2: Standart uygulama giriş noktasını kullanma
        giris_noktalari = [
            ("uygulama.arayuz.uygulama", "Standart UI başlatıcısı (uygulama.py)", True),
            ("sontechsp.uygulama.ana", "Ana bootstrap giriş noktası", False),
            ("uygulama.arayuz.__main__", "Modül giriş noktası", False),
        ]

        standart_bulundu = False
        secilen_giris = ""

        for modul_adi, aciklama, is_standart in giris_noktalari:
            try:
                # Modülü import etmeye çalış
                modul = importlib.import_module(modul_adi)

                # main() fonksiyonunun varlığını kontrol et
                if hasattr(modul, "main") and callable(getattr(modul, "main")):
                    print(f"✓ Geçerli giriş noktası bulundu: {modul_adi} ({aciklama})")

                    # Standart giriş noktası (uygulama.py) bulunduysa öncelik ver
                    if is_standart:
                        print(f"✓ Standart giriş noktası (uygulama.py) doğrulandı")
                        standart_bulundu = True
                        secilen_giris = modul_adi
                        break
                    elif not standart_bulundu:
                        # Standart bulunamadıysa alternatifi kaydet
                        secilen_giris = modul_adi
                else:
                    print(f"✗ {modul_adi} main() fonksiyonu içermiyor")

            except ImportError as e:
                print(f"✗ {modul_adi} import edilemedi: {e}")
                continue

        if secilen_giris:
            if standart_bulundu:
                print(f"✓ Standart giriş noktası kullanılacak: {secilen_giris}")
            else:
                print(f"⚠ Standart giriş noktası bulunamadı, alternatif kullanılacak: {secilen_giris}")
            return True, secilen_giris
        else:
            print("✗ Hiçbir geçerli giriş noktası bulunamadı!")
            return False, ""

    except Exception as e:
        print(f"Giriş noktası doğrulama hatası: {e}")
        return False, ""


def alternatif_giris_noktalari_kontrol() -> List[str]:
    """
    Sistemdeki alternatif giriş noktalarını kontrol eder
    Gereksinim 4.4: Birden fazla giriş metodu varsa en uygun standart metodu kullanma

    Returns:
        List[str]: Bulunan alternatif giriş noktaları
    """
    alternatifler = []

    # Potansiyel alternatif giriş noktaları (standart uygulama.py hariç)
    potansiyel_noktalar = [
        ("uygulama.arayuz.ana_pencere", "Ana pencere doğrudan başlatıcısı"),
        ("sontechsp.uygulama.kurulum.baslat", "Kurulum başlatıcısı"),
        ("sontechsp.uygulama.kod_kalitesi.cli_arayuzu", "Kod kalitesi CLI"),
        ("sontechsp.uygulama.ana", "Ana bootstrap modülü"),
        ("uygulama.__main__", "Paket ana giriş noktası"),
    ]

    print("  Alternatif giriş noktaları taranıyor...")

    for nokta, aciklama in potansiyel_noktalar:
        try:
            modul = importlib.import_module(nokta)
            if hasattr(modul, "main") and callable(getattr(modul, "main")):
                alternatifler.append(nokta)
                print(f"  → Bulundu: {nokta} ({aciklama})")
            else:
                print(f"  ✗ {nokta} - main() fonksiyonu yok")
        except ImportError:
            print(f"  ✗ {nokta} - import edilemedi")
            continue

    if not alternatifler:
        print("  ℹ Hiçbir alternatif giriş noktası bulunamadı")
    else:
        print(f"  ✓ Toplam {len(alternatifler)} alternatif giriş noktası bulundu")

    return alternatifler


def temiz_kapanis(baslatici: UygulamaBaslatici) -> None:
    """
    Uygulamayı temiz şekilde kapatır ve kaynakları temizler

    Args:
        baslatici: UygulamaBaslatici instance'ı
    """
    try:
        print("Uygulama kapatılıyor...")
        if baslatici.ana_pencere:
            baslatici.ana_pencere.close()
        baslatici.kaynaklari_temizle()
        print("Temiz kapanış tamamlandı.")
    except Exception as e:
        print(f"Temiz kapanış hatası: {e}")


def smoke_test_calistir(
    verbose: bool = True,
    ekranlar: Optional[List[str]] = None,
    csv_export: bool = False,
    csv_dosya: Optional[str] = None,
) -> int:
    """
    Smoke testi çalıştırır:
    1. Standart giriş noktasını doğrular
    2. Uygulamayı başlatır
    3. Tüm ekranları gezer
    4. Buton eşleştirmelerini raporlar
    5. Temiz kapanış yapar

    Args:
        verbose: Detaylı çıktı göster
        ekranlar: Test edilecek ekran listesi (None ise tümü)
        csv_export: CSV formatında çıktı üret
        csv_dosya: CSV dosyasının kaydedileceği yol

    Returns:
        int: Çıkış kodu (0: başarılı, 1: hata)
    """
    if verbose:
        print("Smoke Testi Başlatılıyor...")

    # Standart giriş noktası doğrulaması
    if verbose:
        print("\n1. Standart giriş noktası doğrulaması...")

    giris_basarili, secilen_giris = standart_giris_noktasi_dogrula()
    if not giris_basarili:
        print("HATA: Geçerli giriş noktası bulunamadı!")
        return 1

    if verbose:
        print(f"✓ Seçilen giriş noktası: {secilen_giris}")

        # Alternatif giriş noktalarını da kontrol et
        print("\n2. Alternatif giriş noktaları kontrol ediliyor...")
        alternatifler = alternatif_giris_noktalari_kontrol()
        if alternatifler:
            print(f"✓ {len(alternatifler)} alternatif giriş noktası bulundu")
        else:
            print("ℹ Alternatif giriş noktası bulunamadı")

    # Kayıtları temizle
    if verbose:
        print("\n3. Önceki kayıtlar temizleniyor...")
    kayitlari_temizle()

    # Uygulama başlatıcıyı oluştur (standart uygulama.py giriş noktasını kullan)
    # Gereksinim 4.3: UI bileşenlerini düzgün şekilde başlatma
    baslatici = UygulamaBaslatici()

    try:
        # QApplication oluştur
        app = QApplication(sys.argv)
        baslatici.app = app
        baslatici.tema_yukle()

        # Servis fabrikası ve ana pencere oluştur
        from .servis_fabrikasi import ServisFabrikasi
        from .ana_pencere import AnaPencere

        baslatici.servis_fabrikasi = ServisFabrikasi()
        pencere = AnaPencere(baslatici.servis_fabrikasi)
        baslatici.ana_pencere = pencere
        pencere.show()

        if verbose:
            print("✓ Ana pencere açıldı (standart giriş noktası kullanıldı)")

        # Ekran geçiş testi
        if verbose:
            print("\n4. Ekran geçiş testi başlatılıyor...")
        test_basarili = ekran_gecis_testi(pencere, app, ekranlar)

        if not test_basarili:
            print("Ekran geçiş testi başarısız!")
            return 1

        # Rapor dökümü
        if verbose:
            print("\n5. Buton eşleştirme raporu oluşturuluyor...")
            print("\n" + "=" * 50)
            print("BUTON EŞLEŞTİRME TABLOSU")
            print("=" * 50)
            print(tablo_formatinda_cikti())
            print("=" * 50)

        # CSV export
        if csv_export:
            if verbose:
                print("\n6. CSV formatında rapor oluşturuluyor...")

            csv_icerik = csv_formatinda_cikti()

            if csv_dosya:
                # Dosyaya kaydet
                if csv_dosyasina_kaydet(csv_dosya):
                    if verbose:
                        print(f"✓ CSV raporu kaydedildi: {csv_dosya}")
                else:
                    print(f"✗ CSV dosyası kaydedilemedi: {csv_dosya}")
                    return 1
            else:
                # Konsola yazdır
                if verbose:
                    print("\nCSV FORMATINDA RAPOR:")
                    print("-" * 30)
                print(csv_icerik)
                if verbose:
                    print("-" * 30)

        if verbose:
            print("\n✓ Smoke testi başarıyla tamamlandı.")
            print(f"✓ Kullanılan giriş noktası: {secilen_giris}")

        return 0

    except Exception as e:
        print(f"TEST HATASI: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        # Temiz kapanış
        temiz_kapanis(baslatici)


def main() -> int:
    """
    Ana giriş noktası - komut satırı argümanlarını işler ve smoke test çalıştırır

    Returns:
        int: Çıkış kodu
    """
    parser = argparse.ArgumentParser(
        description="SONTECHSP UI Smoke Test Çalıştırıcısı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python -m uygulama.arayuz.smoke_test_calistir
  python -m uygulama.arayuz.smoke_test_calistir --quiet
  python -m uygulama.arayuz.smoke_test_calistir --screens pos_satis urunler_stok
  python -m uygulama.arayuz.smoke_test_calistir --csv
  python -m uygulama.arayuz.smoke_test_calistir --csv-file rapor.csv
        """,
    )

    parser.add_argument("--quiet", "-q", action="store_true", help="Sessiz mod - minimal çıktı")

    parser.add_argument("--screens", "-s", nargs="*", help="Test edilecek ekranlar (boş ise tümü)")

    parser.add_argument("--csv", action="store_true", help="CSV formatında rapor üret")

    parser.add_argument("--csv-file", type=str, help="CSV raporunu dosyaya kaydet")

    parser.add_argument("--version", "-v", action="version", version="SONTECHSP Smoke Test v1.1.0")

    try:
        args = parser.parse_args()

        # Verbose modunu belirle
        verbose = not args.quiet

        # Ekran listesini belirle
        ekranlar = args.screens if args.screens else None

        if verbose:
            print("SONTECHSP UI Smoke Test Başlatılıyor...")
            if ekranlar:
                print(f"Sadece şu ekranlar test edilecek: {ekranlar}")

        # CSV export ayarları
        csv_export = args.csv or args.csv_file is not None
        csv_dosya = args.csv_file

        # Smoke test çalıştır
        return smoke_test_calistir(verbose=verbose, ekranlar=ekranlar, csv_export=csv_export, csv_dosya=csv_dosya)

    except KeyboardInterrupt:
        print("\nTest kullanıcı tarafından iptal edildi.")
        return 130
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
