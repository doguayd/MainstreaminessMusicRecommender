# Mainstreaminess-Based Music Recommender System

> **Course:** COME424/1 — Recommender Systems  
> **University:** Üsküdar University, Department of Computer Engineering  
> **Semester:** Spring 2025–2026  
> **Reference Paper:** Schedl & Bauer (2018) — *An Analysis of Global and Regional Mainstreaminess for Personalized Music Recommender Systems*

---

## Team

| Name | Student ID |
|---|---|
| Doğukan Aydın | 240200019 |
| Elif Dalmış | 230201082 |
| Yaman Balcı | 220201081 |
| Salih Çetin | 220201060 |
| Alperen Keskin | 230201094 |

---

## Project Overview

This project implements and extends the **mainstreaminess framework** proposed by Schedl & Bauer (2018) for personalized music recommendation. The system measures how "mainstream" a user's listening behaviour is — relative to global and country-level listening patterns — and uses that signal to personalise recommendations.

### What is Mainstreaminess?

Mainstreaminess quantifies the overlap between a user's listening profile and the broader listening population. High-mainstreaminess users prefer globally popular artists; low-mainstreaminess users have niche/local tastes.

### Key Measures Implemented (11 total)

| Family | Measures | Description |
|---|---|---|
| **Fraction (F)** | `Fg:AF,u:AF`, `Fc:AF,u:AF`, `Fg:AF·ILF,u:AF·ILF`, `Fc:LF,u:LF`, `Fc:AF·ILF,u:AF·ILF` | Overlap between user and population listening profiles |
| **KL Divergence (D)** | `Dg:AF,u:AF`, `Dc:AF,u:AF`, `Dc:LF,u:LF` | Distribution divergence between user and population |
| **Kendall's τ (C)** | `Cg:AF,u:AF`, `Cc:AF,u:AF`, `Cc:LF,u:LF` | Rank correlation between user and population |

`Cc:AF,u:AF` is used as the primary measure for classifying users into Low / Mid / High mainstreaminess tiers (33rd / 66th percentile thresholds).

### Recommendation Strategies

Based on mainstreaminess tier, users receive different recommendation strategies:
- **High** → Global top artists (`AF_global`)
- **Low** → Country-specific niche artists (`AF·ILF_country`)
- **Mid** → Mixed (global + local blend)

### Comparison Methods

The proposed approach is evaluated against three baselines:

| Method | Description |
|---|---|
| **Popularity Baseline** | Recommends the globally most-played artists to every user |
| **User-KNN (k=10)** | Cosine-similarity nearest-neighbour collaborative filtering |
| **SVD (20 factors)** | Matrix factorisation via truncated SVD (`scipy.sparse.linalg.svds`) |

### Evaluation Metrics

| Metric | Definition |
|---|---|
| **Novelty** | Fraction of recommended artists the user has NOT previously heard |
| **Personalization** | Average Jaccard distance between pairs of users' recommendation lists |

---

## Repository Structure

```
recommender-systems-mainstreaminess/
│
├── README.md                    ← this file
├── error_log.md                 ← full log of all bugs encountered (ERR-001 – ERR-022)
├── lastfm_to_excel.py           ← script to convert Last.fm 360K TSV → Excel
├── hoca_gereksinimleri.md       ← course requirements & grading notes
│
├── An_Analysis_of_...pdf        ← reference paper (Schedl & Bauer 2018)
│
├── first-progress/              ← Initial implementation (March 2026)
│   ├── User-recommender.py      ← first draft with hardcoded data
│   └── recom.py                 ← improved version with basic metrics
│
├── midterm/                     ← Midterm submission (April 2026)
│   ├── mainstream_big.py        ← Excel-based implementation, 11 measures
│   ├── dataset_large.xlsx       ← synthetic dataset (500 users × 81 artists)
│   ├── midterm_report.pdf       ← submitted report
│   └── midterm_report.docx      ← editable version
│
├── Second Progress/             ← Second progress (April 2026)
│   ├── mainstream_big.py        ← path-fix update
│   ├── dataset_large.xlsx       ← same synthetic dataset
│   └── second_progress_report.docx
│
├── Third Progress/              ← Third progress (April–May 2026)
│   └── presentation.pptx        ← progress presentation
│
└── fourth progress/             ← Fourth (final) progress (May 2026) ← MAIN
    ├── Mainstream_final.py      ← complete implementation (515 lines)
    ├── dataset_large.xlsx       ← synthetic dataset (500 users × 81 artists × 12 countries)
    ├── dataset_lfm.xlsx         ← real Last.fm 360K data (489 users × 81 artists × 12 countries)
    ├── progress_report_4_v2.docx← fourth progress report
    └── requirements.txt         ← Python dependencies
```

---

## Datasets

### Synthetic Dataset (`dataset_large.xlsx`)
- **Source:** AI-generated (documented in report)
- **Size:** 500 users × 81 artists × 12 countries
- **Countries:** TR, US, DE, GB, FR, PL, BR, FI, SE, RU, JP, KR
- **Format:** Multi-sheet Excel (Playcounts / Artists / Users / Countries)

### Real-World Dataset (`dataset_lfm.xlsx`)
- **Source:** Last.fm 360K dataset (Celma 2010), filtered and sampled
- **Size:** 489 users × 81 artists × 12 countries
- **Construction:** Top 81 artists (≥5 listeners), proportional country sampling, converted via `lastfm_to_excel.py`
- **Note:** The original Last.fm 360K raw files (~2 GB) are excluded from this repository; see `lastfm_to_excel.py` for reproducible construction

> **AI-assisted expansion:** The synthetic dataset was generated with AI assistance to supplement the real dataset. This is documented in the report as required by course guidelines.

---

## Results (Fourth Progress, 50-user sample)

| Method | Novelty | Personalization |
|---|---|---|
| Popularity Baseline | 0.000 | 0.000 |
| User-KNN (k=10) | 1.000 | 0.905 |
| SVD (20 factors) | 1.000 | 0.933 |
| **Proposed (Mainstreaminess-AF·ILF)** | **0.100** | **0.189** |

The proposed method scores lower novelty than KNN/SVD by design: for high-mainstreaminess users it recommends globally popular artists, which users are more likely to know. Country-specific and mixed strategies (for low/mid users) increase diversity.

---

## Setup & Usage

```bash
# 1. Install dependencies
pip install -r "fourth progress/requirements.txt"

# 2. Run the main system (uses dataset_large.xlsx by default)
cd "fourth progress"
python Mainstream_final.py
```

To use the real Last.fm dataset, change line 23 of `Mainstream_final.py`:
```python
DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_lfm.xlsx")
```

---

## Dependencies

```
pandas>=1.5
openpyxl>=3.0
numpy<2.0.0
scipy>=1.9
scikit-learn>=1.1
```

---

## Error Log

All bugs, warnings, and issues encountered during development are documented in [`error_log.md`](error_log.md) with:
- Date / time of occurrence
- File name and line number
- Full error message
- Root cause analysis
- Fix applied
- Lesson learned

**22 errors recorded** across 3 development sessions (ERR-001 through ERR-022).

---

## Reference

Schedl, M., & Bauer, C. (2018). *An Analysis of Global and Regional Mainstreaminess for Personalized Music Recommender Systems*. Transactions of the International Society for Music Information Retrieval (TISMIR), 1(1), 52–69.
