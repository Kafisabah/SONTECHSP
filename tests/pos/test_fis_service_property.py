# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_fis_service_property
# Description: FisService özellik tabanlı testleri
# Changelog:
# - İlk oluşturma

"""
FisService Özellik Tabanlı Testleri

Bu modül FisService'in özellik tabanlı testlerini içerir.
Hypothesis kütüphanesi kullanılarak rastgele verilerle test edilir.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, assume, settings

from sontechsp.uygulama.moduller.pos.servisler.fis_service import FisService
from sontechsp.uygulama.moduller.pos.hatalar import YazdirmaHatasi
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi


class TestFisServicePropertyTests:
    """FisService özellik tabanlı testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        # Mock repository'ler
        self.mock_satis_repository = Mock()
        self.mock_iade_repository = Mock()
        
        # FisService instance'ı oluştur
        self.fis_service = FisService(
            satis_repository=self.mock_satis_repository,
            iade_repository=self.mock_iade_repository
        )
    
    def teardown_method(self):
        """Her test sonrası çalışır"""
        # Mock'ları sıfırla
        self.mock_satis_repository.reset_mock()
        self.mock_iade_repository.reset_mock()
    
    @given(
        satis_id=st.integers(min_value=1, max_value=10000),
        fis_no=st.text(min_size=5, max_size=20, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2),
        urun_listesi=st.lists(
            st.tuples(
                st.text(min_size=3, max_size=20),  # urun_adi
                st.integers(min_value=1, max_value=10),  # adet
                st.decimals(min_value=Decimal('0.01'), max_value=Decimal('99.99'), places=2)  # birim_fiyat
            ),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=50)
    def test_property_13_satis_tamamlama_ve_fis_olusturma(
        self, satis_id, fis_no, terminal_id, kasiyer_id, toplam_tutar, urun_listesi
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 13: Satış Tamamlama ve Fiş Oluşturma**
        **Validates: Requirements 3.5**
        
        Herhangi bir tamamlanan satış için, sistem fiş oluşturmalı ve yazdırma için hazırlamalı
        """
        # Arrange
        satirlar = []
        for urun_adi, adet, birim_fiyat in urun_listesi:
            satirlar.append({
                'urun_adi': urun_adi,
                'adet': adet,
                'birim_fiyat': float(birim_fiyat),
                'toplam_tutar': float(Decimal(str(adet)) * birim_fiyat)
            })
        
        mock_satis = {
            'id': satis_id,
            'fis_no': fis_no,
            'satis_tarihi': datetime.now().isoformat(),
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'toplam_tutar': float(toplam_tutar),
            'indirim_tutari': 0.0,
            'satirlar': satirlar,
            'odemeler': [
                {
                    'odeme_turu': 'nakit',
                    'tutar': float(toplam_tutar)
                }
            ]
        }
        
        self.mock_satis_repository.satis_getir.return_value = mock_satis
        
        # Act
        fis_icerik = self.fis_service.satis_fisi_olustur(satis_id)
        
        # Assert
        # 1. Fiş oluşturulmuş olmalı
        assert fis_icerik is not None
        assert isinstance(fis_icerik, str)
        assert len(fis_icerik) > 0
        
        # 2. Fiş içeriği gerekli bilgileri içermeli
        assert "SATIŞ FİŞİ" in fis_icerik
        assert fis_no in fis_icerik
        assert str(terminal_id) in fis_icerik
        assert str(kasiyer_id) in fis_icerik
        
        # 3. Ürün bilgileri fiş içinde olmalı
        for urun_adi, adet, birim_fiyat in urun_listesi:
            # Ürün adının bir kısmı fiş içinde olmalı (kısaltılmış olabilir)
            assert any(urun_adi[:10] in satir for satir in fis_icerik.split('\n'))
        
        # 4. Toplam tutar fiş içinde olmalı
        assert f"{float(toplam_tutar):.2f}" in fis_icerik
        
        # 5. Yazdırma için hazır olmalı
        onizleme = self.fis_service.fis_onizleme(fis_icerik)
        assert onizleme['yazdirma_hazir'] is True
        assert onizleme['satir_sayisi'] > 0
        assert onizleme['karakter_sayisi'] > 0
        
        # 6. Repository'den satış bilgisi alınmış olmalı
        self.mock_satis_repository.satis_getir.assert_called_once_with(satis_id)
    
    @given(
        iade_id=st.integers(min_value=1, max_value=10000),
        fis_no=st.text(min_size=5, max_size=20, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        orijinal_satis_id=st.integers(min_value=1, max_value=10000),
        iade_nedeni=st.text(min_size=5, max_size=50),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999.99'), places=2),
        urun_listesi=st.lists(
            st.tuples(
                st.text(min_size=3, max_size=20),  # urun_adi
                st.integers(min_value=1, max_value=5),  # adet
                st.decimals(min_value=Decimal('0.01'), max_value=Decimal('99.99'), places=2)  # birim_fiyat
            ),
            min_size=1,
            max_size=3
        )
    )
    @settings(max_examples=50)
    def test_property_17_iade_fisi_yazdirma(
        self, iade_id, fis_no, terminal_id, kasiyer_id, orijinal_satis_id, 
        iade_nedeni, toplam_tutar, urun_listesi
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 17: İade Fişi Yazdırma**
        **Validates: Requirements 4.4**
        
        Herhangi bir iade fişi için, sistem iade fişi formatında çıktı üretmeli
        """
        # Arrange
        satirlar = []
        for urun_adi, adet, birim_fiyat in urun_listesi:
            satirlar.append({
                'urun_adi': urun_adi,
                'adet': adet,
                'birim_fiyat': float(birim_fiyat),
                'toplam_tutar': float(Decimal(str(adet)) * birim_fiyat)
            })
        
        mock_iade = {
            'id': iade_id,
            'fis_no': fis_no,
            'iade_tarihi': datetime.now().isoformat(),
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'orijinal_satis_id': orijinal_satis_id,
            'neden': iade_nedeni,
            'toplam_tutar': float(toplam_tutar),
            'satirlar': satirlar
        }
        
        self.mock_iade_repository.iade_getir.return_value = mock_iade
        
        # Act
        fis_icerik = self.fis_service.iade_fisi_olustur(iade_id)
        
        # Assert
        # 1. İade fişi oluşturulmuş olmalı
        assert fis_icerik is not None
        assert isinstance(fis_icerik, str)
        assert len(fis_icerik) > 0
        
        # 2. İade fişi formatında olmalı
        assert "İADE FİŞİ" in fis_icerik
        assert fis_no in fis_icerik
        assert str(terminal_id) in fis_icerik
        assert str(kasiyer_id) in fis_icerik
        assert str(orijinal_satis_id) in fis_icerik
        assert iade_nedeni in fis_icerik
        
        # 3. İade edilen ürün bilgileri fiş içinde olmalı
        for urun_adi, adet, birim_fiyat in urun_listesi:
            # Ürün adının bir kısmı fiş içinde olmalı
            assert any(urun_adi[:10] in satir for satir in fis_icerik.split('\n'))
        
        # 4. İade toplamı fiş içinde olmalı
        assert "İADE TOPLAMI" in fis_icerik
        assert f"{float(toplam_tutar):.2f}" in fis_icerik
        
        # 5. İade tamamlandı mesajı olmalı
        assert "İADE TAMAMLANDI" in fis_icerik
        
        # 6. Repository'den iade bilgisi alınmış olmalı
        self.mock_iade_repository.iade_getir.assert_called_once_with(iade_id)
    
    @given(
        satis_id=st.integers(min_value=1, max_value=10000),
        fis_no=st.text(min_size=5, max_size=20),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999.99'), places=2),
        indirim_tutari=st.decimals(min_value=Decimal('0.00'), max_value=Decimal('99.99'), places=2),
        magaza_adi=st.text(min_size=3, max_size=30),
        magaza_adres=st.text(min_size=10, max_size=50),
        magaza_telefon=st.text(min_size=10, max_size=15, alphabet='0123456789()-+ ')
    )
    @settings(max_examples=50)
    def test_property_22_fis_formatlama(
        self, satis_id, fis_no, terminal_id, kasiyer_id, toplam_tutar, 
        indirim_tutari, magaza_adi, magaza_adres, magaza_telefon
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 22: Fiş Formatlaması**
        **Validates: Requirements 6.1, 6.2**
        
        Herhangi bir tamamlanan satış için, sistem fiş içeriğini doğru formatlamalı ve 
        mağaza bilgileri, ürün listesi, ödeme detaylarını içermeli
        """
        # Arrange
        assume(indirim_tutari <= toplam_tutar)  # İndirim toplam tutardan fazla olamaz
        
        net_tutar = toplam_tutar - indirim_tutari
        
        mock_satis = {
            'id': satis_id,
            'fis_no': fis_no,
            'satis_tarihi': datetime.now().isoformat(),
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'toplam_tutar': float(toplam_tutar),
            'indirim_tutari': float(indirim_tutari),
            'satirlar': [
                {
                    'urun_adi': 'Test Ürün 1',
                    'adet': 2,
                    'birim_fiyat': 10.50,
                    'toplam_tutar': 21.00
                },
                {
                    'urun_adi': 'Test Ürün 2',
                    'adet': 1,
                    'birim_fiyat': 15.75,
                    'toplam_tutar': 15.75
                }
            ],
            'odemeler': [
                {
                    'odeme_turu': 'nakit',
                    'tutar': float(net_tutar)
                }
            ]
        }
        
        magaza_bilgileri = {
            'adi': magaza_adi,
            'adres': magaza_adres,
            'telefon': magaza_telefon
        }
        
        self.mock_satis_repository.satis_getir.return_value = mock_satis
        
        # Act
        fis_icerik = self.fis_service.satis_fisi_olustur(satis_id, magaza_bilgileri)
        
        # Assert
        # 1. Mağaza bilgileri fiş içinde olmalı
        assert magaza_adi in fis_icerik
        assert magaza_adres in fis_icerik
        assert magaza_telefon in fis_icerik
        
        # 2. Fiş bilgileri doğru formatlanmış olmalı
        assert fis_no in fis_icerik
        assert str(terminal_id) in fis_icerik
        assert str(kasiyer_id) in fis_icerik
        
        # 3. Ürün listesi formatlanmış olmalı
        assert "ÜRÜN" in fis_icerik
        assert "ADET" in fis_icerik
        assert "B.FİYAT" in fis_icerik
        assert "TOPLAM" in fis_icerik
        
        # 4. Ödeme detayları formatlanmış olmalı
        assert "ÖDEME BİLGİLERİ" in fis_icerik
        assert "NAKIT" in fis_icerik
        
        # 5. Toplam hesaplamaları doğru formatlanmış olmalı
        assert "Ara Toplam" in fis_icerik
        assert f"{float(toplam_tutar):.2f}" in fis_icerik
        
        if indirim_tutari > 0:
            assert "İndirim" in fis_icerik
            assert f"{float(indirim_tutari):.2f}" in fis_icerik
        
        assert "NET TOPLAM" in fis_icerik
        assert f"{float(net_tutar):.2f}" in fis_icerik
        
        # 6. Fiş yapısı doğru olmalı (başlık, içerik, alt bilgi)
        satirlar = fis_icerik.split('\n')
        assert len(satirlar) > 10  # Yeterli satır sayısı
        assert any("SATIŞ FİŞİ" in satir for satir in satirlar)
        assert any("teşekkürler" in satir for satir in satirlar)
        assert any("Yazdırma:" in satir for satir in satirlar)
    
    @given(
        fis_icerik=st.text(min_size=50, max_size=1000),
        yazici_adi=st.one_of(st.none(), st.text(min_size=3, max_size=20))
    )
    @settings(max_examples=50)
    def test_property_23_fis_yazdirma(self, fis_icerik, yazici_adi):
        """
        **Feature: pos-cekirdek-modulu, Property 23: Fiş Yazdırma**
        **Validates: Requirements 6.3**
        
        Herhangi bir fiş yazdırma işlemi için, sistem Fiş_Yazıcı'ya metin formatında göndermeli
        """
        # Arrange - Mock yazıcı gönderme fonksiyonu
        with patch.object(self.fis_service, '_yazici_gonder', return_value=True) as mock_yazici:
            
            # Act
            sonuc = self.fis_service.fis_yazdir(fis_icerik, yazici_adi)
            
            # Assert
            # 1. Yazdırma işlemi başarılı olmalı
            assert sonuc is True
            
            # 2. Yazıcı gönderme fonksiyonu çağrılmış olmalı
            mock_yazici.assert_called_once_with(fis_icerik, yazici_adi)
            
            # 3. Fiş içeriği metin formatında gönderilmiş olmalı
            call_args = mock_yazici.call_args
            gonderilen_icerik = call_args[0][0]
            gonderilen_yazici = call_args[0][1]
            
            assert gonderilen_icerik == fis_icerik
            assert gonderilen_yazici == yazici_adi
            assert isinstance(gonderilen_icerik, str)
    
    @given(
        fis_icerik=st.text(min_size=50, max_size=1000)
    )
    @settings(max_examples=50)
    def test_property_24_yazdirma_hata_yonetimi(self, fis_icerik):
        """
        **Feature: pos-cekirdek-modulu, Property 24: Yazdırma Hata Yönetimi**
        **Validates: Requirements 6.4**
        
        Herhangi bir yazdırma hatası için, sistem hata mesajı göstermeli ve fiş içeriğini saklamalı
        """
        # Arrange - Mock yazıcı gönderme fonksiyonu hata döndürsün
        with patch.object(self.fis_service, '_yazici_gonder', return_value=False) as mock_yazici:
            
            # Act
            sonuc = self.fis_service.fis_yazdir(fis_icerik)
            
            # Assert
            # 1. Yazdırma işlemi başarısız olmalı
            assert sonuc is False
            
            # 2. Yazıcı gönderme fonksiyonu çağrılmış olmalı
            mock_yazici.assert_called_once()
            
            # 3. Fiş içeriği saklanabilir durumda olmalı (dosyaya kaydetme testi)
            dosya_yolu = self.fis_service.fis_kaydet(fis_icerik)
            assert dosya_yolu is not None
            assert isinstance(dosya_yolu, str)
            assert len(dosya_yolu) > 0
            assert dosya_yolu.endswith('.txt')
    
    @given(
        fis_icerik=st.text(min_size=10, max_size=1000)
    )
    @settings(max_examples=50)
    def test_fis_onizleme_property(self, fis_icerik):
        """
        Fiş önizleme özellik testi
        
        Herhangi bir fiş içeriği için önizleme bilgileri doğru hesaplanmalı
        """
        # Act
        onizleme = self.fis_service.fis_onizleme(fis_icerik)
        
        # Assert
        # 1. Önizleme bilgileri mevcut olmalı
        assert 'fis_icerik' in onizleme
        assert 'satir_sayisi' in onizleme
        assert 'karakter_sayisi' in onizleme
        assert 'en_uzun_satir' in onizleme
        assert 'yazdirma_hazir' in onizleme
        
        # 2. Hesaplamalar doğru olmalı
        assert onizleme['fis_icerik'] == fis_icerik
        assert onizleme['karakter_sayisi'] == len(fis_icerik)
        
        satirlar = fis_icerik.split('\n')
        assert onizleme['satir_sayisi'] == len(satirlar)
        
        if satirlar:
            beklenen_en_uzun = max(len(satir) for satir in satirlar)
            assert onizleme['en_uzun_satir'] == beklenen_en_uzun
        
        # 3. Yazdırma hazır durumu doğru olmalı
        assert onizleme['yazdirma_hazir'] is True
    
    @given(
        yazici_adi=st.one_of(st.none(), st.text(min_size=3, max_size=20))
    )
    @settings(max_examples=30)
    def test_yazici_durumu_kontrol_property(self, yazici_adi):
        """
        Yazıcı durumu kontrol özellik testi
        
        Herhangi bir yazıcı için durum bilgileri döndürülmeli
        """
        # Act
        durum = self.fis_service.yazici_durumu_kontrol(yazici_adi)
        
        # Assert
        # 1. Durum bilgileri mevcut olmalı
        assert 'yazici_adi' in durum
        assert 'durum' in durum
        assert 'yazdirma_hazir' in durum
        
        # 2. Yazıcı adı doğru olmalı
        if yazici_adi:
            assert durum['yazici_adi'] == yazici_adi
        else:
            assert durum['yazici_adi'] == 'Varsayılan Yazıcı'
        
        # 3. Durum değerleri geçerli olmalı
        assert durum['durum'] in ['hazir', 'mesgul', 'hata', 'kagit_yok', 'offline']
        assert isinstance(durum['yazdirma_hazir'], bool)


class TestFisServiceValidasyonTests:
    """FisService validasyon testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_satis_repository = Mock()
        self.mock_iade_repository = Mock()
        self.fis_service = FisService(
            satis_repository=self.mock_satis_repository,
            iade_repository=self.mock_iade_repository
        )
    
    def teardown_method(self):
        """Her test sonrası çalışır"""
        self.mock_satis_repository.reset_mock()
        self.mock_iade_repository.reset_mock()
    
    @given(
        gecersiz_satis_id=st.integers(max_value=0)
    )
    @settings(max_examples=30)
    def test_gecersiz_satis_id_validasyonu(self, gecersiz_satis_id):
        """Geçersiz satış ID için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.fis_service.satis_fisi_olustur(gecersiz_satis_id)
        
        assert "Satış ID pozitif olmalıdır" in str(exc_info.value)
    
    @given(
        gecersiz_iade_id=st.integers(max_value=0)
    )
    @settings(max_examples=30)
    def test_gecersiz_iade_id_validasyonu(self, gecersiz_iade_id):
        """Geçersiz iade ID için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.fis_service.iade_fisi_olustur(gecersiz_iade_id)
        
        assert "İade ID pozitif olmalıdır" in str(exc_info.value)
    
    @given(
        satis_id=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=30)
    def test_satis_bulunamadi_validasyonu(self, satis_id):
        """Satış bulunamadığında validasyon hatası"""
        # Arrange
        self.mock_satis_repository.satis_getir.return_value = None
        
        # Act & Assert
        with pytest.raises(SontechHatasi) as exc_info:
            self.fis_service.satis_fisi_olustur(satis_id)
        
        assert f"Satış bulunamadı: {satis_id}" in str(exc_info.value)
    
    @given(
        iade_id=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=30)
    def test_iade_bulunamadi_validasyonu(self, iade_id):
        """İade bulunamadığında validasyon hatası"""
        # Arrange
        self.mock_iade_repository.iade_getir.return_value = None
        
        # Act & Assert
        with pytest.raises(SontechHatasi) as exc_info:
            self.fis_service.iade_fisi_olustur(iade_id)
        
        assert f"İade bulunamadı: {iade_id}" in str(exc_info.value)
    
    @given(
        bos_fis_icerik=st.one_of(st.just(""), st.just("   "), st.just("\n\n"))
    )
    @settings(max_examples=20)
    def test_bos_fis_icerik_validasyonu(self, bos_fis_icerik):
        """Boş fiş içeriği için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.fis_service.fis_yazdir(bos_fis_icerik)
        
        assert "Fiş içeriği boş olamaz" in str(exc_info.value)
    
    @given(
        fis_icerik=st.text(min_size=10, max_size=100)
    )
    @settings(max_examples=30)
    def test_yazici_hata_durumu(self, fis_icerik):
        """Yazıcı hatası durumunda hata yönetimi"""
        # Arrange - Mock yazıcı gönderme fonksiyonu exception fırlatsın
        with patch.object(self.fis_service, '_yazici_gonder', side_effect=Exception("Yazıcı hatası")):
            
            # Act
            sonuc = self.fis_service.fis_yazdir(fis_icerik)
            
            # Assert
            # Hata durumunda False döndürmeli
            assert sonuc is False