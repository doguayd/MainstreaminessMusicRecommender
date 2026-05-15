# Makale vs. Bizim İmplementasyonumuz

> **Makale:** Schedl, M. & Bauer, C. (2018). *An Analysis of Global and Regional Mainstreaminess
> for Personalized Music Recommender Systems.*
> Transactions of the International Society for Music Information Retrieval (TISMIR), 1(1), 52–69.

---

## BÖLÜM 1 — Makale Ne Yapıyor?

### 1.1 Temel Problem

Müzik akış platformlarındaki (Spotify, Last.fm, Deezer gibi) öneri sistemleri, sanatçı popülerliğini
**global** bir metrikle ölçer: kim daha çok dinlendiyse o önerilir. Ama "popüler" kavramı ülkeden
ülkeye çok farklıdır.

- Finlandiya'da mainstream = Nightwish, HIM, CMX
- Türkiye'de mainstream = Duman, Mor ve Ötesi, Sezen Aksu
- Güney Kore'de mainstream = BTS, IU, EXO

Bu durumu görmezden gelen bir sistem herkese aynı global top listeyi önerir — kültürel bağlamı
tamamen yok sayar. Makale bu problemi **mainstreaminess** (ana akımcılık) kavramıyla formalize eder.

---

### 1.2 Mainstreaminess Nedir?

> "Mainstreaminess ölçütü, bir kullanıcının dinleme profilinin genel nüfusun dinleme profiliyle
> ne kadar örtüştüğünü sayısal olarak ifade eder."

- **Yüksek mainstreaminess (High):** Kullanıcı global/yerel mainstream'i dinliyor (herkes gibi)
- **Düşük mainstreaminess (Low):** Kullanıcı niş/alternatif tarzları tercih ediyor
- **Orta mainstreaminess (Mid):** İkisi arasında

---

### 1.3 Makale'nin Kullandığı Veri Seti

| Özellik | Detay |
|---|---|
| **Veri seti** | LFM-1b (Last.fm 1 Billion dataset) |
| **Kullanıcı sayısı** | ~120,000 aktif kullanıcı (filtreden sonra) |
| **Sanatçı sayısı** | ~600,000+ sanatçı |
| **Ülke sayısı** | 47 ülke |
| **Kayıt dönemi** | 2005–2014 |
| **Veri türü** | Gerçek Last.fm play log'ları |

---

### 1.4 Makale'nin Önerdiği 11 Mainstreaminess Ölçütü

Makalenin çekirdeği budur. Üç farklı matematiksel aileden toplam **11 ölçüt** tanımlanır:

#### Aile 1 — Fraction-based (F): 5 ölçüt

Her ölçüt, kullanıcı profilinin popülasyon profiliyle **örtüşme oranını** ölçer.
Formül (Paper Equation 3):

```
F = 1 - (1/|A|) * Σ [ |af_u(a) - af_p(a)| / max(af_u(a), af_p(a)) ]
```

| Ölçüt | Kullanıcı profili | Referans popülasyon |
|---|---|---|
| `Fg:AF,u:AF` | Kullanıcı AF (raw playcount) | Global AF |
| `Fg:AF,u:AF·ILF` | Kullanıcı AF·ILF | Global AF |
| `Fg:AF·ILF,u:AF·ILF` | Kullanıcı AF·ILF | **Global** AF·ILF |
| `Fc:AF,u:AF` | Kullanıcı AF | Ülke AF |
| `Fc:AF·ILF,u:AF·ILF` | Kullanıcı AF·ILF | **Ülke** AF·ILF |

#### Aile 2 — KL Divergence (D): 3 ölçüt

İki dağılım arasındaki **bilgi teorik uzaklığı** ölçer, ters çevrilerek yüksek = daha mainstream.
Formül (Paper Equation 4):

```
D = 1 / (1 + KL_sym(p_u || p_ref))
```

| Ölçüt | Referans |
|---|---|
| `Dg:AF,u:AF` | Global AF |
| `Dc:AF,u:AF` | Ülke AF |
| `Dc:AF·ILF,u:AF·ILF` | Ülke AF·ILF |

#### Aile 3 — Kendall's tau (C): 3 ölçüt

Kullanıcının sanatçı **sıralama düzeni** ile popülasyonun sıralamasının ne kadar uyuştuğunu ölçer.

| Ölçüt | Referans |
|---|---|
| `Cg:AF,u:AF` | Global AF |
| `Cc:AF,u:AF` | Ülke AF ← **sınıflandırma için kullanılan** |
| `Cc:AF·ILF,u:AF·ILF` | Ülke AF·ILF |

---

### 1.5 AF ve AF·ILF Nedir?

**AF (Artist Frequency):** Bir sanatçının toplam dinlenme sayısı.
```
AF(a, U) = Σ playcount(u, a)  for u ∈ U
```

**LF (Listener Frequency):** Bir sanatçıyı en az bir kez dinleyen kullanıcı sayısı.
```
LF(a, U) = |{ u ∈ U : playcount(u,a) > 0 }|
```

**AF·ILF:** TF-IDF'in müzik versiyonu. Globally ubiquitous sanatçıları penalize eder,
yerel olarak özgün sanatçıları ön plana çıkarır. (Paper Equation 1):
```
AF·ILF(a, U1, U2) = log(1 + AF(a, U1)) × log(1 + |U2| / LF(a, U2))
```

---

### 1.6 Low / Mid / High Sınıflandırması

Makale, `Cc:AF,u:AF` skoru üzerinden her kullanıcıyı üç gruba ayırır:
- 33. persentil altı → **Low** mainstreaminess
- 33. – 66. persentil arası → **Mid** mainstreaminess
- 66. persentil üstü → **High** mainstreaminess

---

### 1.7 Makalede Yapılan Analizler

Makale esas olarak bir **analiz çalışmasıdır** — yani bir şeyler önerilmiyor, ölçütler karşılaştırılıyor:

1. 11 ölçütün birbirleriyle korelasyonu inceleniyor (Table 2–4)
2. Ülkelere göre ortalama mainstreaminess profili çıkarılıyor
3. AF vs AF·ILF'in farklı ülke "sesini" nasıl öne çıkardığı gösteriliyor
4. Low/Mid/High kullanıcıların öneri kalitesi RMSE ile değerlendiriliyor (Table 9)
5. Mainstreaminess grubu düşük kullanıcılarda standart CF sistemlerinin başarısız olduğu gösteriliyor

---

### 1.8 Makale'nin Temel Bulguları

| Bulgu | Açıklama |
|---|---|
| AF·ILF > AF | AF·ILF, yerel mainstream sanatçıları çok daha iyi tespit ediyor |
| Low users ≠ well-served | Düşük mainstreaminess'li kullanıcılar mevcut CF sistemleriyle kötü öneriler alıyor |
| Country-level matters | Ülke bazlı profil, global profile göre çok daha anlamlı ayrışma sağlıyor |
| Cc:AF,u:AF en stabil | Kendall tau ülke bazlı ölçüt en tutarlı sınıflandırmayı veriyor |

---

## BÖLÜM 2 — Biz Ne Yaptık? Neyi Ekledik / Değiştirdik?

### 2.1 Makaleden Aynen Aldıklarımız ✅

| Bileşen | Makale'de | Bizim koddaki karşılığı |
|---|---|---|
| AF formülü | Equation 2 | `compute_AF()` — satır 50 |
| LF formülü | Equation 2 | `compute_LF()` — satır 57 |
| AF·ILF formülü | Equation 1 | `compute_AF_ILF()` — satır 76 |
| Fraction measure (F) | Equation 3 | `fraction_measure()` — satır 113 |
| KL divergence (D) | Equation 4 | `kl_divergence_sym()` — satır 125 |
| Kendall's tau (C) | Equation 5 | `kendall_tau_measure()` — satır 136 |
| 11 ölçütün tamamı | Table 5 | `results` döngüsü — satır 150–173 |
| Low/Mid/High sınıflandırması | Section 3.3 | Satır 195–202 |
| Cc:AF,u:AF temel ölçüt olarak | Section 3.3 | `results_df["Level"]` — satır 195 |

---

### 2.2 Makaleden Farklı Yaptığımız Şeyler 🔄

#### Fark 1 — Veri Seti

| | Makale | Bizim implementasyon |
|---|---|---|
| **Veri kaynağı** | LFM-1b (gerçek, 1 milyar kayıt) | `dataset_large.xlsx` (AI-üretimi, 500 kullanıcı) |
| **Gerçek veri** | ✅ var | `dataset_lfm.xlsx` (Last.fm 360K'dan türetildi) |
| **Kullanıcı sayısı** | ~120,000 | 500 (sentetik) / 489 (gerçek) |
| **Sanatçı sayısı** | ~600,000 | 81 |
| **Ülke sayısı** | 47 | 12 (TR, US, DE, GB, FR, PL, BR, FI, SE, RU, JP, KR) |
| **Neden?** | Ders kapsamında bu boyut gerekli değil; hoca "dataset büyütmeni istemiyorum" dedi |

#### Fark 2 — AF·ILF Global Profil (ERR-017 Düzeltmesi)

Makale `Fg:AF·ILF,u:AF·ILF` ve `Fc:AF·ILF,u:AF·ILF` ölçütlerini açıkça tanımlıyor:
- **`Fg`** → referans popülasyon = TÜM kullanıcılar üzerinden hesaplanan global AF·ILF
- **`Fc`** → referans popülasyon = kullanıcının ülkesi üzerinden hesaplanan AF·ILF

İlk implementasyonumuzda her iki ölçüt de ülke profiline bakıyordu (hata). Düzelttik:

```python
# Eklenen satır (satır 90) — makalenin Fg tanımıyla tutarlı:
AF_ILF_global = compute_AF_ILF(AF_global, LF_global, N_total)

# Fg için global profil kullanıldı (artık doğru):
"Fg:AF·ILF,u:AF·ILF": round(fraction_measure(af_ilf_user_c, AF_ILF_global), 4),
# Fc için ülke profili (zaten doğruydu):
"Fc:AF·ILF,u:AF·ILF": round(fraction_measure(af_ilf_user_c, af_ilf_c_g),    4),
```

---

### 2.3 Makalenin Üzerine Eklediğimiz Şeyler 🆕

Makale bir analiz çalışmasıdır — öneri sistemi bileşeni sınırlıdır. Biz bunu
**çalışır bir öneri sistemi + karşılaştırmalı değerlendirme** pipeline'ına genişlettik.

---

#### Ekleme 1 — Mainstreaminess Tabanlı Öneri Fonksiyonu

Makale Low/Mid/High sınıflandırmasını tanımlıyor ama "bu kullanıcıya hangi sanatçıları öner?"
sorusunu tam cevaplamıyor. Biz bunu implement ettik:

```python
def recommend_mainstreaminess(user_id, n=5):
    level    = results_df.loc[user_id, "Level"]   # Low / Mid / High
    country  = results_df.loc[user_id, "Country"]
    strategy = {"High": "global", "Low": "local", "Mid": "mixed"}[level]
    candidates = get_top_candidates(country, n=15)
    # Already-heard filtering (fair comparison with KNN/SVD)
    user_plays = df.loc[user_id, artist_cols]
    filtered   = [a for a in candidates[strategy] if user_plays[a] == 0]
    recs = filtered[:n] if len(filtered) >= n else candidates[strategy][:n]
    return {"recommendations": recs, ...}
```

Strateji mantığı:
- **High** → Global AF top sanatçılar (global mainstream)
- **Low** → AF·ILF top sanatçılar (yerel özgün, dünyada daha az popüler)
- **Mid** → Global + Local karışımı

---

#### Ekleme 2 — 3 Karşılaştırma Metodu

Makale RMSE bazlı değerlendirme yapıyor ama öneri sistemlerini karşılaştırmıyor.
Biz üç standart baseline ekledi ve mainstreaminess tabanlı yaklaşımı bunlarla kıyasladık:

| Metod | Kod | Açıklama |
|---|---|---|
| **Popularity Baseline** | `recommend_popularity()` | Her kullanıcıya global en popüler 5 sanatçı |
| **User-KNN (k=10)** | `recommend_knn()` | Cosine benzerlik + en yakın 10 komşu |
| **SVD (20 faktör)** | `recommend_svd()` | `scipy.sparse.linalg.svds` ile matris ayrıştırması |
| **Proposed (Mainstreaminess)** | `recommend_mainstreaminess()` | Yukarıdaki ekleme |

KNN detayı:
```
sim(u, v) = (r_u · r_v) / (||r_u|| × ||r_v||)
```

SVD detayı:
```
R ≈ U_k Σ_k V_k^T + μ_u   (k=20 latent factor, log-scale + mean-centering)
```

---

#### Ekleme 3 — Novelty ve Personalization Metrikleri

Makale RMSE ile değerlendirme yapıyor. Biz kullanıcı deneyimini daha iyi yansıtan
iki ek metrik implement ettik:

**Novelty** — Kullanıcının daha önce duymadığı sanatçıların oranı:
```python
novelty = 1 - mean(heard_fraction)   # heard_fraction = kaç öneri zaten dinlenmiş
```

**Personalization** — İki kullanıcının öneri listeleri ne kadar farklı (Jaccard distance):
```python
personalization = mean( 1 - |A∩B| / |A∪B| )  # tüm kullanıcı çiftleri üzerinden
```

Sonuçlar (50 kullanıcı örneklem):

| Metod | Novelty | Personalization |
|---|---|---|
| Popularity Baseline | 0.000 | 0.000 |
| User-KNN (k=10) | 1.000 | 0.905 |
| SVD (20 factors) | 1.000 | 0.933 |
| **Proposed (MS-AF·ILF)** | **0.100** | **0.189** |

---

#### Ekleme 4 — Tutarlı Değerlendirme Çerçevesi (EVAL_SAMPLE)

Tüm metodlar aynı 50 kullanıcı üzerinden değerlendiriliyor:

```python
EVAL_SAMPLE = df.index[:50].tolist()  # bir kez tanımla, her metodda kullan
```

Bu sayede metodlar arasındaki karşılaştırma **adil** — farklı örneklem boyutları
sonuçları yanıltmıyor.

---

#### Ekleme 5 — Last.fm 360K'dan Gerçek Veri Seti Türetme

Makale LFM-1b kullanıyor ama bu veri seti kamuya açık değil.
Biz Last.fm 360K'dan (kamuya açık) bir alt küme oluşturduk:

```python
# lastfm_to_excel.py — bizim dönüştürücü scriptimiz
# Top 81 sanatçı (≥5 dinleyici), proportional ülke örneklemesi
# → dataset_lfm.xlsx: 489 kullanıcı × 81 sanatçı × 12 ülke
```

Aynı şema (Playcounts / Artists / Users / Countries sheet'leri),
`Mainstream_final.py` ile doğrudan uyumlu.

---

#### Ekleme 6 — Zaten-Dinleneni Filtrele (Fair Novelty)

Makale filtreleme stratejisini tartışmıyor. Biz KNN ve SVD ile tutarlı olmak için
`recommend_mainstreaminess()` fonksiyonuna already-heard filtrelemesi ekledik:

- `candidates` havuzunu n=5'ten n=15'e büyüttük (filtreleme için yer açmak)
- Kullanıcının sıfırın üstünde playcount verdiği sanatçılar listeden çıkarıldı
- Fallback: yeterli bilinmeyen sanatçı yoksa tam havuzdan alınıyor

Bu fix öncesi MS Novelty = 0.000, fix sonrası = 0.100.

---

## BÖLÜM 3 — Özet Karşılaştırma Tablosu

| Bileşen | Makalede Var mı? | Bizim Durumumuz |
|---|---|---|
| AF, LF formülleri | ✅ | Aynen implement ettik |
| AF·ILF formülü | ✅ | Aynen implement ettik |
| 11 ölçüt (F/D/C aileleri) | ✅ | Aynen implement ettik |
| Low/Mid/High sınıflandırması | ✅ | Aynen implement ettik (Cc:AF,u:AF) |
| Ülke bazlı analiz | ✅ | Implement ettik (12 ülke) |
| AF vs AF·ILF karşılaştırması | ✅ | Section 1 çıktısı |
| LFM-1b veri seti | ✅ | ❌ Erişim yok; sentetik + LFM-360K kullandık |
| 47 ülke | ✅ | ❌ 12 ülkeyle sınırlandırdık |
| RMSE değerlendirmesi | ✅ | ✅ SVD için implement ettik |
| **Mainstreaminess öneri fonksiyonu** | ❌ (sadece analiz) | **✅ Biz ekledik** |
| **Popularity Baseline karşılaştırması** | ❌ | **✅ Biz ekledik** |
| **User-KNN karşılaştırması** | ❌ | **✅ Biz ekledik** |
| **SVD karşılaştırması** | ❌ | **✅ Biz ekledik** |
| **Novelty metriği** | ❌ | **✅ Biz ekledik** |
| **Personalization metriği** | ❌ | **✅ Biz ekledik** |
| **Already-heard filtreleme** | ❌ | **✅ Biz ekledik** |
| **Global AF·ILF profili (Fg fix)** | ✅ (tanım var) | **✅ Hatayı tespit edip düzelttik** |

---

## BÖLÜM 4 — Bizim Katkılarımızın Önemi

Makale "mainstreaminess ölçülür ve anlamlıdır" diyor.
Biz bunu "mainstreaminess öneri sistemine nasıl entegre edilir?" sorusuna kadar götürdük:

1. **Çalışır öneri motoru:** 11 ölçütü hesaplamaktan öneri listesi üretmeye köprü
2. **Adil karşılaştırma:** 3 standart baselines ile Novelty/Personalization karşılaştırması
3. **Gerçek veri validasyonu:** LFM-360K ile sentetik verinin tutarlılığı test edildi
4. **Açık kaynak pipeline:** Makale LFM-1b gerektiriyor (kamuya kapalı),
   biz herkesin çalıştırabileceği bir implementasyon ürettik

---

*Son güncelleme: 15 Mayıs 2026*
