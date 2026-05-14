import numpy as np
import pandas as pd
from scipy.stats import kendalltau
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# SAMPLE DATASET
# ============================================================
# 3 ülke: TR (Türkiye), FI (Finlandiya), US (Amerika)
# 10 sanatçı, 9 kullanıcı
# Her hücre: kullanıcının o sanatçıyı kaç kez dinlediği (playcount)

np.random.seed(42)

artists = [
    "Radiohead", "Pink Floyd", "Metallica", "Daft Punk", "Coldplay",
    "Grup Yorum", "Mabel Matiz", "Stam1na", "Nightwish", "CMX"
]

# Kullanıcı verisi: [user_id, country, artist_playcounts...]
data = {
    "user_id": ["u1","u2","u3","u4","u5","u6","u7","u8","u9"],
    "country": ["TR","TR","TR","FI","FI","FI","US","US","US"],
    # Global popüler sanatçılar (Radiohead, Pink Floyd, Metallica, Daft Punk, Coldplay)
    "Radiohead":  [500, 420, 380,  80,  60,  40, 600, 550, 480],
    "Pink Floyd": [600, 580, 510,  50,  30,  20, 500, 460, 420],
    "Metallica":  [450, 400, 350, 200, 180, 150, 300, 280, 260],
    "Daft Punk":  [300, 280, 260,  90,  80,  70, 400, 380, 360],
    "Coldplay":   [200, 190, 180, 100,  90,  80, 350, 330, 310],
    # Türkiye'ye özgü sanatçılar
    "Grup Yorum": [800, 750, 700,   5,   3,   2,   0,   0,   0],
    "Mabel Matiz":[600, 580, 550,   8,   5,   3,   0,   0,   0],
    # Finlandiya'ya özgü sanatçılar
    "Stam1na":    [  5,   3,   2, 900, 850, 800,   0,   0,   0],
    "Nightwish":  [ 10,   8,   5, 700, 680, 650,  20,  15,  10],
    "CMX":        [  3,   2,   1, 600, 580, 560,   0,   0,   0],
}

df = pd.DataFrame(data)
df = df.set_index("user_id")

print("=" * 65)
print("ÖRNEK VERİ SETİ (User-Artist Playcount Matrix)")
print("=" * 65)
print(df.to_string())
print()

# ============================================================
# TEMEL TANIMLAR
# ============================================================
artist_cols = artists
countries = df["country"].unique()
N_total = len(df)  # toplam kullanıcı sayısı

# ---- AF (Artist Frequency) hesaplama ----
# AF_a_U1 = U1 kullanıcılarının artist a'yı toplam dinleme sayısı

def compute_AF(user_set):
    """Verilen kullanıcı kümesi için her sanatçının AF değerini döndürür."""
    return df.loc[user_set, artist_cols].sum()

def compute_LF(user_set):
    """Verilen kullanıcı kümesi için her sanatçının LF (dinleyici sayısı) değerini döndürür."""
    return (df.loc[user_set, artist_cols] > 0).sum()

# Global profiller
all_users = df.index.tolist()
AF_global = compute_AF(all_users)
LF_global = compute_LF(all_users)

# Ülke bazlı profiller
country_users = {c: df[df["country"] == c].index.tolist() for c in countries}
AF_country = {c: compute_AF(country_users[c]) for c in countries}
LF_country = {c: compute_LF(country_users[c]) for c in countries}

# ============================================================
# AF-ILF HESAPLAMA (Makale Denklemi 1)
# AF·ILF(a, U1, U2) = log(1 + AF_a_U1) * log(1 + |U2| / LF_a_U2)
# ============================================================

def compute_AF_ILF(af_u1, lf_u2, n_u2):
    """
    af_u1: Series - U1 için AF değerleri
    lf_u2: Series - U2 için LF değerleri
    n_u2:  int    - U2 büyüklüğü
    """
    ilf = np.log(1 + n_u2 / lf_u2.replace(0, np.nan)).fillna(0)
    return np.log(1 + af_u1) * ilf

# Her ülke için AF-ILF (country level AF, global level ILF)
AF_ILF_country_global = {
    c: compute_AF_ILF(AF_country[c], LF_global, N_total) for c in countries
}

print("=" * 65)
print("BÖLÜM 1: AF / LF / AF-ILF DEĞERLERİ")
print("=" * 65)

summary_rows = []
for a in artists:
    row = {"Artist": a, "Global AF": AF_global[a], "Global LF": LF_global[a]}
    for c in countries:
        row[f"AF ({c})"] = AF_country[c][a]
        row[f"LF ({c})"] = LF_country[c][a]
        row[f"AF-ILF ({c})"] = round(AF_ILF_country_global[c][a], 3)
    summary_rows.append(row)

summary_df = pd.DataFrame(summary_rows).set_index("Artist")
print(summary_df.to_string())
print()

# ============================================================
# BÖLÜM 2: 11 MAINSTREAMİNESS ÖLÇÜTLERİ
# ============================================================

# --- Normalize AF (sum-to-unity) ---
def normalize(series):
    s = series.sum()
    return series / s if s > 0 else series

# --- FRACTION-BASED MEASURES ---

def fraction_measure(af_user, af_pop):
    """
    F = 1 - (1/|A|) * sum( |af_u - af_p| / max(af_u, af_p) )
    af_user, af_pop: normalize edilmiş Series
    """
    af_u = normalize(af_user)
    af_p = normalize(af_pop)
    denom = pd.concat([af_u, af_p], axis=1).max(axis=1).replace(0, np.nan)
    diff = (af_u - af_p).abs() / denom
    return 1 - diff.fillna(0).mean()

# --- KULLBACK-LEIBLER DIVERGENCE ---

def kl_divergence_sym(p, q, epsilon=1e-10):
    """
    Symmetrized KL Divergence (inverted so higher = more mainstream)
    D = [ sum(p*log(p/q)) + sum(q*log(q/p)) ] / 2
    """
    p = normalize(p) + epsilon
    q = normalize(q) + epsilon
    kl_pq = (p * np.log(p / q)).sum()
    kl_qp = (q * np.log(q / p)).sum()
    sym_kl = (kl_pq + kl_qp) / 2
    return 1 / (1 + sym_kl)  # invert: daha yakın mainstream → daha yüksek değer

# --- KENDALL'S TAU ---

def kendall_tau_measure(af_user, af_pop):
    """
    Kullanıcı ve popülasyon ranking'lerinin Kendall tau korelasyonu.
    """
    ranks_u = af_user.rank(ascending=False)
    ranks_p = af_pop.rank(ascending=False)
    tau, _ = kendalltau(ranks_u, ranks_p)
    return tau

# ============================================================
# HER KULLANICI İÇİN TÜM 11 ÖLÇÜTLERİ HESAPLA
# ============================================================

results = []

for uid in df.index:
    user_country = df.loc[uid, "country"]
    af_user = df.loc[uid, artist_cols].astype(float)
    af_c = AF_country[user_country].astype(float)
    af_g = AF_global.astype(float)

    # AF-ILF for user (AF computed for user, ILF on country level)
    lf_c = LF_country[user_country]
    n_c  = len(country_users[user_country])
    af_ilf_user_c = compute_AF_ILF(af_user, lf_c, n_c)

    # AF-ILF for country (AF on country level, ILF globally)
    af_ilf_c_g = AF_ILF_country_global[user_country]

    row = {
        "User": uid,
        "Country": user_country,
        # --- FRACTION-BASED (5 ölçüt) ---
        "Fg:AF,u:AF":           round(fraction_measure(af_user, af_g), 4),
        "Fg:AF,u:AF·ILF":       round(fraction_measure(af_ilf_user_c, af_g), 4),
        "Fg:AF·ILF,u:AF·ILF":   round(fraction_measure(af_ilf_user_c, af_ilf_c_g), 4),
        "Fc:AF,u:AF":           round(fraction_measure(af_user, af_c), 4),
        "Fc:AF·ILF,u:AF·ILF":   round(fraction_measure(af_ilf_user_c, af_ilf_c_g), 4),
        # --- KL DIVERGENCE (3 ölçüt) ---
        "Dg:AF,u:AF":           round(kl_divergence_sym(af_user, af_g), 4),
        "Dc:AF,u:AF":           round(kl_divergence_sym(af_user, af_c), 4),
        "Dc:AF·ILF,u:AF·ILF":   round(kl_divergence_sym(af_ilf_user_c, af_ilf_c_g), 4),
        # --- KENDALL'S TAU (3 ölçüt) ---
        "Cg:AF,u:AF":           round(kendall_tau_measure(af_user, af_g), 4),
        "Cc:AF,u:AF":           round(kendall_tau_measure(af_user, af_c), 4),
        "Cc:AF·ILF,u:AF·ILF":   round(kendall_tau_measure(af_ilf_user_c, af_ilf_c_g), 4),
    }
    results.append(row)

results_df = pd.DataFrame(results).set_index("User")

print("=" * 65)
print("BÖLÜM 2: 11 MAINSTREAMİNESS ÖLÇÜTLERİ - TÜM KULLANICILAR")
print("(Yüksek değer = Mainstream'e daha yakın)")
print("=" * 65)

# Fraction-based
print("\n--- FRACTION-BASED MEASURES (F) ---")
f_cols = ["Country","Fg:AF,u:AF","Fg:AF,u:AF·ILF","Fg:AF·ILF,u:AF·ILF","Fc:AF,u:AF","Fc:AF·ILF,u:AF·ILF"]
print(results_df[f_cols].to_string())

print("\n--- KL DIVERGENCE MEASURES (D) ---")
d_cols = ["Country","Dg:AF,u:AF","Dc:AF,u:AF","Dc:AF·ILF,u:AF·ILF"]
print(results_df[d_cols].to_string())

print("\n--- KENDALL'S TAU MEASURES (C) ---")
c_cols = ["Country","Cg:AF,u:AF","Cc:AF,u:AF","Cc:AF·ILF,u:AF·ILF"]
print(results_df[c_cols].to_string())

# ============================================================
# BÖLÜM 3: ÜLKE BAZLI ORTALAMA MAINSTREAMİNESS
# ============================================================
print("\n" + "=" * 65)
print("BÖLÜM 3: ÜLKE BAZLI ORTALAMA MAINSTREAMİNESS SKORLARI")
print("=" * 65)

measure_cols = [c for c in results_df.columns if c != "Country"]
country_avg = results_df.groupby("Country")[measure_cols].mean().round(4)
print(country_avg.to_string())

# ============================================================
# BÖLÜM 4: KULLANICI MAINSTREAMİNESS SEVİYESİ (Low / Mid / High)
# ============================================================
print("\n" + "=" * 65)
print("BÖLÜM 4: KULLANICI SINIFLANDIRMASI - Cc:AF,u:AF ÖLÇÜTÜİLE")
print("(Makale'nin en iyi performans gösteren ölçütü)")
print("=" * 65)

scores = results_df["Cc:AF,u:AF"].values
thresholds = [np.percentile(scores, 33), np.percentile(scores, 66)]
def classify(v):
    if v <= thresholds[0]: return "Low"
    elif v <= thresholds[1]: return "Mid"
    else: return "High"
results_df["Cc:AF,u:AF_level"] = results_df["Cc:AF,u:AF"].apply(classify)
level_df = results_df[["Country","Cc:AF,u:AF","Cc:AF,u:AF_level"]].copy()
level_df.columns = ["Country", "Cc:AF,u:AF Score", "Mainstreaminess Level"]
print(level_df.to_string())

print("\n" + "=" * 65)
print("BÖLÜM 5: AF-ILF ÜLKE-SPESİFİK SANATÇI PROFILLERI")
print("(Globalden farklı, ülkeye özgü popüler sanatçılar)")
print("=" * 65)

for c in countries:
    top_af = AF_country[c].nlargest(3)
    top_afilf = AF_ILF_country_global[c].nlargest(3)
    print(f"\n{c} - Top 3 AF (global popüler baskın):  {', '.join([f'{a}({v:.0f})' for a,v in top_af.items()])}")
    print(f"{c} - Top 3 AF-ILF (ülkeye özgü):         {', '.join([f'{a}({v:.2f})' for a,v in top_afilf.items()])}")

print("\n✓ Tüm hesaplamalar tamamlandı.")