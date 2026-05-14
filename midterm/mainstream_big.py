import numpy as np
import pandas as pd
from scipy.stats import kendalltau
import warnings
import os
warnings.filterwarnings('ignore')

# ============================================================
# LOAD DATASET FROM EXCEL
# ============================================================
DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_large.xlsx")

raw = pd.read_excel(DATASET_PATH, sheet_name="Playcounts", header=2)
raw = raw.rename(columns={"User ID": "user_id", "Country\nCode": "country_code", "Country Name": "country_name"})
raw = raw.set_index("user_id")

artist_cols = [c for c in raw.columns if c not in ["country_code", "country_name"]]
df = raw[["country_code"] + artist_cols].rename(columns={"country_code": "country"}).copy()

# Artist list from Artists sheet
artists_meta = pd.read_excel(DATASET_PATH, sheet_name="Artists", header=1)
artists = artists_meta["Artist"].tolist()

print("=" * 70)
print(f"DATASET: {len(df)} users  |  {len(artist_cols)} artists  |  {df['country'].nunique()} countries")
print("=" * 70)
print(df.groupby("country").size().rename("users").to_frame().T.to_string())
print()

# ============================================================
# BASIC DEFINITIONS
# ============================================================
countries = df["country"].unique()
N_total   = len(df)

def compute_AF(user_set):
    """Returns AF (total playcount) per artist for the given user set."""
    return df.loc[user_set, artist_cols].sum()

def compute_LF(user_set):
    """Returns LF (unique listener count) per artist for the given user set."""
    return (df.loc[user_set, artist_cols] > 0).sum()

all_users     = df.index.tolist()
AF_global     = compute_AF(all_users)
LF_global     = compute_LF(all_users)

country_users = {c: df[df["country"] == c].index.tolist() for c in countries}
AF_country    = {c: compute_AF(country_users[c]) for c in countries}
LF_country    = {c: compute_LF(country_users[c]) for c in countries}

# ============================================================
# AF-ILF (Paper Equation 1)
# ============================================================
def compute_AF_ILF(af_u1, lf_u2, n_u2):
    """
    af_u1 : Series  - AF values for U1
    lf_u2 : Series  - LF values for U2
    n_u2  : int     - |U2|
    """
    ilf = np.log(1 + n_u2 / lf_u2.replace(0, np.nan)).fillna(0)
    return np.log(1 + af_u1) * ilf

AF_ILF_country_global = {
    c: compute_AF_ILF(AF_country[c], LF_global, N_total) for c in countries
}

# ── Section 1: Top artists per country ──────────────────────────────────────
print("=" * 70)
print("SECTION 1: TOP 5 ARTISTS PER COUNTRY  (AF  vs  AF-ILF)")
print("=" * 70)
for c in sorted(countries):
    top_af    = AF_country[c].nlargest(5)
    top_afilf = AF_ILF_country_global[c].nlargest(5)
    print(f"\n  {c}  AF    : {', '.join([f'{a}({v:,.0f})' for a,v in top_af.items()])}")
    print(f"  {c}  AF-ILF: {', '.join([f'{a}({v:.2f})' for a,v in top_afilf.items()])}")

# ============================================================
# 11 MAINSTREAMINESS MEASURES
# ============================================================
def normalize(series):
    """series: Pandas Series — returns sum-to-unity normalised version."""
    s = series.sum()
    return series / s if s > 0 else series

def fraction_measure(af_user, af_pop):
    """
    F = 1 - (1/|A|) * sum(|af_u - af_p| / max(af_u, af_p))
    af_user : Series - user playcount profile
    af_pop  : Series - reference population profile
    """
    af_u  = normalize(af_user)
    af_p  = normalize(af_pop)
    denom = pd.concat([af_u, af_p], axis=1).max(axis=1).replace(0, np.nan)
    return 1 - (af_u - af_p).abs().div(denom).fillna(0).mean()

def kl_divergence_sym(p, q, epsilon=1e-10):
    """
    Symmetrized KL divergence (inverted: higher = more mainstream)
    p       : Series - user profile
    q       : Series - reference population profile
    epsilon : float  - prevents log(0), default 1e-10
    """
    p = normalize(p) + epsilon
    q = normalize(q) + epsilon
    return 1 / (1 + ((p * np.log(p/q)).sum() + (q * np.log(q/p)).sum()) / 2)

def kendall_tau_measure(af_user, af_pop):
    """
    Kendall tau rank correlation (C family)
    af_user : Series - user playcount profile
    af_pop  : Series - reference population profile
    """
    tau, _ = kendalltau(af_user.rank(ascending=False), af_pop.rank(ascending=False))
    return tau

# ── Compute all 11 measures ──────────────────────────────────────────────────
print("\n" + "=" * 70)
print("SECTION 2: COMPUTING 11 MEASURES FOR ALL 500 USERS...")
print("=" * 70)

results = []
for uid in df.index:
    uc            = df.loc[uid, "country"]
    af_user       = df.loc[uid, artist_cols].astype(float)
    af_c          = AF_country[uc].astype(float)
    af_g          = AF_global.astype(float)
    lf_c          = LF_country[uc]
    n_c           = len(country_users[uc])
    af_ilf_user_c = compute_AF_ILF(af_user, lf_c, n_c)
    af_ilf_c_g    = AF_ILF_country_global[uc]

    results.append({
        "User": uid, "Country": uc,
        "Fg:AF,u:AF":          round(fraction_measure(af_user,       af_g),        4),
        "Fg:AF,u:AF·ILF":      round(fraction_measure(af_ilf_user_c, af_g),        4),
        "Fg:AF·ILF,u:AF·ILF":  round(fraction_measure(af_ilf_user_c, af_ilf_c_g), 4),
        "Fc:AF,u:AF":          round(fraction_measure(af_user,       af_c),        4),
        "Fc:AF·ILF,u:AF·ILF":  round(fraction_measure(af_ilf_user_c, af_ilf_c_g), 4),
        "Dg:AF,u:AF":          round(kl_divergence_sym(af_user,       af_g),       4),
        "Dc:AF,u:AF":          round(kl_divergence_sym(af_user,       af_c),       4),
        "Dc:AF·ILF,u:AF·ILF":  round(kl_divergence_sym(af_ilf_user_c,af_ilf_c_g),4),
        "Cg:AF,u:AF":          round(kendall_tau_measure(af_user,      af_g),      4),
        "Cc:AF,u:AF":          round(kendall_tau_measure(af_user,      af_c),      4),
        "Cc:AF·ILF,u:AF·ILF":  round(kendall_tau_measure(af_ilf_user_c,af_ilf_c_g),4),
    })

results_df = pd.DataFrame(results).set_index("User")
print(f"Done — {len(results_df)} users computed.")

# ── Section 3: Country-level averages ────────────────────────────────────────
measure_cols = [c for c in results_df.columns if c != "Country"]
country_avg  = results_df.groupby("Country")[measure_cols].mean().round(4)

print("\n" + "=" * 70)
print("SECTION 3: COUNTRY-LEVEL AVERAGE MAINSTREAMINESS SCORES")
print("=" * 70)
# Print key measures for readability
key = ["Fg:AF,u:AF","Fc:AF,u:AF","Dg:AF,u:AF","Dc:AF,u:AF","Cg:AF,u:AF","Cc:AF,u:AF"]
print(country_avg[key].sort_values("Cg:AF,u:AF", ascending=False).to_string())

# ── Section 4: Low / Mid / High classification ───────────────────────────────
scores     = results_df["Cc:AF,u:AF"].values
thresholds = [np.percentile(scores, 33), np.percentile(scores, 66)]

def classify(v):
    """v: float — Cc:AF,u:AF score for one user."""
    if v <= thresholds[0]: return "Low"
    elif v <= thresholds[1]: return "Mid"
    return "High"

results_df["Level"] = results_df["Cc:AF,u:AF"].apply(classify)

print("\n" + "=" * 70)
print("SECTION 4: MAINSTREAMINESS LEVEL DISTRIBUTION BY COUNTRY")
print("=" * 70)
dist = results_df.groupby(["Country","Level"]).size().unstack(fill_value=0)
for col in ["Low","Mid","High"]:
    if col not in dist.columns:
        dist[col] = 0
dist = dist[["Low","Mid","High"]]
dist["Total"] = dist.sum(axis=1)
print(dist.sort_values("Total", ascending=False).to_string())

print("\n" + "=" * 70)
print("SECTION 5: GLOBAL vs LOCAL MAINSTREAMINESS COMPARISON")
print("(Countries ranked by Cg:AF — how close to GLOBAL mainstream)")
print("=" * 70)
ranking = country_avg["Cg:AF,u:AF"].sort_values(ascending=False)
for rank, (country, score) in enumerate(ranking.items(), 1):
    bar = "█" * int(score * 30)
    print(f"  {rank:2d}. {country}  {score:+.4f}  {bar}")

print("\n✓ All computations completed.")