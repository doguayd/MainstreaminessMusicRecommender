# An Analysis of Global and Regional Mainstreaminess for Personalized Music Recommender Systems
### Schedl & Bauer (2018) — Study Review & Python Implementation
**Recommender Systems (COME424/1) — Üsküdar University, 2026**

**Group Members:**
| Name | Student ID |
|---|---|
| Doğukan Aydın | 240200019 |
| Elif Dalmış | 230201082 |
| Yaman Balcı | 220201081 |
| Salih Çetin | 220201060 |
| Alperen Keskin | 230201094 |

---

## Files Included

| File | Description |
|---|---|
| `Mainstream_final.py` | Main Python script — all analysis, recommendations, and figures |
| `dataset_lfm.xlsx` | Real Last.fm 360K derived dataset (489 users × 81 artists × 12 countries) |
| `requirements.txt` | Python dependency list |
| `fig1_af_vs_afilf.png` | Figure 1: AF vs AF-ILF top-5 artists per country |
| `fig2_country_heatmap.png` | Figure 2: Country mainstreaminess heatmap |
| `fig3_level_distribution.png` | Figure 3: Low/Mid/High level distribution by country |
| `fig4_global_ranking.png` | Figure 4: Global mainstreaminess ranking |
| `fig5_method_comparison.png` | Figure 5: Novelty & Personalization comparison |
| `Report_1.docx` | Full academic report |
| `Report_2.docx` | One-page midterm vs final summary |
| `Report_3.docx` | Line-by-line code explanation |

---

## Requirements

- Python 3.9 or higher
- Required packages listed in `requirements.txt`

---

## Installation

### Step 1 — Verify Python is installed

```bash
python --version
```

If Python is not installed, download it from https://www.python.org/downloads/

### Step 2 — (Optional) Create a virtual environment

```bash
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **macOS / Linux:** `source venv/bin/activate`

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

This installs: `numpy`, `pandas`, `scipy`, `scikit-learn`, `openpyxl`, `matplotlib`

---

## Running the Code

Make sure `dataset_lfm.xlsx` is in the **same folder** as `Mainstream_final.py`, then run:

```bash
python Mainstream_final.py
```

### Expected console output (in order):

| Section | Description |
|---|---|
| Dataset summary | User/artist/country counts |
| Section 1 | Top-5 artists per country: AF vs AF-ILF |
| Section 2 | 11 mainstreaminess measures computed for all users |
| Section 3 | Country-level average mainstreaminess scores |
| Section 4 | Low/Mid/High level distribution per country |
| Section 5 | Global mainstreaminess country ranking |
| Method 1 | Popularity Baseline — novelty score |
| Method 2 | User-KNN (k=10) — novelty score |
| Method 3 | SVD (20 factors) — RMSE + novelty score |
| Comparison | Novelty & Personalization table for all 4 methods |
| Figures | 5 PNG files saved to the same directory |

### Expected figures generated:

```
fig1_af_vs_afilf.png
fig2_country_heatmap.png
fig3_level_distribution.png
fig4_global_ranking.png
fig5_method_comparison.png
```

All figures are saved automatically in the same folder as the script. No display window is required (non-interactive backend).

---

## Approximate Runtime

| Hardware | Estimated time |
|---|---|
| Modern laptop (2020+) | ~15–30 seconds |
| Older hardware | ~60 seconds |

The SVD decomposition and KNN evaluation over 50 users are the most time-intensive steps.

---

## Dataset

`dataset_lfm.xlsx` contains two sheets:

| Sheet | Description |
|---|---|
| `Playcounts` | User-artist playcount matrix (489 users × 81 artists), with country code per user |
| `Artists` | Artist metadata (name, genre tags) |

The data was derived from the publicly available **Last.fm 360K dataset**
(Celma, 2010 — http://mtg.upf.edu/node/1489), filtered to 489 users across 12 countries.

---

## References

Schedl, M., & Bauer, C. (2018). An analysis of global and regional mainstreaminess for personalized music recommender systems. *Journal of Mobile Multimedia*, 14(1), 95–122.
