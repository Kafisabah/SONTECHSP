# Uygulama Kaynakları Klasörü

Bu klasör, SonTechSP uygulamasının görsel kaynaklarını (logo, ikon, resim) içerir.

## Klasör Yapısı

```
kaynaklar/
├── resimler/          # Logo ve genel resimler
│   ├── logo.png       # Ana uygulama logosu
│   ├── logo_kucuk.png # Küçük logo (32x32)
│   └── ...
├── ikonlar/           # UI ikonları
│   ├── kaydet.png     # Kaydet ikonu
│   ├── sil.png        # Sil ikonu
│   └── ...
└── README.md          # Bu dosya
```

## Logo Dosyaları

### Ana Logo
- **Dosya adı**: `logo.png`
- **Önerilen boyut**: 256x256 piksel veya daha büyük
- **Format**: PNG (şeffaf arka plan önerilir)
- **Kullanım**: Ana pencere, splash screen, hakkında ekranı

### Küçük Logo
- **Dosya adı**: `logo_kucuk.png`
- **Önerilen boyut**: 32x32 piksel
- **Format**: PNG
- **Kullanım**: Pencere ikonu, sistem tepsisi

## Kullanım Örnekleri

### Python Kodunda Logo Kullanımı

```python
from sontechsp.uygulama.arayuz.kaynaklar import logo_yukle, ikon_yukle

# Ana logo yükleme
logo = logo_yukle("logo.png", genislik=200)
if logo:
    label.setPixmap(logo)

# Küçük logo/ikon yükleme
pencere_ikonu = ikon_yukle("logo_kucuk.png", boyut=32)
if pencere_ikonu:
    self.setWindowIcon(pencere_ikonu)
```

### PyQt6 Pencere İkonu Ayarlama

```python
from PyQt6.QtWidgets import QMainWindow
from sontechsp.uygulama.arayuz.kaynaklar import ikon_yukle

class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        # Pencere ikonunu ayarla
        ikon = ikon_yukle("logo_kucuk.png")
        if ikon:
            self.setWindowIcon(ikon)
```

## Desteklenen Formatlar

- **PNG**: Önerilen (şeffaf arka plan desteği)
- **JPG/JPEG**: Desteklenir
- **BMP**: Desteklenir
- **GIF**: Desteklenir (animasyon desteklenmez)
- **SVG**: Desteklenir (QSvgWidget gerekli)

## Dosya Adlandırma Kuralları

- Türkçe karakter kullanmayın
- Boşluk yerine alt çizgi (_) kullanın
- Küçük harf tercih edin
- Açıklayıcı isimler verin

Örnekler:
- ✅ `logo.png`
- ✅ `kaydet_ikon.png`
- ✅ `musteri_resmi.jpg`
- ❌ `Logo Büyük.png`
- ❌ `müşteri-resmi.jpg`

## Logo Ekleme Adımları

1. Logo dosyanızı `resimler/` klasörüne kopyalayın
2. Ana logo için `logo.png` adını kullanın
3. Küçük ikon için `logo_kucuk.png` adını kullanın
4. Kodunuzda `logo_yukle()` fonksiyonunu kullanın

## Performans İpuçları

- Büyük resimleri önceden ölçeklendirin
- Sık kullanılan resimleri cache'leyin
- PNG formatını şeffaf arka plan için tercih edin
- İkonlar için 32x32, 48x48, 64x64 boyutlarını hazır bulundurun