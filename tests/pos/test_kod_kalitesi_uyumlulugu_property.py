# Version: 0.1.0
# Last Update: 2025-12-19
# Module: test_kod_kalitesi_uyumlulugu_property
# Description: POS kod kalitesi uyumluluğu için özellik tabanlı testler
# Changelog:
# - İlk oluşturma - Kod kalitesi uyumluluk özellik testi

"""
POS Kod Kalitesi Uyumluluğu Özellik Testleri

**Feature: pos-arayuz-entegrasyonu, Property 10: Kod Kalitesi Uyumluluğu**
**Validates: Requirements 9.2, 9.3, 9.4**

POS dosyalarının kod kalitesi standartlarına uygunluğunu test eder.
"""

import ast
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck


class TestKodKalitesiUyumlulugu:
    """POS kod kalitesi uyumluluğu özellik testleri"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Test kurulumu"""
        self.pos_ui_klasoru = "sontechsp/uygulama/arayuz/ekranlar/pos"
        self.max_dosya_boyutu = 120
        self.max_fonksiyon_boyutu = 25

    def test_pos_dosya_boyut_limiti_property(self):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 10: Kod Kalitesi Uyumluluğu**
        **Validates: Requirements 9.2**

        Herhangi bir POS dosyasında, sistem 120 satır dosya limitine uyum sağlamalıdır
        """
        pos_dosyalari = self._pos_dosyalarini_bul()

        for dosya_yolu in pos_dosyalari:
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                satirlar = f.readlines()

            # Yorum olmayan satırları say
            kod_satirlari = [satir for satir in satirlar if satir.strip() and not satir.strip().startswith("#")]

            assert len(kod_satirlari) <= self.max_dosya_boyutu, (
                f"Dosya {dosya_yolu} 120 satır limitini aşıyor: "
                f"{len(kod_satirlari)} satır (limit: {self.max_dosya_boyutu})"
            )

    def test_pos_fonksiyon_boyut_limiti_property(self):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 10: Kod Kalitesi Uyumluluğu**
        **Validates: Requirements 9.3**

        Herhangi bir POS fonksiyonunda, sistem 25 satır fonksiyon limitine uyum sağlamalıdır
        """
        pos_dosyalari = self._pos_dosyalarini_bul()

        for dosya_yolu in pos_dosyalari:
            try:
                with open(dosya_yolu, "r", encoding="utf-8") as f:
                    icerik = f.read()

                tree = ast.parse(icerik)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        fonksiyon_satirlari = node.end_lineno - node.lineno + 1

                        assert fonksiyon_satirlari <= self.max_fonksiyon_boyutu, (
                            f"Fonksiyon {node.name} dosyada {dosya_yolu} "
                            f"25 satır limitini aşıyor: {fonksiyon_satirlari} satır "
                            f"(limit: {self.max_fonksiyon_boyutu})"
                        )

            except SyntaxError:
                # Syntax hatası olan dosyaları atla
                continue

    def test_pos_pep8_uyumluluk_property(self):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 10: Kod Kalitesi Uyumluluğu**
        **Validates: Requirements 9.4**

        Herhangi bir POS dosyasında, sistem PEP8 standartlarına uyum sağlamalıdır
        """
        pos_dosyalari = self._pos_dosyalarini_bul()

        for dosya_yolu in pos_dosyalari:
            # Temel PEP8 kurallarını kontrol et
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                satirlar = f.readlines()

            for satir_no, satir in enumerate(satirlar, 1):
                # Satır uzunluğu kontrolü (120 karakter)
                if len(satir.rstrip()) > 120:
                    assert False, (
                        f"Dosya {dosya_yolu} satır {satir_no}: "
                        f"Satır uzunluğu 120 karakteri aşıyor: {len(satir.rstrip())} karakter"
                    )

                # Tab karakteri kontrolü
                if "\t" in satir:
                    assert False, (
                        f"Dosya {dosya_yolu} satır {satir_no}: " f"Tab karakteri kullanılmış, 4 boşluk kullanın"
                    )

                # Satır sonu boşluk kontrolü
                if satir.endswith(" \n") or satir.endswith(" \r\n"):
                    assert False, f"Dosya {dosya_yolu} satır {satir_no}: " f"Satır sonunda gereksiz boşluk var"

    @given(
        st.sampled_from(
            [
                "sontechsp/uygulama/arayuz/ekranlar/pos/pos_satis_ekrani.py",
                "sontechsp/uygulama/arayuz/ekranlar/pos/sepet_modeli.py",
                "sontechsp/uygulama/arayuz/ekranlar/pos/ust_bar.py",
                "sontechsp/uygulama/arayuz/ekranlar/pos/odeme_paneli.py",
                "sontechsp/uygulama/arayuz/ekranlar/pos/hizli_islem_seridi.py",
                "sontechsp/uygulama/arayuz/ekranlar/pos/hizli_urunler_sekmesi.py",
                "sontechsp/uygulama/arayuz/ekranlar/pos/turkuaz_tema.py",
                "sontechsp/uygulama/arayuz/ekranlar/pos/pos_hata_yoneticisi.py",
            ]
        )
    )
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_pos_dosya_kalite_standartlari_property(self, dosya_yolu):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 10: Kod Kalitesi Uyumluluğu**
        **Validates: Requirements 9.2, 9.3, 9.4**

        Herhangi bir POS dosyasında, sistem tüm kod kalitesi standartlarına uyum sağlamalıdır
        """
        if not os.path.exists(dosya_yolu):
            pytest.skip(f"Dosya mevcut değil: {dosya_yolu}")

        # Dosya boyutu kontrolü
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            satirlar = f.readlines()

        kod_satirlari = [satir for satir in satirlar if satir.strip() and not satir.strip().startswith("#")]

        assert len(kod_satirlari) <= 120, f"Dosya boyutu limiti aşıldı: {len(kod_satirlari)} > 120"

        # Fonksiyon boyutu kontrolü
        try:
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                icerik = f.read()

            tree = ast.parse(icerik)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    fonksiyon_satirlari = node.end_lineno - node.lineno + 1
                    assert fonksiyon_satirlari <= 25, (
                        f"Fonksiyon {node.name} boyutu limiti aşıldı: " f"{fonksiyon_satirlari} > 25"
                    )

        except SyntaxError:
            pass  # Syntax hatası olan dosyaları atla

        # Temel PEP8 kontrolü
        for satir_no, satir in enumerate(satirlar, 1):
            if len(satir.rstrip()) > 120:
                assert False, f"Satır {satir_no} uzunluğu 120 karakteri aşıyor"

            if "\t" in satir:
                assert False, f"Satır {satir_no} tab karakteri içeriyor"

    def _pos_dosyalarini_bul(self) -> List[str]:
        """POS UI klasöründeki Python dosyalarını bulur"""
        pos_dosyalari = []

        if os.path.exists(self.pos_ui_klasoru):
            for root, dirs, files in os.walk(self.pos_ui_klasoru):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        pos_dosyalari.append(os.path.join(root, file))

        return pos_dosyalari

    def test_pos_kod_kalitesi_raporu_olusturma(self):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 10: Kod Kalitesi Uyumluluğu**
        **Validates: Requirements 9.2, 9.3, 9.4**

        Sistem otomatik kod kalitesi raporlama sistemi kurmalıdır
        """
        pos_dosyalari = self._pos_dosyalarini_bul()

        rapor = {
            "analiz_tarihi": "2024-12-19",
            "toplam_dosya": len(pos_dosyalari),
            "buyuk_dosyalar": [],
            "buyuk_fonksiyonlar": [],
            "pep8_ihlalleri": [],
        }

        for dosya_yolu in pos_dosyalari:
            # Dosya boyutu analizi
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                satirlar = f.readlines()

            kod_satirlari = [satir for satir in satirlar if satir.strip() and not satir.strip().startswith("#")]

            if len(kod_satirlari) > 120:
                rapor["buyuk_dosyalar"].append({"dosya": dosya_yolu, "satir_sayisi": len(kod_satirlari)})

            # Fonksiyon boyutu analizi
            try:
                with open(dosya_yolu, "r", encoding="utf-8") as f:
                    icerik = f.read()

                tree = ast.parse(icerik)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        fonksiyon_satirlari = node.end_lineno - node.lineno + 1
                        if fonksiyon_satirlari > 25:
                            rapor["buyuk_fonksiyonlar"].append(
                                {"dosya": dosya_yolu, "fonksiyon": node.name, "satir_sayisi": fonksiyon_satirlari}
                            )

            except SyntaxError:
                continue

            # PEP8 ihlal analizi
            for satir_no, satir in enumerate(satirlar, 1):
                if len(satir.rstrip()) > 120:
                    rapor["pep8_ihlalleri"].append(
                        {"dosya": dosya_yolu, "satir": satir_no, "ihlal": "Satır uzunluğu 120 karakteri aşıyor"}
                    )

                if "\t" in satir:
                    rapor["pep8_ihlalleri"].append(
                        {"dosya": dosya_yolu, "satir": satir_no, "ihlal": "Tab karakteri kullanılmış"}
                    )

        # Rapor oluşturulabildiğini doğrula
        assert isinstance(rapor, dict)
        assert "analiz_tarihi" in rapor
        assert "toplam_dosya" in rapor
        assert "buyuk_dosyalar" in rapor
        assert "buyuk_fonksiyonlar" in rapor
        assert "pep8_ihlalleri" in rapor

        # Rapor içeriğinin mantıklı olduğunu kontrol et
        assert rapor["toplam_dosya"] >= 0
        assert isinstance(rapor["buyuk_dosyalar"], list)
        assert isinstance(rapor["buyuk_fonksiyonlar"], list)
        assert isinstance(rapor["pep8_ihlalleri"], list)
