MİMARİ KURALLARI (UYGULAMA ANAYASASI)

KATMANLAR
- ui/: PyQt ekranları. İş kuralı YOK.
- services/: İş kuralları. UI’dan çağrılır. Repo kullanır.
- repositories/: DB erişimi. SQL/ORM burada.
- database/: modeller + migration + bağlantı.

BAĞIMLILIK YÖNÜ (KESİN)
ui -> services -> repositories -> database

YASAKLAR
- ui katmanı repository/database import edemez
- services katmanı ui import edemez
- repositories katmanı services/ui import edemez
- entegrasyon modülleri doğrudan ui’dan çağrılamaz

EŞ ZAMANLI STOK
- stok düşme/ayırma işlemleri transaction içinde yapılır
- repository düzeyinde row-level lock uygulanır
- tutarlılık önceliklidir

OFFLINE POS
- satış işlemi offline ise SQLite kuyruğa yazılır
- online olunca senkron servisi kuyruğu işler (iskele)

---
inclusion: always
---
<!------------------------------------------------------------------------------------
   Add rules to this file or a short description and have Kiro refine them for you.
   
   Learn about inclusion modes: https://kiro.dev/docs/steering/#inclusion-modes
-------------------------------------------------------------------------------------> 