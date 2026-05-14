import numpy as np
import pandas as pd
from scipy.stats import kendalltau
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# SAMPLE DATASET
# ============================================================
# 3 countries: TR (Turkey), FI (Finland), US (United States)
# 10 artists, 9 users
# Each cell: number of times the user listened to that artist (playcount)

np.random.seed(42)

artists = [
    "Radiohead", "Pink Floyd", "Metallica", "Daft Punk", "Coldplay",
    "Grup Yorum", "Mabel Matiz", "Stam1na", "Nightwish", "CMX"
]

# User data: [user_id, country, artist_playcounts...]
data = {
    "user_id": ["u1","u2","u3","u4","u5","u6","u7","u8","u9"],
    "country": ["TR","TR","TR","FI","FI","FI","US","US","US"],
    # Globally popular artists (Radiohead, Pink Floyd, Metallica, Daft Punk, Coldplay)
    "Radiohead":  [500, 420, 380,  80,  60,  40, 600, 550, 480],
    "Pink Floyd": [600, 580, 510,  50,  30,  20, 500, 460, 420],
    "Metallica":  [450, 400, 350, 200, 180, 150, 300, 280, 260],
    "Daft Punk":  [300, 280, 260,  90,  80,  70, 400, 380, 360],
    "Coldplay":   [200, 190, 180, 100,  90,  80, 350, 330, 310],
    # Turkey-specific artists
    "Grup Yorum": [800, 750, 700,   5,   3,   2,   0,   0,   0],
    "Mabel Matiz":[600, 580, 550,   8,   5,   3,   0,   0,   0],
    # Finland-specific artists
    "Stam1na":    [  5,   3,   2, 900, 850, 800,   0,   0,   0],
    "Nightwish":  [ 10,   8,   5, 700, 680, 650,  20,  15,  10],
    "CMX":        [  3,   2,   1, 600, 580, 560,   0,   0,   0],
}

df = pd.DataFrame(data)
df = df.set_index("user_id")

print("=" * 65)
print("SAMPLE DATASET (User-Artist Playcount Matrix)")
print("=" * 65)
print(df.to_string())
print()

# ============================================================
# BASIC DEFINITIONS
# ============================================================
artist_cols = artists
countries = df["country"].unique()
N_total = len(df)  # total number of users

# ---- Artist Frequency (AF) computation ----
# AF_{a,U1} = total playcount of artist a across user set U1

def compute_AF(user_set):
    """Returns the AF value for each artist across the given user set."""
    return df.loc[user_set, artist_cols].sum()

def compute_LF(user_set):
    """Returns the LF (listener frequency) for each artist across the given user set."""
    return (df.loc[user_set, artist_cols] > 0).sum()

# Global profiles
all_users = df.index.tolist()
AF_global = compute_AF(all_users)
LF_global = compute_LF(all_users)

# Country-level profiles
country_users = {c: df[df["country"] == c].index.tolist() for c in countries}
AF_country = {c: compute_AF(country_users[c]) for c in countries}
LF_country = {c: compute_LF(country_users[c]) for c in countries}

# ============================================================
# AF-ILF COMPUTATION (Paper Equation 1)
# AF·ILF(a, U1, U2) = log(1 + AF_{a,U1}) * log(1 + |U2| / LF_{a,U2})
# ============================================================

def compute_AF_ILF(af_u1, lf_u2, n_u2):
    """
    af_u1 : Series  - AF values for population U1
    lf_u2 : Series  - LF values for population U2
    n_u2  : int     - size of population U2 (|U2|)
    """
    ilf = np.log(1 + n_u2 / lf_u2.replace(0, np.nan)).fillna(0)
    return np.log(1 + af_u1) * ilf

# AF-ILF for each country (country-level AF, global-level ILF)
AF_ILF_country_global = {
    c: compute_AF_ILF(AF_country[c], LF_global, N_total) for c in countries
}

print("=" * 65)
print("SECTION 1: AF / LF / AF-ILF VALUES")
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
# SECTION 2: 11 MAINSTREAMINESS MEASURES
# ============================================================

# --- Normalisation (sum-to-unity) ---
def normalize(series):
    """
    series : Pandas Series of non-negative numeric values
    Returns the sum-to-unity normalised version (probability distribution).
    """
    s = series.sum()
    return series / s if s > 0 else series

# --- FRACTION-BASED MEASURES ---

def fraction_measure(af_user, af_pop):
    """
    Implements the fraction-based mainstreaminess formula (F family, Table 5):
    F = 1 - (1/|A|) * sum( |af_u - af_p| / max(af_u, af_p) )

    af_user : Series - playcount profile for a single user
    af_pop  : Series - playcount profile for the reference population
    """
    af_u = normalize(af_user)
    af_p = normalize(af_pop)
    denom = pd.concat([af_u, af_p], axis=1).max(axis=1).replace(0, np.nan)
    diff = (af_u - af_p).abs() / denom
    return 1 - diff.fillna(0).mean()

# --- KULLBACK-LEIBLER DIVERGENCE ---

def kl_divergence_sym(p, q, epsilon=1e-10):
    """
    Symmetrized KL Divergence (inverted so that higher = more mainstream):
    D = [ sum(p*log(p/q)) + sum(q*log(q/p)) ] / 2

    p       : Series - user profile
    q       : Series - reference population profile
    epsilon : float  - small constant to prevent log(0), default 1e-10
    """
    p = normalize(p) + epsilon
    q = normalize(q) + epsilon
    kl_pq = (p * np.log(p / q)).sum()
    kl_qp = (q * np.log(q / p)).sum()
    sym_kl = (kl_pq + kl_qp) / 2
    return 1 / (1 + sym_kl)  # invert: closer to mainstream -> higher value

# --- KENDALL'S TAU ---

def kendall_tau_measure(af_user, af_pop):
    """
    Rank-order correlation between user and population profiles (C family, Table 5).

    af_user : Series - playcount profile for a single user
    af_pop  : Series - playcount profile for the reference population
    """
    ranks_u = af_user.rank(ascending=False)
    ranks_p = af_pop.rank(ascending=False)
    tau, _ = kendalltau(ranks_u, ranks_p)
    return tau

# ============================================================
# COMPUTE ALL 11 MEASURES FOR EVERY USER
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
        # --- FRACTION-BASED (5 measures) ---
        "Fg:AF,u:AF":           round(fraction_measure(af_user, af_g), 4),
        "Fg:AF,u:AF·ILF":       round(fraction_measure(af_ilf_user_c, af_g), 4),
        "Fg:AF·ILF,u:AF·ILF":   round(fraction_measure(af_ilf_user_c, af_ilf_c_g), 4),
        "Fc:AF,u:AF":           round(fraction_measure(af_user, af_c), 4),
        "Fc:AF·ILF,u:AF·ILF":   round(fraction_measure(af_ilf_user_c, af_ilf_c_g), 4),
        # --- KL DIVERGENCE (3 measures) ---
        "Dg:AF,u:AF":           round(kl_divergence_sym(af_user, af_g), 4),
        "Dc:AF,u:AF":           round(kl_divergence_sym(af_user, af_c), 4),
        "Dc:AF·ILF,u:AF·ILF":   round(kl_divergence_sym(af_ilf_user_c, af_ilf_c_g), 4),
        # --- KENDALL'S TAU (3 measures) ---
        "Cg:AF,u:AF":           round(kendall_tau_measure(af_user, af_g), 4),
        "Cc:AF,u:AF":           round(kendall_tau_measure(af_user, af_c), 4),
        "Cc:AF·ILF,u:AF·ILF":   round(kendall_tau_measure(af_ilf_user_c, af_ilf_c_g), 4),
    }
    results.append(row)

results_df = pd.DataFrame(results).set_index("User")

print("=" * 65)
print("SECTION 2: ALL 11 MAINSTREAMINESS MEASURES -- ALL USERS")
print("(Higher value = closer to mainstream)")
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
# SECTION 3: COUNTRY-LEVEL AVERAGE MAINSTREAMINESS
# ============================================================
print("\n" + "=" * 65)
print("SECTION 3: COUNTRY-LEVEL AVERAGE MAINSTREAMINESS SCORES")
print("=" * 65)

measure_cols = [c for c in results_df.columns if c != "Country"]
country_avg = results_df.groupby("Country")[measure_cols].mean().round(4)
print(country_avg.to_string())

# ============================================================
# SECTION 4: USER MAINSTREAMINESS LEVEL (Low / Mid / High)
# ============================================================
print("\n" + "=" * 65)
print("SECTION 4: USER CLASSIFICATION -- Cc:AF,u:AF MEASURE")
print("(Best-performing measure according to the paper)")
print("=" * 65)

scores = results_df["Cc:AF,u:AF"].values
thresholds = [np.percentile(scores, 33), np.percentile(scores, 66)]

def classify(v):
    """
    v : float - Cc:AF,u:AF score for a single user
    Assigns Low / Mid / High label based on 33rd and 66th percentile thresholds.
    """
    if v <= thresholds[0]: return "Low"
    elif v <= thresholds[1]: return "Mid"
    else: return "High"

results_df["Cc:AF,u:AF_level"] = results_df["Cc:AF,u:AF"].apply(classify)
level_df = results_df[["Country","Cc:AF,u:AF","Cc:AF,u:AF_level"]].copy()
level_df.columns = ["Country", "Cc:AF,u:AF Score", "Mainstreaminess Level"]
print(level_df.to_string())

print("\n" + "=" * 65)
print("SECTION 5: AF-ILF COUNTRY-SPECIFIC ARTIST PROFILES")
print("(Artists that differ from the global mainstream)")
print("=" * 65)

for c in countries:
    top_af    = AF_country[c].nlargest(3)
    top_afilf = AF_ILF_country_global[c].nlargest(3)
    print(f"\n{c} - Top 3 AF  (globally dominant):  {', '.join([f'{a}({v:.0f})' for a,v in top_af.items()])}")
    print(f"{c} - Top 3 AF-ILF (country-specific): {', '.join([f'{a}({v:.2f})' for a,v in top_afilf.items()])}")

print("\n✓ All computations completed.")