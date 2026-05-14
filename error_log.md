# COME424/1 — Proje Hata ve Sorun Günlüğü

> **Ders:** Recommender Systems (COME424/1)  
> **Hoca:** Dr. Öğr. Üyesi Gamze Uslu — Üsküdar Üniversitesi  
> **Grup:** Doğukan Aydın (240200019), Elif Dalmış (230201082), Yaman Balcı (220201081), Salih Çetin (220201060), Alperen Keskin (230201094)  
> **Makale:** Schedl & Bauer (2018) — Mainstreaminess for Personalized Music Recommender Systems  
> **Güncelleme:** 14 Mayıs 2026

---

## Kayıt Formatı

Her hata şu başlıklar altında kaydedilmiştir:

- **Tarih / Saat:** Ne zaman karşılaşıldı
- **Dosya / Konum:** Hangi dosyada, hangi satır civarında
- **Hata Mesajı:** Tam terminal çıktısı
- **Kök Neden:** Neden oluştu
- **Çözüm:** Nasıl giderildi
- **Öğrenilen:** Gelecek için not

---

## OTURUM 1 — 12 Nisan 2026

### ERR-001 · `KeyError: 'user_id'`

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 12 Nisan 2026, ~11:00 |
| **Dosya** | `mainstreaminess.py` (ilk versiyon, hardcoded veri) |
| **Aşama** | Midterm implementasyonu |

**Hata Mesajı:**
```
KeyError: 'user_id'
```

**Kök Neden:**  
İlk versiyonda veri seti doğrudan Python sözlüğü olarak tanımlanmıştı. DataFrame oluşturulurken `index` kolonu `"User"` olarak adlandırıldı, ancak kod `df["user_id"]` ile erişmeye çalışıyordu. Kolon adı tutarsızlığından kaynaklandı.

**Çözüm:**  
```python
# Yanlış
df = pd.DataFrame(data)
df["user_id"]  # KeyError

# Doğru
df = pd.DataFrame(data)
df.index.name = "user_id"
# veya
df = pd.DataFrame(data).set_index("User")
```

**Öğrenilen:** DataFrame index'i ile kolon adı karıştırılmamalı. İndeks ile çalışırken `.index` ve `.loc[]` kullanılmalı.

---

### ERR-002 · `ZeroDivisionError` — `normalize()` fonksiyonu

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 12 Nisan 2026, ~11:30 |
| **Dosya** | `mainstreaminess.py` — `normalize()` fonksiyonu |
| **Aşama** | Fraction-based mainstreaminess hesaplama |

**Hata Mesajı:**
```
ZeroDivisionError: float division by zero
```

**Kök Neden:**  
Hiç playcount'u olmayan kullanıcı için `normalize()` fonksiyonu toplam = 0 olduğunda sıfıra bölüyor.

**Çözüm:**
```python
# Yanlış
def normalize(series):
    return series / series.sum()

# Doğru
def normalize(series):
    s = series.sum()
    return series / s if s > 0 else series
```

**Öğrenilen:** Müzik verilerinde seyrek matris (sparse matrix) çok yaygın — sıfır sum kontrolü zorunlu.

---

### ERR-003 · `log(0)` — KL Divergence hesabında NaN

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 12 Nisan 2026, ~12:00 |
| **Dosya** | `mainstreaminess.py` — `kl_divergence_sym()` |
| **Aşama** | KL Divergence implementasyonu |

**Hata Mesajı:**
```
RuntimeWarning: divide by zero encountered in log
RuntimeWarning: invalid value encountered in multiply
# Sonuç: nan veya -inf
```

**Kök Neden:**  
Bir kullanıcı belirli bir sanatçıyı hiç dinlememişse ilgili playcount = 0, normalize edildiğinde de 0 kalır. `log(0)` matematiksel olarak tanımsız (`-inf`).

**Çözüm:**
```python
# Epsilon (küçük sayı) ekleyerek sıfırdan kaçınma
def kl_divergence_sym(p, q, epsilon=1e-10):
    p = normalize(p) + epsilon   # 0 olmaktan çıkartılıyor
    q = normalize(q) + epsilon
    kl_pq = (p * np.log(p / q)).sum()
    kl_qp = (q * np.log(q / p)).sum()
    return 1 / (1 + (kl_pq + kl_qp) / 2)
```

**Öğrenilen:** Olasılık dağılımlarında `epsilon=1e-10` ekleme, information-theoretic hesaplamalarda standart pratiktir (Laplace smoothing'in bir çeşidi).

---

### ERR-004 · `NaN` — `compute_AF_ILF()` sıfıra bölme

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 12 Nisan 2026, ~12:15 |
| **Dosya** | `mainstreaminess.py` — `compute_AF_ILF()` |
| **Aşama** | AF-ILF hesaplama |

**Hata Mesajı:**
```
RuntimeWarning: divide by zero encountered in true_divide
# lf_u2 = 0 olduğunda nan çıkıyor
```

**Kök Neden:**  
Eğer bir sanatçıyı U2 popülasyonunda hiç kimse dinlememiş ise `LF(U2) = 0`. ILF formülünde `|U2| / LF(U2)` işlemi sıfıra bölüme yol açıyor.

**Çözüm:**
```python
def compute_AF_ILF(af_u1, lf_u2, n_u2):
    # replace(0, np.nan) → sıfırları NaN yap,
    # fillna(0) → NaN olan ILF değerini 0 olarak ata
    ilf = np.log(1 + n_u2 / lf_u2.replace(0, np.nan)).fillna(0)
    return np.log(1 + af_u1) * ilf
```

**Öğrenilen:** Seyrek veri matrislerinde hiç dinlenmeyen sanatçılar için NaN chain oluşabiliyor; `.replace(0, np.nan).fillna(0)` pattern'i kullanılabilir.

---

## OTURUM 2 — 7 Mayıs 2026

### ERR-005 · `KeyError: 'User ID'` — Excel sütun adı

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 7 Mayıs 2026, ~09:30 |
| **Dosya** | `mainstream_big.py` — Excel okuma bloğu (satır 13–15) |
| **Aşama** | Büyük dataset (500 kullanıcı) ile ilk çalıştırma |

**Hata Mesajı:**
```
KeyError: 'User ID'
```

**Kök Neden:**  
`dataset_large.xlsx` dosyasındaki Playcounts sheet'i `header=2` parametresiyle (3. satır başlık) okunuyor. Ancak Excel'de başlık satırının gerçek içeriği `"User ID"` yerine `"User\nID"` şeklinde (satır sonu karakteriyle) yazılmıştı. Pandas bu karakteri farklı algıladı.

**Çözüm:**
```python
raw = pd.read_excel(DATASET_PATH, sheet_name="Playcounts", header=2)
raw = raw.rename(columns={
    "User ID":       "user_id",    # bazen "User ID" olarak geliyor
    "Country\nCode": "country_code",  # \n karakteri Excel'den geliyor
    "Country Name":  "country_name"
})
```

**Öğrenilen:** Excel hücre içindeki satır sonları (`Alt+Enter`) pandas'ta `\n` karakteri olarak okunur. Rename sözlüğüne her iki ihtimali eklemek veya `str.strip()` ile temizlemek güvenli yöntemdir.

---

### ERR-006 · `KeyError: 'country_code'` — rename sonrası sütun bulunamıyor

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 7 Mayıs 2026, ~09:45 |
| **Dosya** | `mainstream_big.py` — satır 17–18 |
| **Aşama** | Büyük dataset yüklenirken |

**Hata Mesajı:**
```
KeyError: 'country_code'
```

**Kök Neden:**  
`rename()` çağrısı yapılmadan önce `set_index("user_id")` çağrısı yapılmıştı. İndeks olarak set edilen kolon artık sütunlar arasında yoktu; ardından `rename()` çalıştırıldığında `"user_id"` sütunu bulunamayınca diğer rename'ler de patladı.

**Çözüm:** Önce `rename()`, sonra `set_index()` yapılmalı:
```python
raw = pd.read_excel(...)
raw = raw.rename(columns={...})  # ÖNCE rename
raw = raw.set_index("user_id")   # SONRA set_index
```

**Öğrenilen:** pandas'ta işlem sırası kritik. Bir sütunu index olarak set etmek onu sütun listesinden çıkartır.

---

### ERR-007 · `ValueError: Shape of passed values` — artists listesi boyut uyumsuzluğu

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 7 Mayıs 2026, ~10:00 |
| **Dosya** | `mainstream_big.py` |
| **Aşama** | Artists sheet'ten artist listesi okunurken |

**Hata Mesajı:**
```
ValueError: Shape of passed values is (82, 500), indices imply (81, 500)
```

**Kök Neden:**  
`pd.read_excel(DATASET_PATH, sheet_name="Artists", header=1)` çağrısında `header=1` parametresi Artists sheet'inin 2. satırını başlık olarak alıyor. Ancak bazı Excel versiyonlarında bu hesaplama yanlış satırı başlık olarak seçiyordu; artist listesi 81 yerine 82 eleman içeriyordu (boş bir satır dahil edilmişti).

**Çözüm:**
```python
artists_meta = pd.read_excel(DATASET_PATH, sheet_name="Artists", header=1)
artists = artists_meta["Artist"].dropna().tolist()  # dropna() eklendi
```

**Öğrenilen:** Excel sheet'lerinde boş satırlar pandas tarafından NaN olarak okunur. Liste oluştururken `dropna()` her zaman eklenmelidir.

---

### ERR-008 · `MemoryError` — 500 kullanıcı × 11 ölçüt döngüsü

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 7 Mayıs 2026, ~10:30 |
| **Dosya** | `mainstream_big.py` — `results = []` ana döngü |
| **Aşama** | 11 mainstreaminess ölçütü 500 kullanıcı için hesaplanırken |

**Hata Mesajı:**
```
MemoryError
# veya çok uzun süre çalışıp yanıt vermeme durumu
```

**Kök Neden:**  
Her adımda `pd.concat()` ile büyüyen bir liste üzerinde işlem yapılıyordu. Orijinal küçük dataset (9 kullanıcı) için sorun yoktu; 500 kullanıcıya geçince her döngü iterasyonunda yeni DataFrame oluşturulması ve birleştirilmesi belleği doldurdu.

**Çözüm:** Liste append yaklaşımına geçildi:
```python
# Yanlış (her adımda DataFrame oluşturma)
results_df = pd.DataFrame()
for uid in df.index:
    row_df = pd.DataFrame([{...}])
    results_df = pd.concat([results_df, row_df])  # yavaş, bellek tüketici

# Doğru (Python listesine append, en sonda tek seferlik DataFrame)
results = []
for uid in df.index:
    results.append({...})
results_df = pd.DataFrame(results).set_index("User")
```

**Öğrenilen:** Büyük döngülerde `pd.concat` yerine liste append + son adımda `pd.DataFrame()` çok daha verimlidir.

---

### ERR-009 · `numpy.linalg.LinAlgError` — SVD yakınsama hatası

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 7 Mayıs 2026, ~11:00 |
| **Dosya** | `Mainstream_final.py` — SVD comparison method bloğu |
| **Aşama** | SVD (latent factor) comparison method implementasyonu |

**Hata Mesajı:**
```
numpy.linalg.LinAlgError: SVD did not converge
```

**Kök Neden:**  
`np.linalg.svd()` fonksiyonu tam SVD hesaplamaya çalışıyor ve 500×81 matris üzerinde yakınsama problemi yaşıyordu. Playcount matrisinin çok seyrek (sparse) olması (pek çok hücre = 0) ve bazı sütunların tamamen sıfır olması bu hatanın kaynağıydı.

**Çözüm:** `scipy.sparse.linalg.svds` ile truncated (kısmi) SVD kullanıldı:
```python
# Yanlış
U, sigma, Vt = np.linalg.svd(log_matrix, full_matrices=False)

# Doğru — scipy ile kısmi SVD, daha kararlı
from scipy.sparse.linalg import svds
U, sigma, Vt = svds(log_matrix, k=N_FACTORS)  # k=20 faktör yeterli
```

**Öğrenilen:** Seyrek matrisler için `scipy.sparse.linalg.svds` her zaman `numpy.linalg.svd`'den daha kararlı ve verimlidir. `k` parametresi bellek ve süre kontrolü sağlar.

---

### ERR-010 · `IndexError` — User-KNN boş komşu listesi

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 7 Mayıs 2026, ~11:20 |
| **Dosya** | `Mainstream_final.py` — `recommend_knn()` fonksiyonu |
| **Aşama** | User-KNN comparison method |

**Hata Mesajı:**
```
IndexError: index 0 is out of bounds for axis 0 with size 0
```

**Kök Neden:**  
KNN algoritması kullanıcının komşularını bulamadığı durumda boş liste dönüyordu. Bu durum, özellikle `k=10` komşu istenirken ilgili ülkede yeterince kullanıcı olmadığında (örn. KR = 25 kullanıcı, bazıları sıfır vektöre sahip) ortaya çıktı. Ardından `neighbor_plays.sum(axis=0)` boş numpy array üzerinde çalışıyordu.

**Çözüm:**
```python
def recommend_knn(user_id, n=5):
    distances, indices = knn_model.kneighbors(
        playcount_matrix[user_index[user_id]].reshape(1, -1), 
        n_neighbors=min(K_NEIGHBORS + 1, len(df))  # +1 çünkü kullanıcının kendisi dahil
    )
    neighbor_ids = [df.index[i] for i in indices[0][1:]]
    if len(neighbor_ids) == 0:
        return recommend_popularity(user_id, n)  # fallback
    ...
```

**Öğrenilen:** KNN tabanlı sistemlerde her zaman fallback mekanizması gerekir. Özellikle seyrek verilerde komşu bulunamama durumu beklenmelidir.

---

### ERR-011 · `SettingWithCopyWarning` — pandas veri kopyası uyarısı

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 7 Mayıs 2026, ~11:40 |
| **Dosya** | `Mainstream_final.py` — dataset yükleme bloğu |
| **Aşama** | df hazırlama |

**Hata Mesajı:**
```
SettingWithCopyWarning: 
A value is trying to be set on a copy of a slice from a DataFrame.
Try using .loc[row_indexer,col_indexer] = value instead
```

**Kök Neden:**  
`df = raw[["country_code"] + artist_cols]` ifadesi pandas'a göre bir "slice" (dilim) oluşturuyordu. Ardından bu df üzerinde yeni sütun atanmaya çalışıldığında pandas orijinal veride mi yoksa kopyada mı değişiklik yapıldığından emin olamıyordu.

**Çözüm:**
```python
# .copy() ekleyerek gerçek kopya alındı
df = raw[["country_code"] + artist_cols].rename(
    columns={"country_code": "country"}
).copy()  # <-- bu satır eklendi
```

**Öğrenilen:** pandas'ta slice üzerinde işlem yapacaksanız `.copy()` ile bağımsız kopya oluşturmak hem hatayı ortadan kaldırır hem de beklenmedik side-effect'leri önler.

---

### ERR-012 · Satır numarası uyuşmazlığı — rapordaki satır satır açıklamada

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 7 Mayıs 2026, ~14:00 |
| **Dosya** | `progress_report_4_v2.docx` — satır satır kod açıklaması bölümü |
| **Aşama** | Rapor hazırlama |

**Hata Mesajı:**
```
(Hata değil, tutarsızlık)
Raporda "satır 124: def fraction_measure(...)" yazıyor
Gerçek dosyada satır 128: def fraction_measure(...)
```

**Kök Neden:**  
Kod dosyası birkaç kez güncellendi (fonksiyon sırası değişti, comment satırları eklendi/silindi). Satır numaraları raporla eşleşmez hale geldi. Özellikle 4 fonksiyon başlangıç satırı kaymıştı:

| Raporda | Gerçek |
|---|---|
| 124 | 128 |
| 137 | 144 |
| 151 | 162 |
| 164 | 178 |
| 166 | 180 |

**Çözüm:**  
Python ile kod dosyası satır satır okundu, her fonksiyon başlangıcının gerçek satır numarası tespit edildi ve rapor XML düzeyinde güncellendi.

**Öğrenilen:** Rapor yazma süreci ile kod geliştirme birlikte ilerliyorsa, satır numaraları raporun son haline göre kodun son versiyonu üzerinden alınmalı. Raporun bu bölümü en son tamamlanmalı.

---

## OTURUM 3 — 14 Mayıs 2026 (Bu Oturum)

### ERR-013 · `ModuleNotFoundError: No module named 'openpyxl'`

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 14 Mayıs 2026, ~12:10 |
| **Dosya** | `lastfm_to_excel.py` (yeni oluşturuldu) |
| **Aşama** | Last.fm → Excel dönüştürme scripti ilk çalıştırması |

**Hata Mesajı:**
```
Traceback (most recent call last):
  File "lastfm_to_excel.py", line 21, in <module>
    import openpyxl
ModuleNotFoundError: No module named 'openpyxl'
```

**Kök Neden:**  
`openpyxl` paketi bu Python ortamında kurulu değildi. Daha önce `pandas` ile birlikte gelmişti (ortak bağımlılık); ancak bu ortamda ayrıca kurulması gerekiyordu.

**Çözüm:**
```bash
pip install openpyxl pandas numpy
```

Çıktı:
```
Successfully installed et-xmlfile-2.0.0 openpyxl-3.1.5
```

**Öğrenilen:** `requirements.txt` dosyasına `openpyxl` eklenmeli (zaten fourth progress'teki requirements.txt'te `openpyxl` vardı, ancak ana klasörde kurulu değildi). Her zaman `pip install -r requirements.txt` ile kurulum yapılmalı.

---

### ERR-014 · `UnicodeEncodeError` — Windows terminal türkçe/unicode karakter

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 14 Mayıs 2026, ~12:15 |
| **Dosya** | `lastfm_to_excel.py` — son print satırı |
| **Aşama** | Excel dosyası kaydedildikten sonra print ifadesi |

**Hata Mesajı:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '✓' in position 2: 
character maps to <undefined>
```

**Kök Neden:**  
Windows terminali (cmd/PowerShell) varsayılan olarak `cp1254` (Windows Türkçe) encoding kullanıyor. `✓` karakteri (`✓`) bu encoding'de tanımlı değil. Ancak bu hata **dosya kaydedildikten sonra** oluştu — yani Excel dosyası başarıyla yazılmıştı.

**Çözüm:**  
Dosya başarıyla oluştu (`168 KB`), hata yalnızca terminal çıktısında idi. Scriptteki `✓` ve `│` gibi unicode karakterler ASCII alternatiflerine çevrildi:

```python
# Yanlış (terminal patlatıyor)
print(f"\n✓ Saved: {OUT_PATH}")

# Doğru
print(f"\n[OK] Saved: {OUT_PATH}")
```

Kalıcı çözüm için terminalde `chcp 65001` (UTF-8) komutu çalıştırılabilir veya script başına şu satır eklenebilir:

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')  # Python 3.7+
```

**Öğrenilen:** Windows'ta `cp1254` encoding'i `→`, `✓`, `│`, `█` gibi box-drawing karakterleri ve birçok unicode sembolü desteklemiyor. Cross-platform script yazarken ya ASCII kullan ya da dosyanın en başına `sys.stdout.reconfigure` ekle.

---

### ERR-015 · Last.fm TSV dosyası encoding sorunu — `\x00` null bytes

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 14 Mayıs 2026, ~12:20 |
| **Dosya** | `lastfm_to_excel.py` — `pd.read_csv()` okuma aşaması |
| **Aşama** | 17.5M satırlık plays dosyası okunurken |

**Hata Mesajı:**
```
ParserWarning: Falling back to the 'python' engine because the 'c' engine does 
not support sep=None with delim_whitespace=False; you can avoid this warning by 
specifying engine='python'.
```
*(ve bazı satırlarda sanatçı adında bozuk karakter)*

**Kök Neden:**  
Last.fm 360K veri seti `UTF-8` ile kodlanmış ancak bazı satırlarda `latin-1` veya bozuk encoding var. Özellikle `ü`, `ö`, `ñ`, `ø` gibi karakterler içeren sanatçı adları bozuk okunabiliyor.

**Çözüm:**  
`pd.read_csv()` çağrısına `encoding='utf-8', errors='replace'` parametresi eklendi ve artist name normalizasyonu yapıldı:

```python
plays = pd.read_csv(
    PLAYS_TSV, sep="\t", header=None,
    names=["user", "artist_id", "artist_name", "plays"],
    encoding="utf-8", errors="replace",  # bozuk karakterleri ? ile değiştir
    chunksize=CHUNK,
)
# Sonra normalizasyon:
plays["artist_name"] = plays["artist_name"].str.strip().str.lower()
```

**Öğrenilen:** Real-world müzik veri setlerinde encoding tutarsızlığı çok yaygın. `errors='replace'` ile devam edilebilir; sanatçı adları lowercase yapılarak eşleştirme tutarlı hale gelir.

---

### ERR-016 · KR (South Korea) kullanıcı sayısı yetersiz

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 14 Mayıs 2026, ~12:25 |
| **Dosya** | `lastfm_to_excel.py` — kullanıcı seçme bloğu |
| **Aşama** | 12 ülke için proportional sampling |

**Hata Mesajı:**
```
(Hata değil, uyarı)
KR (Korea, Republic of): Sadece 427 kullanıcı mevcut.
Quota=25, ancak gender/age bilgisi olan sadece ~180 kullanıcı var.
```

**Kök Neden:**  
Last.fm 360K veri setinde Güney Kore kullanıcısı sayısı diğer ülkelere göre çok düşük (427 kişi). Bu, Güney Kore'nin 2006-2010 yıllarında Last.fm kullanımının sınırlı olmasından kaynaklanıyor. Sendai veri setinin toplama dönemi (2006-2009) K-Pop'un küresel yükselişinden önceye denk geliyor.

**Çözüm:**  
KR için quota 25'e düşürüldü (diğer ülkelerin 31-50 arasında olduğu yerde). Script `min(quota, available)` mantığıyla çalışıyor:

```python
if len(pool_complete) >= quota:
    chosen = pool_complete.sample(quota, random_state=42)
elif len(pool) >= quota:
    chosen = pool.sample(quota, random_state=42)
else:
    chosen = pool  # mevcut ne varsa al
```

**Öğrenilen:** Gerçek veri setlerinde ülke dağılımı dengesiz olabilir. Raporda bu sınırlılık belgelenmelidir: "KR için yalnızca 25 kullanıcı mevcut, sentetik datasetteki 36 kullanıcıdan farklıdır."

---

## OTURUM 3 DEVAMI — 14 Mayıs 2026 (Kod İnceleme)

### ERR-017 · `Fg:AF·ILF,u:AF·ILF` ve `Fc:AF·ILF,u:AF·ILF` birebir aynı hesaplanıyor

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 14 Mayıs 2026, ~13:00 |
| **Dosya** | `Mainstream_final.py` — satır 160 ve 162 |
| **Aşama** | 4. Progress kod incelemesi sırasında tespit edildi |
| **Durum** | **Düzeltildi ✅ — 14 Mayıs 2026** |

**Hata Mesajı:**
```
(Runtime hatası değil — mantık hatası, sessizce yanlış sonuç üretir)
Measure Fg:AF·ILF,u:AF·ILF ve Fc:AF·ILF,u:AF·ILF
her kullanıcı için aynı değeri üretiyor.
```

**Sorunlu Kod:**
```python
# Satır 160 — Fg (GLOBAL referans olması lazım)
"Fg:AF·ILF,u:AF·ILF":  round(fraction_measure(af_ilf_user_c, af_ilf_c_g), 4),
# Satır 162 — Fc (COUNTRY referans — bu doğru)
"Fc:AF·ILF,u:AF·ILF":  round(fraction_measure(af_ilf_user_c, af_ilf_c_g), 4),
```

Her iki satırda argümanlar aynı: `fraction_measure(af_ilf_user_c, af_ilf_c_g)`.
- `Fg` → referans popülasyon GLOBAL AF·ILF olmalı: `compute_AF_ILF(AF_global, LF_global, N_total)`
- `Fc` → referans popülasyon COUNTRY AF·ILF: `af_ilf_c_g` ✓

**Kök Neden:**  
Global AF·ILF profili (`AF_ILF_global`) hiç hesaplanmıyor. Kod sadece `AF_ILF_country_global` sözlüğünü oluşturuyor (her ülke için ayrı); genel bir "tüm kullanıcılar üzerinden global AF·ILF" profili eksik.

**Doğru Çözüm:**
```python
# Satır 83-85 civarına ekle (AF_ILF_country_global hesaplandıktan sonra):
AF_ILF_global = compute_AF_ILF(AF_global, LF_global, N_total)

# Satır 160'ı düzelt:
"Fg:AF·ILF,u:AF·ILF":  round(fraction_measure(af_ilf_user_c, AF_ILF_global), 4),
# Satır 162 değişmez (zaten doğru):
"Fc:AF·ILF,u:AF·ILF":  round(fraction_measure(af_ilf_user_c, af_ilf_c_g),    4),
```

**Etkisi:** 11 ölçütten 2'si (F3 ve F5) şu an aynı değer üretiyor. Rapordaki ölçüt tablosu bu durumu yansıtıyor — hoca kodu çalıştırırsa iki sütunun birebir aynı olduğunu fark edebilir.

**Öğrenilen:** Measure isimlerindeki `g` (global) ve `c` (country) öneki, referans popülasyonun ne olduğunu belirtir. Benzer isimdeki ölçütlerin gerçekten farklı hesaplandığı doğrulanmalıdır.

---

### ERR-018 · `pop_novelty` 500 kullanıcı, diğerleri 50 kullanıcı — eşitsiz karşılaştırma

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 14 Mayıs 2026, ~13:05 |
| **Dosya** | `Mainstream_final.py` — satır 287 |
| **Aşama** | 4. Progress kod incelemesi sırasında tespit edildi |
| **Durum** | **Düzeltildi ✅ — 14 Mayıs 2026** |

**Hata Mesajı:**
```
(Runtime hatası değil — metodolojik tutarsızlık)
Karşılaştırma tablosunda "sample of 50 users" yazıyor
ama Popularity Baseline tüm 500 kullanıcıdan hesaplanıyor.
```

**Sorunlu Kod:**
```python
# Satır 287 — Popularity: TÜM 500 kullanıcı (YANLIŞ)
for uid in df.index:
    ...pop_novelty...      # 500 kullanıcı

# Satır 358 — KNN: ilk 50 kullanıcı
for uid in df.index[:50]:  # 50 kullanıcı

# Satır 437 — SVD: ilk 50 kullanıcı
for uid in df.index[:50]:  # 50 kullanıcı

# Satır 461 — Mainstreaminess: ilk 50 kullanıcı
for uid in df.index[:50]:  # 50 kullanıcı
```

**Kök Neden:**  
Popularity Baseline hesabı sonradan diğer metodlar eklenmeden önce yazıldı; tüm kullanıcılar üzerinden çalışması makul görünüyordu. Diğer metodlar eklenince örneklem tutarsızlığı fark edilmedi.

**Doğru Çözüm:**
```python
# Satır 287'yi değiştir:
for uid in df.index[:50]:   # df.index → df.index[:50]
    ...
```

**Etkisi:** Popularity Baseline için Novelty = 0.000 değişmez (tüm kullanıcılar zaten global top-5'i duymuş), ancak metodolojik tutarlılık sağlanır. Rapordaki karşılaştırma tablosu güncellenmesi gerekmez.

**Öğrenilen:** Farklı metodlar için metrik hesaplamaları yazılırken kullanılan örneklem boyutu ilk satırda sabit bir değişkene bağlanmalıdır:
```python
EVAL_SAMPLE = df.index[:50].tolist()  # bir kez tanımla, her yerde kullan
```

---

### ERR-019 · `recommend_mainstreaminess` zaten duyulan sanatçıları filtrelemiyor — adil olmayan karşılaştırma

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 14 Mayıs 2026, ~13:10 |
| **Dosya** | `Mainstream_final.py` — `get_top_candidates()` ve `recommend_mainstreaminess()` fonksiyonları (satır 223–257) |
| **Aşama** | 4. Progress kod incelemesi sırasında tespit edildi |
| **Durum** | **Düzeltildi ✅ — 14 Mayıs 2026** |

**Hata Mesajı:**
```
(Runtime hatası değil — tasarım sorunu)
Novelty sonuçlarında tutarsızlık:
  Popularity Baseline  : Novelty = 0.000  (filtreleme YOK)
  User-KNN (k=10)      : Novelty = 1.000  (filtreleme VAR)
  SVD (20 factors)     : Novelty = 1.000  (filtreleme VAR)
  Proposed (MS)        : Novelty = 0.000  (filtreleme YOK)
```

**Kök Neden:**  
KNN (satır 347–351) ve SVD (satır 417–420) kullanıcının zaten duyduğu sanatçıları `-1` / `-inf` ile maskeleyerek öneri listesinden çıkarır. `recommend_mainstreaminess` ise sabit bir "ülkenin top-n sanatçısı" listesi döner — kullanıcının daha önce dinleyip dinlemediğini kontrol etmez.

**Doğru Çözüm:** `get_top_candidates` yerine kullanıcıya özel filtreleme:
```python
def recommend_mainstreaminess(user_id, n=5):
    ...
    strategy   = {"High": "global", "Low": "local", "Mid": "mixed"}[level]
    # Yeterince aday al (n*3), sonra zaten duyulanları filtrele
    candidates = get_top_candidates(country, n * 3)
    user_plays  = df.loc[user_id, artist_cols]
    filtered    = [a for a in candidates[strategy] if user_plays[a] == 0]
    # Yeterli öneri yoksa filtresiz listeye dön (fallback)
    recs = filtered[:n] if len(filtered) >= n else candidates[strategy][:n]
    return {
        ...
        "recommendations": recs,
    }

def get_top_candidates(country_code, n=15):  # n büyütüldü
    global_top = AF_global.nlargest(n).index.tolist()
    local_top  = AF_ILF_country_global[country_code].nlargest(n).index.tolist()
    mixed      = list(dict.fromkeys(global_top + local_top))[:n]
    return {"global": global_top, "local": local_top, "mixed": mixed}
```

**Etkisi:** Düzeltme sonrası Novelty ve Personalization değerleri değişecek. Rapordaki Tablo 3 (karşılaştırma) güncellenmelidir.

**Öğrenilen:** Karşılaştırmalı değerlendirmede tüm metodların aynı koşullarda test edilmesi (already-heard filtreleme yapıp yapmama) metodolojik tutarlılık açısından zorunludur. Bir metod filtre yaparken diğeri yapmazsa "elma ile armut" karşılaştırması olur.

---

### ERR-020 · Kullanılmayan import: `train_test_split` (satır 7)

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 14 Mayıs 2026, ~13:15 |
| **Dosya** | `Mainstream_final.py` — satır 7 |
| **Aşama** | 4. Progress kod incelemesi sırasında tespit edildi |
| **Durum** | **Düzeltildi ✅ — 14 Mayıs 2026** |

**Hata Mesajı:**
```
(Hata değil — temizlik sorunu)
from sklearn.model_selection import train_test_split
# Bu import hiçbir yerde kullanılmıyor
```

**Kök Neden:**  
SVD değerlendirmesi için `train_test_split` kullanılması planlanmıştı; sonradan `np.random.choice` ile manual split tercih edildi, ancak import temizlenmedi.

**Çözüm:**
```python
# Satır 7'yi sil
from sklearn.model_selection import train_test_split  # ← sil
```

**Öğrenilen:** Kullanılmayan importlar kodu gereksiz yere uzatır ve okuyucuyu yanıltır. Kod tamamlandıktan sonra import'lar gözden geçirilmeli.

---

### ERR-021 · Kullanılmayan `artists` değişkeni (satır 34) — dead code

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 14 Mayıs 2026, ~13:16 |
| **Dosya** | `Mainstream_final.py` — satır 34 |
| **Aşama** | 4. Progress kod incelemesi sırasında tespit edildi |
| **Durum** | **Düzeltildi ✅ — 14 Mayıs 2026** |

**Hata Mesajı:**
```
(Hata değil — dead code)
artists = artists_meta["Artist"].tolist()
# Bu liste kodun hiçbir yerinde kullanılmıyor
# Tüm artist erişimleri artist_cols değişkeni üzerinden yapılıyor
```

**Kök Neden:**  
Başlangıçta artist sıralamasını korumak için bu liste planlandı; ardından DataFrame sütun sırası (`artist_cols`) yeterli oldu, liste kullanılmadı.

**Çözüm:** Satırı silmek veya silmeden bırakmak (işlevsel etkisi yok). Raporda "34. satır: artists listesi için ayrı Sheet okunur" şeklinde açıklama yapılmışsa tutarlılık açısından bırakılabilir.

---

### ERR-022 · Rapor `personalization_score` kod bloğu gerçek koddan farklı

| Alan | Detay |
|---|---|
| **Tarih/Saat** | 14 Mayıs 2026, ~13:20 |
| **Dosya** | `progress_report_4_v2.docx` — Section 4.12, Code 12 bloğu |
| **Aşama** | 4. Progress rapor incelemesi sırasında tespit edildi |
| **Durum** | **Düzeltildi ✅ — 14 Mayıs 2026** |

**Hata Mesajı:**
```
(Hata değil — rapor-kod tutarsızlığı)
Raporda gösterilen personalization_score fonksiyonu
gerçek Mainstream_final.py'deki versiyondan farklı.
```

**Rapordaki versiyon (basitleştirilmiş):**
```python
rec_sets = [set(rec_func(uid,n=n)['recommendations']) for uid in sample_users]
```

**Gerçek koddaki versiyon (satır 477–482):**
```python
rec_sets = []
for uid in sample_users:
    try:
        recs = rec_func(uid, n=n)["recommendations"]
        rec_sets.append(set(recs))
    except Exception:
        continue
if len(rec_sets) < 2:
    return 0.0
```

**Kök Neden:**  
Rapor hazırlanırken kod fonksiyonu sadeleştirilerek gösterildi (tek satır list comprehension); gerçek kodda hata yönetimi (`try/except`) ve boş liste koruması (`if len < 2`) vardı. Rapor kodu ile çalışan kod senkronize tutulmadı.

**Çözüm:** Rapordaki Code 12 bloğunu gerçek kod ile güncellenmeli; ya da açıklamaya "simplified for clarity" notu eklenmeli.

**Öğrenilen:** Raporda gösterilen kod ile çalışan kod birebir aynı olmalı. "Sadeleştirilmiş" gösterim raporu zayıflatır — hoca orijinal kodu karşılaştırabilir.

---

## Genel Paternler ve Önlemler

### Karşılaşılan Hata Kategorileri

| Kategori | Adet | Örnekler |
|---|---|---|
| Matematiksel (sıfır/NaN) | 3 | ERR-002, ERR-003, ERR-004 |
| pandas veri erişim | 4 | ERR-001, ERR-005, ERR-006, ERR-007 |
| Performans/Bellek | 2 | ERR-008, ERR-009 |
| Algoritma (ML) | 2 | ERR-009, ERR-010 |
| Kodlama uyarıları | 2 | ERR-011, ERR-014 |
| Rapor tutarsızlığı | 2 | ERR-012, ERR-022 |
| Bağımlılık/ortam | 2 | ERR-013, ERR-014 |
| Veri kalitesi | 2 | ERR-015, ERR-016 |
| Mantık/Metodoloji hatası | 4 | ERR-017, ERR-018, ERR-019, ERR-020 |
| Dead code | 2 | ERR-020, ERR-021 |

---

### Tekrarlayan Sorunlar ve Genel Çözümler

**1. Seyrek Matris / Sıfır Değer Sorunları**
```python
# Her hesaplamada şu deseni kullan:
.replace(0, np.nan).fillna(0)   # bölme işlemlerinde
+ epsilon                        # log işlemlerinde
if s > 0 else series            # normalize fonksiyonunda
```

**2. Excel Okuma Sorunları**
```python
# Her zaman rename'i önce yap
raw = pd.read_excel(path, sheet_name="...", header=2)
raw = raw.rename(columns={...})  # önce
raw = raw.set_index("user_id")   # sonra
# Artist listesi için dropna zorunlu
artists = sheet["Artist"].dropna().tolist()
```

**3. Büyük Döngüler**
```python
# İyi yaklaşım: liste + son adımda DataFrame
results = []
for uid in df.index:
    results.append({...})
results_df = pd.DataFrame(results)  # bir kez
```

**4. Windows Terminal Encoding**
```python
# Script başına ekle:
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
```

**5. Kurulum**
```bash
# Her ortamda önce kurulum:
pip install -r requirements.txt
# requirements.txt içinde: pandas, openpyxl, numpy<2.0.0, scipy, scikit-learn
```

---

## Dosya Değişiklik Geçmişi

| Tarih | Dosya | Değişiklik | Neden |
|---|---|---|---|
| 12 Mar 2026 | `User-recommender.py` | İlk taslak — temel recommender | Proje başlangıcı |
| 19 Mar 2026 | `recom.py` | Geliştirilmiş versiyon | Midterm hazırlık |
| 29 Mar 2026 | `maintream.py` | 11 ölçüt eklendi | Midterm implementasyon |
| 10 Nis 2026 | `mainstream_big.py` (midterm) | Hardcoded veri → Excel okuma | Dataset genişletme |
| 10 Nis 2026 | `dataset_large.xlsx` | 500u×81a×12c sentetik veri | Midterm teslim |
| 26 Nis 2026 | `mainstream_big.py` (second) | Excel path düzeltmesi | Second Progress |
| 25 Nis 2026 | `mainstream_big.py` (ana) | 193 satır son versiyon | Ana klasör |
|  7 May 2026 | `Mainstream_final.py` | +3 comparison method (Pop/KNN/SVD) | Fourth Progress |
|  7 May 2026 | `requirements.txt` | Bağımlılık listesi oluşturuldu | Fourth Progress |
| 14 May 2026 | `lastfm_to_excel.py` | Last.fm → Excel dönüştürücü | Gerçek veri entegrasyonu |
| 14 May 2026 | `dataset_lfm.xlsx` | 489u×81a×12c gerçek LFM verisi | Fourth Progress eklentisi |
| 14 May 2026 | `error_log.md` | ERR-017..022 eklendi (kod inceleme bulguları) | Hata kaydı güncelleme |

---

*Bu dosya proje süresince karşılaşılan tüm teknik sorunların kaydıdır. Hata raporunu güncel tutmak için her oturumda yeni hatalar bu dosyaya eklenmelidir.*
