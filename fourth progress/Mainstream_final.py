import sys
import numpy as np
import pandas as pd
from scipy.stats import kendalltau
from scipy.sparse.linalg import svds
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import mean_squared_error
import warnings
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

warnings.filterwarnings('ignore')

# ============================================================
# LOAD DATASET FROM EXCEL
# ============================================================
# dataset_large.xlsx must be in the same directory as this script.
# Sheet "Playcounts" : user-artist playcount matrix
# Sheet "Artists"    : artist metadata

DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_large.xlsx")

raw = pd.read_excel(DATASET_PATH, sheet_name="Playcounts", header=2)
raw = raw.rename(columns={
    "User ID":       "user_id",
    "Country\nCode": "country_code",
    "Country Name":  "country_name"
})
raw = raw.set_index("user_id")

artist_cols = [c for c in raw.columns if c not in ["country_code", "country_name"]]
df = raw[["country_code"] + artist_cols].rename(columns={"country_code": "country"}).copy()

artists_meta = pd.read_excel(DATASET_PATH, sheet_name="Artists", header=1)

print("=" * 70)
print(f"DATASET: {len(df)} users  |  {len(artist_cols)} artists  |  {df['country'].nunique()} countries")
print("=" * 70)
print(df.groupby("country").size().rename("users").to_frame().T.to_string())
print()

# ============================================================
# BASIC DEFINITIONS
# ============================================================
countries  = df["country"].unique()
N_total    = len(df)

def compute_AF(user_set):
    """
    Returns AF (total playcount) per artist for the given user set.
    user_set : list of user ID strings
    """
    return df.loc[user_set, artist_cols].sum()

def compute_LF(user_set):
    """
    Returns LF (unique listener count) per artist for the given user set.
    user_set : list of user ID strings
    """
    return (df.loc[user_set, artist_cols] > 0).sum()

all_users     = df.index.tolist()
AF_global     = compute_AF(all_users)
LF_global     = compute_LF(all_users)

country_users = {c: df[df["country"] == c].index.tolist() for c in countries}
AF_country    = {c: compute_AF(country_users[c]) for c in countries}
LF_country    = {c: compute_LF(country_users[c]) for c in countries}

# ============================================================
# AF-ILF  (Paper Equation 1)
# AF·ILF(a, U1, U2) = log(1 + AF_{a,U1}) * log(1 + |U2| / LF_{a,U2})
# ============================================================
def compute_AF_ILF(af_u1, lf_u2, n_u2):
    """
    af_u1 : Series  - AF values for population U1
    lf_u2 : Series  - LF values for population U2
    n_u2  : int     - size of U2 (|U2|)
    """
    ilf = np.log(1 + n_u2 / lf_u2.replace(0, np.nan)).fillna(0)
    return np.log(1 + af_u1) * ilf

AF_ILF_country_global = {
    c: compute_AF_ILF(AF_country[c], LF_global, N_total) for c in countries
}
# Global AF·ILF profile: U1 = all users, U2 = all users
# Used as the population reference for Fg:AF·ILF,u:AF·ILF
AF_ILF_global = compute_AF_ILF(AF_global, LF_global, N_total)

# ── Section 1: Top artists per country (AF vs AF-ILF) ───────────────────
print("=" * 70)
print("SECTION 1: TOP 5 ARTISTS PER COUNTRY  (AF  vs  AF-ILF)")
print("=" * 70)
for c in sorted(countries):
    top_af    = AF_country[c].nlargest(5)
    top_afilf = AF_ILF_country_global[c].nlargest(5)
    print(f"\n  {c}  AF    : {', '.join([f'{a}({v:,.0f})' for a,v in top_af.items()])}")
    print(f"  {c}  AF-ILF: {', '.join([f'{a}({v:.2f})' for a,v in top_afilf.items()])}")

# ============================================================
# 11 MAINSTREAMINESS MEASURES  (Proposed Approach)
# ============================================================
def normalize(series):
    """
    series : Pandas Series of non-negative numeric values
    Returns the sum-to-unity normalised version (probability distribution).
    """
    s = series.sum()
    return series / s if s > 0 else series

def fraction_measure(af_user, af_pop):
    """
    Fraction-based mainstreaminess (F family, Table 5).
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
    Symmetrized KL divergence (D family, Table 5), inverted so higher = more mainstream.
    p       : Series - user profile
    q       : Series - reference population profile
    epsilon : float  - prevents log(0), default 1e-10
    """
    p = normalize(p) + epsilon
    q = normalize(q) + epsilon
    return 1 / (1 + ((p * np.log(p / q)).sum() + (q * np.log(q / p)).sum()) / 2)

def kendall_tau_measure(af_user, af_pop):
    """
    Kendall tau rank correlation (C family, Table 5).
    af_user : Series - user playcount profile
    af_pop  : Series - reference population profile
    """
    tau, _ = kendalltau(af_user.rank(ascending=False), af_pop.rank(ascending=False))
    return tau

# ── Compute all 11 measures ──────────────────────────────────────────────
print("\n" + "=" * 70)
print("SECTION 2: COMPUTING 11 MAINSTREAMINESS MEASURES — ALL USERS")
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
        "Fg:AF,u:AF":          round(fraction_measure(af_user,        af_g),        4),
        "Fg:AF,u:AF·ILF":      round(fraction_measure(af_ilf_user_c,  af_g),         4),
        "Fg:AF·ILF,u:AF·ILF":  round(fraction_measure(af_ilf_user_c,  AF_ILF_global), 4),
        "Fc:AF,u:AF":          round(fraction_measure(af_user,        af_c),        4),
        "Fc:AF·ILF,u:AF·ILF":  round(fraction_measure(af_ilf_user_c,  af_ilf_c_g), 4),
        "Dg:AF,u:AF":          round(kl_divergence_sym(af_user,        af_g),       4),
        "Dc:AF,u:AF":          round(kl_divergence_sym(af_user,        af_c),       4),
        "Dc:AF·ILF,u:AF·ILF":  round(kl_divergence_sym(af_ilf_user_c, af_ilf_c_g), 4),
        "Cg:AF,u:AF":          round(kendall_tau_measure(af_user,       af_g),      4),
        "Cc:AF,u:AF":          round(kendall_tau_measure(af_user,       af_c),      4),
        "Cc:AF·ILF,u:AF·ILF":  round(kendall_tau_measure(af_ilf_user_c, af_ilf_c_g), 4),
    })

results_df = pd.DataFrame(results).set_index("User")
print(f"Done — {len(results_df)} users computed.")

# ── Country averages ──────────────────────────────────────────────────────
measure_cols = [c for c in results_df.columns if c != "Country"]
country_avg  = results_df.groupby("Country")[measure_cols].mean().round(4)

print("\n" + "=" * 70)
print("SECTION 3: COUNTRY-LEVEL AVERAGE MAINSTREAMINESS")
print("=" * 70)
key = ["Fg:AF,u:AF", "Fc:AF,u:AF", "Dg:AF,u:AF", "Dc:AF,u:AF", "Cg:AF,u:AF", "Cc:AF,u:AF"]
print(country_avg[key].sort_values("Cg:AF,u:AF", ascending=False).to_string())

# ── Low / Mid / High classification ──────────────────────────────────────
scores     = results_df["Cc:AF,u:AF"].values
thresholds = [np.percentile(scores, 33), np.percentile(scores, 66)]

def classify(v):
    """
    v : float — Cc:AF,u:AF score for one user.
    Returns Low / Mid / High based on 33rd and 66th percentile thresholds.
    """
    if v <= thresholds[0]: return "Low"
    elif v <= thresholds[1]: return "Mid"
    return "High"

results_df["Level"] = results_df["Cc:AF,u:AF"].apply(classify)

print("\n" + "=" * 70)
print("SECTION 4: MAINSTREAMINESS LEVEL DISTRIBUTION BY COUNTRY")
print("=" * 70)
dist = results_df.groupby(["Country", "Level"]).size().unstack(fill_value=0)
for col in ["Low", "Mid", "High"]:
    if col not in dist.columns:
        dist[col] = 0
dist = dist[["Low", "Mid", "High"]]
dist["Total"] = dist.sum(axis=1)
print(dist.sort_values("Total", ascending=False).to_string())

print("\n" + "=" * 70)
print("SECTION 5: GLOBAL vs LOCAL MAINSTREAMINESS RANKING")
print("(Ranked by Cg:AF — closeness to global mainstream)")
print("=" * 70)
ranking = country_avg["Cg:AF,u:AF"].sort_values(ascending=False)
for rank, (country, score) in enumerate(ranking.items(), 1):
    bar = "█" * int(score * 30)
    print(f"  {rank:2d}. {country}  {score:+.4f}  {bar}")

# ============================================================
# PROPOSED RECOMMENDATION FUNCTION
# Maps mainstreaminess level → recommendation strategy
# ============================================================
def get_top_candidates(country_code, n=15):
    """
    Returns top-n artist candidates per recommendation strategy for a country.
    n is intentionally larger than the final recommendation count so that
    already-heard artists can be filtered out in recommend_mainstreaminess.
    country_code : str  - ISO country code
    n            : int  - candidate pool size (default 15)
    """
    global_top = AF_global.nlargest(n).index.tolist()
    local_top  = AF_ILF_country_global[country_code].nlargest(n).index.tolist()
    mixed      = list(dict.fromkeys(global_top + local_top))[:n]
    return {"global": global_top, "local": local_top, "mixed": mixed}

def recommend_mainstreaminess(user_id, n=5):
    """
    Recommends artists based on mainstreaminess level (proposed approach).
    High  → Global strategy  (globally popular artists)
    Low   → Local strategy   (country-specific mainstream)
    Mid   → Mixed strategy   (blend of global and local)
    Already-heard artists are excluded for fair comparison with KNN and SVD.

    user_id : str - user ID
    n       : int - number of recommendations
    """
    if user_id not in results_df.index:
        return {"error": f"User {user_id} not found."}
    level      = results_df.loc[user_id, "Level"]
    country    = results_df.loc[user_id, "Country"]
    strategy   = {"High": "global", "Low": "local", "Mid": "mixed"}[level]
    candidates = get_top_candidates(country, n=15)
    user_plays  = df.loc[user_id, artist_cols]
    # Filter out artists the user has already heard
    filtered = [a for a in candidates[strategy] if user_plays[a] == 0]
    # Fallback: if not enough unheard candidates, use full candidate list
    recs = filtered[:n] if len(filtered) >= n else candidates[strategy][:n]
    return {
        "user_id":         user_id,
        "country":         country,
        "level":           level,
        "strategy":        strategy,
        "Cc:AF,u:AF":      round(results_df.loc[user_id, "Cc:AF,u:AF"], 4),
        "recommendations": recs,
    }

# ============================================================
# EVALUATION SAMPLE — fixed for all four methods (fair comparison)
# ============================================================
EVAL_SAMPLE = df.index[:50].tolist()

# ============================================================
# METHOD 1 — POPULARITY-BASED BASELINE
# Recommends the globally most-played artists to every user,
# ignoring individual preferences and country context entirely.
# ============================================================
print("\n" + "=" * 70)
print("COMPARISON METHOD 1: POPULARITY-BASED BASELINE")
print("Recommends the same globally top-N artists to every user.")
print("=" * 70)

def recommend_popularity(user_id, n=5):
    """
    Popularity baseline: returns the top-n globally most-listened artists.
    No user history or country context is used.

    user_id : str - user ID (used only for output labelling)
    n       : int - number of recommendations
    """
    top_global = AF_global.nlargest(n).index.tolist()
    return {
        "user_id":         user_id,
        "method":          "Popularity Baseline",
        "recommendations": top_global,
    }

# Evaluate: what fraction of recommendations are already known to the user?
# (Higher = over-recommends already-heard artists = less useful)
popularity_already_heard = []
for uid in EVAL_SAMPLE:
    recs      = recommend_popularity(uid, n=5)["recommendations"]
    user_row  = df.loc[uid, artist_cols]
    heard     = sum(1 for a in recs if a in artist_cols and user_row[a] > 0)
    popularity_already_heard.append(heard / 5)

pop_novelty = 1 - np.mean(popularity_already_heard)

print(f"  Top-5 global artists: {AF_global.nlargest(5).index.tolist()}")
print(f"  Average fraction of recs already heard by user : {np.mean(popularity_already_heard):.3f}")
print(f"  Novelty score (lower already-heard = better)   : {pop_novelty:.3f}")

# ============================================================
# METHOD 2 — USER-BASED KNN COLLABORATIVE FILTERING
# Finds the K most similar users based on playcount cosine similarity,
# then recommends artists they listened to that the target user has not.
# ============================================================
print("\n" + "=" * 70)
print("COMPARISON METHOD 2: USER-BASED KNN COLLABORATIVE FILTERING")
print("Finds K nearest neighbours by cosine similarity, recommends their top artists.")
print("=" * 70)

# Build the user-artist matrix (rows=users, cols=artists)
playcount_matrix = df[artist_cols].values.astype(float)

# Normalise each user row to unit length for cosine similarity
norms = np.linalg.norm(playcount_matrix, axis=1, keepdims=True)
norms[norms == 0] = 1
playcount_norm = playcount_matrix / norms

K = 10  # number of neighbours
knn_model = NearestNeighbors(n_neighbors=K + 1, metric="cosine", algorithm="brute")
knn_model.fit(playcount_norm)

user_index = {uid: i for i, uid in enumerate(df.index)}

def recommend_knn(user_id, n=5, k=K):
    """
    KNN collaborative filtering recommendation.
    Finds k nearest neighbours, aggregates their playcounts
    (excluding artists already heard by the target user),
    and returns the top-n unheard artists.

    user_id : str - target user ID
    n       : int - number of recommendations
    k       : int - number of nearest neighbours (default K=10)
    """
    idx        = user_index[user_id]
    user_vec   = playcount_norm[idx].reshape(1, -1)
    distances, indices = knn_model.kneighbors(user_vec)
    # Skip the first result (the user itself, distance ≈ 0)
    neighbour_indices = indices[0][1:]
    neighbour_scores  = distances[0][1:]

    # Weight neighbour playcounts by similarity (1 - cosine distance)
    weights         = (1 - neighbour_scores)
    neighbour_plays = playcount_matrix[neighbour_indices]
    aggregated      = (neighbour_plays * weights[:, None]).sum(axis=0)

    # Mask artists already heard by the target user
    already_heard_mask = playcount_matrix[idx] > 0
    aggregated[already_heard_mask] = -1

    top_indices = np.argsort(aggregated)[::-1][:n]
    return {
        "user_id":         user_id,
        "method":          "User-KNN (k={})".format(k),
        "recommendations": [artist_cols[i] for i in top_indices],
    }

knn_already_heard = []
for uid in EVAL_SAMPLE:
    recs  = recommend_knn(uid, n=5)["recommendations"]
    heard = sum(1 for a in recs if df.loc[uid, a] > 0)
    knn_already_heard.append(heard / 5)

knn_novelty = 1 - np.mean(knn_already_heard)

# Show 3 example recommendations
print(f"  K = {K} neighbours, cosine similarity")
for uid in df.index[:3]:
    rec = recommend_knn(uid, n=5)
    country = df.loc[uid, "country"]
    print(f"  {uid} ({country}): {rec['recommendations']}")
print(f"  Novelty score (sample of 50 users): {knn_novelty:.3f}")

# ============================================================
# METHOD 3 — SVD MATRIX FACTORIZATION
# Decomposes the user-artist playcount matrix into latent factors.
# Predicted scores are used to recommend unheard artists.
# ============================================================
print("\n" + "=" * 70)
print("COMPARISON METHOD 3: SVD MATRIX FACTORIZATION")
print("Decomposes the playcount matrix into latent user/artist factors.")
print("=" * 70)

N_FACTORS = 20   # number of latent dimensions
TRAIN_RATIO = 0.8

# Log-scale the matrix to reduce outlier dominance (as in paper)
log_matrix = np.log1p(playcount_matrix)

# Centre the matrix (subtract per-user mean) before SVD
user_means    = log_matrix.mean(axis=1, keepdims=True)
centred_matrix = log_matrix - user_means

# Truncated SVD
U, sigma, Vt = svds(centred_matrix, k=N_FACTORS)
# Sort by descending singular value
idx_sorted = np.argsort(sigma)[::-1]
U     = U[:, idx_sorted]
sigma = sigma[idx_sorted]
Vt    = Vt[idx_sorted, :]

# Reconstruct predicted ratings
predicted = U @ np.diag(sigma) @ Vt + user_means

def recommend_svd(user_id, n=5):
    """
    SVD-based recommendation: uses reconstructed latent-factor scores
    to rank unheard artists and return the top-n.

    user_id : str - target user ID
    n       : int - number of recommendations
    """
    idx         = user_index[user_id]
    user_pred   = predicted[idx]
    # Mask already-heard artists
    already_mask = playcount_matrix[idx] > 0
    user_pred_masked = user_pred.copy()
    user_pred_masked[already_mask] = -np.inf
    top_indices = np.argsort(user_pred_masked)[::-1][:n]
    return {
        "user_id":         user_id,
        "method":          f"SVD ({N_FACTORS} factors)",
        "recommendations": [artist_cols[i] for i in top_indices],
    }

# Evaluate RMSE on a held-out test split (20% of non-zero entries)
nonzero_rows, nonzero_cols = np.where(playcount_matrix > 0)
test_size    = int(len(nonzero_rows) * (1 - TRAIN_RATIO))
test_indices = np.random.choice(len(nonzero_rows), test_size, replace=False)

actual_vals    = log_matrix[nonzero_rows[test_indices], nonzero_cols[test_indices]]
predicted_vals = predicted[nonzero_rows[test_indices], nonzero_cols[test_indices]]
svd_rmse       = np.sqrt(mean_squared_error(actual_vals, predicted_vals))

svd_already_heard = []
for uid in EVAL_SAMPLE:
    recs  = recommend_svd(uid, n=5)["recommendations"]
    heard = sum(1 for a in recs if df.loc[uid, a] > 0)
    svd_already_heard.append(heard / 5)

svd_novelty = 1 - np.mean(svd_already_heard)

print(f"  Latent factors: {N_FACTORS}")
print(f"  RMSE on held-out 20% entries (log-scale): {svd_rmse:.4f}")
print(f"  Novelty score (sample of 50 users): {svd_novelty:.3f}")
for uid in df.index[:3]:
    rec     = recommend_svd(uid, n=5)
    country = df.loc[uid, "country"]
    print(f"  {uid} ({country}): {rec['recommendations']}")

# ============================================================
# COMPARISON SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("COMPARISON SUMMARY: ALL FOUR METHODS (sample of 50 users)")
print("=" * 70)

# Mainstreaminess-based novelty
ms_already_heard = []
for uid in EVAL_SAMPLE:
    recs  = recommend_mainstreaminess(uid, n=5)["recommendations"]
    heard = sum(1 for a in recs if df.loc[uid, a] > 0)
    ms_already_heard.append(heard / 5)
ms_novelty = 1 - np.mean(ms_already_heard)

# Personalization: how different are two random users' recommendation lists?
def personalization_score(rec_func, sample_users, n=5):
    """
    Measures diversity across users.
    Higher = recommendations differ more between users (more personalized).
    rec_func     : function(user_id, n) → dict with 'recommendations' key
    sample_users : list of user IDs
    n            : number of recommendations
    """
    rec_sets = []
    for uid in sample_users:
        try:
            recs = rec_func(uid, n=n)["recommendations"]
            rec_sets.append(set(recs))
        except Exception:
            continue
    if len(rec_sets) < 2:
        return 0.0
    diffs = []
    for i in range(len(rec_sets)):
        for j in range(i + 1, len(rec_sets)):
            union = len(rec_sets[i] | rec_sets[j])
            inter = len(rec_sets[i] & rec_sets[j])
            diffs.append(1 - inter / union if union > 0 else 0)
    return np.mean(diffs)

pop_personalization = personalization_score(
    lambda uid, n: recommend_popularity(uid, n), EVAL_SAMPLE)
knn_personalization = personalization_score(
    lambda uid, n: recommend_knn(uid, n), EVAL_SAMPLE)
svd_personalization = personalization_score(
    lambda uid, n: recommend_svd(uid, n), EVAL_SAMPLE)
ms_personalization  = personalization_score(
    lambda uid, n: recommend_mainstreaminess(uid, n), EVAL_SAMPLE)

print(f"\n{'Method':<35} {'Novelty':>9} {'Personalization':>17}")
print("-" * 63)
print(f"{'Popularity Baseline':<35} {pop_novelty:>9.3f} {pop_personalization:>17.3f}")
print(f"{'User-KNN (k=10)':<35} {knn_novelty:>9.3f} {knn_personalization:>17.3f}")
print(f"{'SVD (20 factors)':<35} {svd_novelty:>9.3f} {svd_personalization:>17.3f}")
print(f"{'Proposed (Mainstreaminess-AF-ILF)':<35} {ms_novelty:>9.3f} {ms_personalization:>17.3f}")

print("\nMetric definitions:")
print("  Novelty        : fraction of recs the user has NOT heard before (higher = better)")
print("  Personalization: how different two users' rec lists are (higher = more personalised)")

print("\n✓ All computations completed.")