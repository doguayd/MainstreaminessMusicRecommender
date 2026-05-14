# COME424/1 — Hoca Gereksinimleri ve Dikkat Noktaları

> **Ders:** Recommender Systems (COME424/1)  
> **Hoca:** Dr. Öğr. Üyesi Gamze Uslu — Üsküdar Üniversitesi  
> **Grup:** Doğukan Aydın, Elif Dalmış, Yaman Balcı, Salih Çetin, Alperen Keskin  
> **Kaynak:** Ders ses kaydı transkripleri + office hours konuşması + assignment metinleri

---

## 1. Genel Proje Yapısı

### Seçilen Makale
**Schedl & Bauer (2018)** — *An Analysis of Global and Regional Mainstreaminess for Personalized Music Recommender Systems*

Hoca her grup için farklı bir makale seçtirdi. Tüm proje boyunca **bu makalenin** yöntemi, karşılaştırma metodları, dataset'i ve sonuçları referans alınacak.

### Teslim Takvimi
| Aşama | İçerik |
|---|---|
| **Midterm** | En az 10 kavram seçimi, Python implementasyonu, satır satır açıklama, dataset özellikleri |
| **Progress Report 1–3** | Haftalık gelişim raporları (slayt formatı dahil) |
| **Progress Report 4** | Proposed approach + comparison methods implementasyon detayları + satır satır kod açıklaması |
| **Final** | Tüm raporların birleşimi + önerilen yaklaşım + karşılaştırma + sonuçlar |

---

## 2. Midterm Gereksinimleri (Detaylı)

Hoca midterm için şunları söyledi:

> *"Pick at least 10 concepts which are the parts of the methods mentioned in your selected article for part A."*

### ✅ Yapılması gerekenler:
1. **En az 10 kavram** — makaledeki metodların bileşenleri (bizim için: AF, LF, AF-ILF, TF-IDF, normalizasyon, fraction measure, KL divergence, Kendall's tau, global mainstreaminess, local mainstreaminess, Low/Mid/High sınıflandırma)
2. **Bu kavramlar raporda bölüm başlıkları olacak** — her kavram ayrı alt bölüm
3. **Her kavram için Python kodu** — ana koddan o kavrama ait parçalar ayrılacak, her alt başlık altında kendi kodu olacak
4. **Kodun çıktısı gösterilecek** — tablolar ve grafikler dahil
5. **Sonuçlar açıklanacak** — tablolar ve plotlar ile
6. **Satır satır ve bölüm bölüm kod açıklaması**
7. **Kullanılan dataset'in özellikleri açıklanacak**
8. **Sample dataset kullanılabilir** — "Your code will be executed on sample datasets"

### 📌 Hocamızın vurguladığı nokta:
> *"11 alt başlık, bunlara denk gelen kod kısımlarını ana koddan ayırıp o altbaşlık altına koyarak... ana kodu parçalara ayırarak... en sona da kod açıklaması"*

Bu demek ki: tek blok kod değil, her kavram için ayrı küçük kod bloğu + en sona tüm kodun satır satır açıklaması.

---

## 3. Progress Report 4 Gereksinimleri

Hoca office hours'ta şunları söyledi:

> *"4. progress report'unuzda gene bir rapor isteyeceğim ama nasıl bir rapor isteyeceğim; proposed approach'ınızın implementation detayları, bir de compare ettiğiniz approach'ların implementation detaylarını içeren bir rapor isteyeceğim"*

### ✅ Yapılması gerekenler:
1. **Report 1:** Problem tanımı + proposed approach implementasyon detayları + comparison approach'ların implementasyon detayları
2. **Report 2:** Kod satır satır ve bölüm bölüm açıklaması
3. **Yeni rapor** — eski raporun üzerine değil, bağımsız yeni belge
4. **Finalde birleşimi istenecek**

### 📌 Hocamızın vurguladığı nokta:
> *"Kodda değiştirmenizi isteyeceğim bir şey olmayacak"* — ama ekleme yapmak isteğe bağlı:  
> *"Biz istersek hani birkaç tane güncelleme yapmayı da planlıyoruz kodla alakalı — olabildiğince iyi bir versiyon yapın, projenizi daha iyi yapmak için kodunuzu da değiştirmeniz gerekiyorsa değiştirin"*

**Deadline: 18 Mayıs 2026**

---

## 4. Sunum (Progress Report 3 — PPTX) Gereksinimleri

Hoca tahtaya şu yapıyı çizdi:

```
Slayt 1:  Title (kapak — numarasız)
Slayt #1: Novelty
Slayt #2: Method (Proposed Approach — detail)
Slayt #3: Experimental Setup & Results
Slayt #4: Impact
Slayt #5: Sustainability
```

### Slayt #1 — Novelty içeriği:
- **Problem Definition** — problemin sınırları ne, ne dahil ne değil, domandaki zorluklar
- **Motivation** — neden bu konuyla çalışıyorsunuz, literatürdeki boşluk nerede
- **Proposed Approach** (brief) — sadece kısa özet, detay değil
- **Contributions of This Study** — 3 madde halinde katkılar

> *"Novelty, something that has not been done before. No research team can do everything in a single article, therefore some items are already left as future work. You can pick your novelty based on those future work sections."*

> *"It doesn't have to be a great novelty, just pick something small that has not been addressed."*

### Slayt #2 — Method içeriği:
- Önerilen yaklaşım **detaylı** — block diagram çiz
- Her kavram block diagram'da bir bileşen olacak
- Her bileşen hakkında önemli detaylar

> *"You can draw a block diagram here in this next slide such that each of those concepts will be a component in your diagram, in your block diagram."*

### Slayt #3 — Experimental Setup & Results:
- Karşılaştırılan metodlar (method 1, 2, 3...) ve neden seçildikleri
- Dataset özellikleri (kaç instance, sınıflar, neden kullanıldı)
- Kendi implementasyonunuzun sonuçları — tablolar ve plotlar
- **Kendi çalıştırdığınız kodun çıktısı olacak**, makaleden kopyalanmış değil

> *"Whatever you put inside your results slide must be the output of your own implementation."*

### Slayt #4 — Impact içeriği:
- Bu çalışma başarılı olsaydı hangi alanlar/uygulamalar/nüfus fayda görürdü
- Sayısal verilerle desteklenmeli (istatistikler, nüfus verileri)

> *"Once your results become successful, what domains, what applications, what fields will benefit... Let's say millions of people suffering from this disease... Once we perform this study, this many population will benefit."*

### Slayt #5 — Sustainability içeriği:
- Çözümün uygulanabilirliği
- İleride devam etme potansiyeli

### ⚠️ Önemli: Sayfa numaralandırması
- Kapak sayfası **numarasız**
- Novelty'den başlayarak 1, 2, 3, 4, 5

### ⚠️ Önemli: Öğrenci Kongresi
Hoca bazı grupları **Öğrenci Kongresi'nde sunum yapmak için seçecek**:
- Seçilirseniz sunum zorunlu — yapmazsanız FF
- Değerlendirme kriteri: Novelty %30, Method %30, Impact %20, Sustainability %20
- Geniş impactlı proje konuları avantajlı

---

## 5. Final Gereksinimleri

Hoca final için şunları belirtti:

> *"You will implement the proposed approach. You will implement the methods compared against proposed approach in your selected article. Then you will run these methods on the same sets of datasets used in your selected article. You will display your results in tables and plots using the same table and plots structure in your selected article. Then you will compare your results against the results displayed in your selected article."*

### ✅ Yapılması gerekenler:
1. **Proposed approach'ı implement et** — makaledeki yöntemi kodla
2. **Comparison methods'ları implement et** — makaledeki karşılaştırma metodlarını kodla
3. **Aynı dataset'i kullan** — makaledeki dataset'i (LFM-1b) veya benzerini
4. **Sonuçları tablolar ve plotlarla göster** — makaledeki tablo/plot yapısıyla aynı formatta
5. **Makalenin sonuçlarıyla karşılaştır** — kendi sonuçlarınız vs. makaledeki sayılar

### 📌 Dataset hakkında:
> *"Yayına dönüştürme planınız varsa publicly available dataset'ler üstünde de bir şeyler yapmaya çalışın ama yayın mecburiyetiniz yok."*  
> *"Generated dataset kabul edilir, ama normalde bir yayına dönüştürecekseniz generated dataset'ler şu an çok kabul görmüyor."*

**Bizim durumumuz:** AI ile üretilmiş 500 kullanıcı × 81 sanatçı × 12 ülke dataset — ders kapsamında kabul edilir. Gerçek veri kullanmak bonus sayılır.

---

## 6. Raporun Genel Formatı

Hoca midterm assignment metninden:

> *"The concepts mentioned in the above item will be the section titles in your report. You will explain each of those concepts in detail. You will exemplify each of those concepts with the corresponding Python implementation. You will show the output of each of the pieces of code that corresponds to these concepts. You will also explain your results using tables and plots, which are generated by executing the pieces of code you provide."*

### Rapor yapısı (bizim uygulamamız):

```
Kapak
A. Novelty
B. Impact  
C. Sustainability
1. 11 Mainstreaminess Measures (tablo ile)
2. TF-IDF & AF-ILF
3. Comparison Methods
4. LFM-1b Dataset
5. Python Implementation
   5.1  Artist Frequency (AF)          ← kod + çıktı
   5.2  Listener Frequency (LF)        ← kod + çıktı
   5.3  AF-ILF                         ← kod + çıktı + plot
   5.4  Normalization                  ← kod
   5.5  Fraction-based Measure         ← kod + çıktı
   5.6  KL Divergence                  ← kod + çıktı
   5.7  Kendall's Tau                  ← kod + çıktı
   5.8  Global vs Local Mainstreaminess ← plot
   5.9  AF vs AF-ILF Comparison        ← plot
   5.10 Low/Mid/High Classification    ← tablo + plot
   5.11 Country-Specific Differences   ← tablo
6. Line-by-Line Code Explanation
References
```

---

## 7. Hocamızın Genel Dikkat Noktaları

### ✅ Yapılması:
- Kodun **kendi implementasyonunuzun çıktısını** gösterin — makaleden kopyalamayın
- Tablolar ve plotlar **kodunuzu çalıştırarak** üretilmeli
- Her kavramı **detaylı açıklayın** — yüzeysel geçmeyin
- Literatürden **kısa atıflar** yapın (related studies ne kapsıyor, siz ne ekliyorsunuz)
- **Contribution** açık olmalı — 3 maddede ne katkı sağladınız
- **Dataset'in özelliklerini** açıklayın (kaç kullanıcı, sanatçı, ülke, neden bu dataset)
- Kod açıklaması **gerçekten satır satır** olmalı — bölüm bölüm yetmez
- Rapor ve sunum **aynı problemi** ele alır, format farklıdır

### ❌ Yapılmaması:
- Makaledeki tabloları/sonuçları olduğu gibi kopyalamak
- Kodun çıktısını elle yazmak (çalıştırılmış kod çıktısı olmalı)
- Çok büyük dataset mecburiyeti yok — ders kapsamında generated kabul edilir
- Kodu tamamen değiştirme mecburiyeti yok — hoca zorlamıyor

### 💡 Hocamızın tavsiyesi:
> *"Bu projeleri CV'nize koymanız için yapıyoruz. Ondan dolayı olabildiğince iyi bir versiyon yapın."*

---

## 8. Comparison Methods — Ne Olmalı?

Makaledeki Schedl & Bauer (2018) şu metodları karşılaştırmıştır:
- Farklı mainstreaminess ölçütleri kendi aralarında (11 ölçüt)
- RMSE bazlı değerlendirme (Table 9)

Biz final için **recommendation sistem seviyesinde** karşılaştırma ekliyoruz:

| Method | Açıklama | Bizim implementasyonumuz |
|---|---|---|
| **Popularity Baseline** | Global en popüler sanatçıları herkese öner | `recommend_popularity()` |
| **User-KNN (k=10)** | Benzer kullanıcıların dinlediklerini öner | `recommend_knn()` |
| **SVD (20 faktör)** | Latent faktör matris ayrıştırması | `recommend_svd()` |
| **Proposed (Mainstreaminess)** | Level'e göre Global/Local/Mixed strateji | `recommend_mainstreaminess()` |

**Değerlendirme metrikleri:**
- **Novelty** — önerilen sanatçının kullanıcı tarafından daha önce dinlenmemiş olma oranı
- **Personalization** — kullanıcılar arası Jaccard diversity (pairwise)

---

## 9. Dataset Hakkında Hocamızın Tutumu

> *"Normalde bir yayına dönüştürecekseniz generated dataset'ler şu an çok kabul görmüyor ama ders kapsamında üstüne çalışacağınız bir data olması bakımından, yani hazır dataset'lerde onun karşılığını bulamadıysanız yapabilirsiniz."*

> *"Dataset'i daha çok büyütmenizi istiyor musunuz? — Yok hayır istemiyorum."*

**Sonuç:** 500 kullanıcı × 81 sanatçı × 12 ülke yeterli. Gerçek LFM-1b kullanmak bonus, zorunlu değil.

**AI ile üretildiğini raporda belirtmek gerekiyor:**
> Makalede: *"AI-assisted expansion documented in report Section 4.1"*

---

## 10. Öğrenci Kongresi Değerlendirme Kriterleri

Hoca şu dağılımı verdi:

| Kriter | Ağırlık |
|---|---|
| Novelty | %30 |
| Method | %30 |
| Impact | %20 |
| Sustainability | %20 |

> *"If your topic is a wider impact topic, this will be beneficial for you to get higher scores in this competition."*

Müzik mainstreaminess → kültürel çeşitlilik, filter bubble, 600M+ Spotify kullanıcısı etkisi = geniş impact.

---

## 11. Önemli Tarihler

| Tarih | Teslim |
|---|---|
| 16 Nisan 2026 | Midterm (teslim edildi ✅) |
| 18 Mayıs 2026 | **Progress Report 4** (deadline) |
| Final | Tüm raporların birleşimi + final implementasyon |
| ? | Öğrenci Kongresi (hoca seçilenleri bildirecek) |

---

## 12. Mevcut Dosya Durumu

| Dosya | Açıklama | Durum |
|---|---|---|
| `mainstream_final.py` | 515 satır — 11 ölçüt + 3 comparison method + evaluation | ✅ Hazır |
| `mainstream_big.py` | 193 satır — sadece proposed approach (midterm kodu) | ✅ Hazır |
| `dataset_large.xlsx` | 500u × 81a × 12c, 4 sheet | ✅ Hazır |
| `final_report_v9.docx` | Ana midterm raporu — A/B/C + Section 1-6 + References | ✅ Hazır |
| `progress_report_4_v2.docx` | 4. progress report — Report1 + Report2 (515 satır açıklaması) | ✅ Hazır (eksik satırlar var) |
| `presentation.pptx` | 6 slayt sunum | ✅ Hazır |

### ⚠️ Hâlâ eksik:
- `progress_report_4_v2.docx` içinde 179 satır açıklanmamış — tamamlanması gerekiyor
- Gerçek LFM-1b verisiyle test (opsiyonel ama güçlü olur)

---

## 13. Yeni Claude Oturumunda Başlarken Söylenecekler

Yeni oturumda Claude'a şunları ver:

```
Bu proje COME424/1 Recommender Systems dersi için hazırlanıyor.
Makale: Schedl & Bauer (2018) — Mainstreaminess for Personalized Music Recommender Systems
Grup: Doğukan Aydın (240200019), Elif Dalmış (230201082), Yaman Balcı (220201081), 
      Salih Çetin (220201060), Alperen Keskin (230201094)
Hoca: Dr. Öğr. Üyesi Gamze Uslu

Mevcut dosyalar:
- mainstream_final.py (515 satır, 4 method)
- mainstream_big.py (193 satır, proposed approach)
- dataset_large.xlsx (500 kullanıcı, 81 sanatçı, 12 ülke)
- final_report_v9.docx (ana rapor)
- progress_report_4_v2.docx (4. ilerleme raporu — eksik satırlar var)
- presentation.pptx

Yapılacaklar: [buraya görev yaz]
```
