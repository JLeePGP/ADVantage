"""
ADVantage Data Engine -- math_processor.py (JSON-Pure Architecture)
==================================================================
Precision Growth Partners | Agentic ABM Infrastructure

Ingests 5 years of SEC Form ADV Part 1A bulk CSVs, qualifies firms against
ICP hard filters on the latest year, computes 5-year longitudinal metrics,
scores each firm across 20 behavioral signals, and outputs two distinct
JSON layers:
  1. prospects_top100.json   -- fast interface prioritization cache
  2. financial_profiles.json -- universal registry for wildcard agent lookups

Run from project root:
    python engine/math_processor.py
"""

import json
import math
import os
import pandas as pd

# -- PATH CONFIGURATION ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

YEAR_FILES = {
    2022: os.path.join(BASE_DIR, "raw_sec_adv_files", "220601.csv"),
    2023: os.path.join(BASE_DIR, "raw_sec_adv_files", "230602.csv"),
    2024: os.path.join(BASE_DIR, "raw_sec_adv_files", "240605.csv"),
    2025: os.path.join(BASE_DIR, "raw_sec_adv_files", "250602.csv"),
    2026: os.path.join(BASE_DIR, "raw_sec_adv_files", "260601.CSV"),
}

LATEST_YEAR   = 2026
SORTED_YEARS  = sorted(YEAR_FILES.keys())

# Unified JSON output coordinates
OUTPUT_TOP100_JSON = os.path.join(BASE_DIR, "data", "output", "prospects_top100.json")
OUTPUT_MASTER_JSON = os.path.join(BASE_DIR, "data", "output", "financial_profiles.json")

# -- ICP SCALE FILTERS (applied to LATEST_YEAR snapshot only) ------------------
MIN_AUM       = 150_000_000    # $150M floor
MAX_AUM       = 5_000_000_000  # $5B ceiling
MAX_EMPLOYEES = 200

# -- FORM ADV COLUMN GROUPS -----------------------------------------------------
CLIENT_COUNT_COLS = [
    "5D(a)(1)", "5D(b)(1)", "5D(c)(1)", "5D(d)(1)", "5D(e)(1)",
    "5D(f)(1)", "5D(g)(1)", "5D(h)(1)", "5D(i)(1)", "5D(j)(1)",
    "5D(k)(1)", "5D(l)(1)", "5D(m)(1)",
]

MARKETING_COLS = [
    "5L(1)(a)", "5L(1)(b)", "5L(1)(c)", "5L(1)(d)", "5L(1)(e)",
    "5L(2)", "5L(3)", "5L(4)",
]

DISC_COLS_TO_TRACK = [
    "11A(1)", "11A(2)", "11B(1)", "11B(2)", "11C(1)", "11C(2)",
    "11C(3)", "11C(4)", "11C(5)", "11D(1)", "11D(2)", "11D(3)",
]

# -- HELPERS --------------------------------------------------------------------
def safe_float(val):
    try:
        result = float(str(val).replace(",", "").strip())
        return result if not math.isnan(result) else 0.0
    except (ValueError, TypeError):
        return 0.0

def safe_int(val):
    try:
        return int(float(str(val).replace(",", "").strip()))
    except (ValueError, TypeError):
        return 0

def safe_div(numerator, denominator, default=0.0):
    return numerator / denominator if denominator else default

def compute_cagr(start_val, end_val, years):
    if start_val <= 0 or end_val <= 0 or years <= 0:
        return None
    return (end_val / start_val) ** (1.0 / years) - 1.0

# -- PHASE 1: LONGITUDINAL INGESTION -------------------------------------------
def _load_csv(year, path):
    if not os.path.exists(path):
        print(f"  WARNING: '{os.path.basename(path)}' not found. Skipping {year}.")
        return None
    print(f"  Reading {os.path.basename(path)}  ({year})...")
    df = pd.read_csv(path, dtype=str, encoding="latin-1", low_memory=False)
    print(f"    {len(df):,} total rows loaded.")
    return df

def _apply_qualification_filters(df):
    n0 = len(df)
    df = df[df["5E(1)"].str.strip().str.upper() == "Y"].copy()
    df = df[df["5E(5)"].str.strip().str.upper() == "N"].copy()
    df = df[df["5F(1)"].str.strip().str.upper() == "Y"].copy()

    df["_disc"]      = df["5F(2)(a)"].apply(safe_float)
    df["_ndisc"]     = df["5F(2)(b)"].apply(safe_float)
    df["_total_aum"] = df["_disc"] + df["_ndisc"]
    df = df[(df["_total_aum"] >= MIN_AUM) & (df["_total_aum"] <= MAX_AUM)].copy()

    df["_emp_count"] = df["5A"].apply(safe_int)
    df = df[df["_emp_count"] <= MAX_EMPLOYEES].copy()

    print(f"    {len(df):,} firms passed all qualification filters.")
    return df

def _extract_metrics(row, df_columns):
    disc_aum     = safe_float(row.get("5F(2)(a)", 0))
    ndisc_aum    = safe_float(row.get("5F(2)(b)", 0))
    total_aum    = safe_float(row.get("5F(2)(c)", 0))
    if total_aum == 0:
        total_aum = disc_aum + ndisc_aum

    disc_accounts  = safe_int(row.get("5F(2)(d)", 0))
    ndisc_accounts = safe_int(row.get("5F(2)(e)", 0))
    total_accounts = disc_accounts + ndisc_accounts

    total_clients = sum(safe_int(row.get(c, 0)) for c in CLIENT_COUNT_COLS if c in df_columns)
    has_disclosure = any(str(row.get(c, "")).strip().upper() == "Y" for c in DISC_COLS_TO_TRACK if c in df_columns)

    if any(c in df_columns for c in MARKETING_COLS):
        has_marketing = any(str(row.get(c, "")).strip().upper() == "Y" for c in MARKETING_COLS if c in df_columns)
    else:
        has_marketing = None

    hnw_aum       = safe_float(row.get("5D(b)(3)", 0))
    hnw_count    = safe_int(row.get("5D(b)(1)", 0))
    non_hnw_aum  = safe_float(row.get("5D(a)(3)", 0))
    non_hnw_count = safe_int(row.get("5D(a)(1)", 0))
    team_size    = safe_int(row.get("5A", 0))
    advisor_count = safe_int(row.get("5B(1)", 0))

    disc_pct_aum         = round(safe_div(disc_aum, total_aum), 4)
    ndisc_pct_aum        = round(safe_div(ndisc_aum, total_aum), 4)
    hnw_dependency_ratio = round(safe_div(hnw_aum, total_aum), 4)
    avg_account_size     = round(safe_div(total_aum, total_accounts)) if total_accounts else 0
    avg_disc_account_size  = round(safe_div(disc_aum, disc_accounts)) if disc_accounts else 0
    avg_ndisc_account_size = round(safe_div(ndisc_aum, ndisc_accounts)) if ndisc_accounts else 0
    aum_per_advisor      = round(safe_div(total_aum, advisor_count)) if advisor_count else 0

    return {
        "firm_name":              str(row.get("Primary Business Name", "")).strip(),
        "address":                str(row.get("Main Office Street Address 1", "")).strip(),
        "city":                   str(row.get("Main Office City", "")).strip(),
        "state":                  str(row.get("Main Office State", "")).strip().upper(),
        "phone":                  str(row.get("Main Office Telephone Number", "")).strip(),
        "website_url":            str(row.get("Website Address", "")).strip(),
        "fiscal_year_end_month":  str(row.get("3B", "")).strip(),
        "latest_adv_filing_date": str(row.get("Latest ADV Filing Date", "")).strip(),
        "team_size":              team_size,
        "advisor_count":          advisor_count,
        "total_aum":              total_aum,
        "disc_aum":               disc_aum,
        "ndisc_aum":              ndisc_aum,
        "disc_accounts":          disc_accounts,
        "ndisc_accounts":         ndisc_accounts,
        "total_accounts":         total_accounts,
        "avg_account_size":        avg_account_size,
        "avg_disc_account_size":   avg_disc_account_size,
        "avg_ndisc_account_size":  avg_ndisc_account_size,
        "disc_pct_aum":           disc_pct_aum,
        "ndisc_pct_aum":          ndisc_pct_aum,
        "total_clients":          total_clients,
        "hnw_client_count":       hnw_count,
        "hnw_aum":                hnw_aum,
        "non_hnw_client_count":   non_hnw_count,
        "non_hnw_aum":            non_hnw_aum,
        "hnw_dependency_ratio":       hnw_dependency_ratio,
        "avg_hnw_account_size":       round(safe_div(hnw_aum, hnw_count)) if hnw_count else 0,
        "avg_non_hnw_account_size":   round(safe_div(non_hnw_aum, non_hnw_count)) if non_hnw_count else 0,
        "hnw_pct_of_clients":         round(safe_div(hnw_count, total_clients), 4) if total_clients else 0,
        "hnw_pct_of_aum":             round(safe_div(hnw_aum, total_aum), 4),
        "non_hnw_pct_of_clients":     round(safe_div(non_hnw_count, total_clients), 4) if total_clients else 0,
        "non_hnw_pct_of_aum":         round(safe_div(non_hnw_aum, total_aum), 4),
        "aum_per_advisor":            aum_per_advisor,
        "has_marketing_infrastructure":    has_marketing,
        "regulatory_disclosures_reported": "Yes" if has_disclosure else "None Reported",
    }

def build_firms_database():
    print("=" * 70)
    print(" ADVANTAGE DATA ENGINE -- PHASE 1: LONGITUDINAL INGESTION")
    print("=" * 70)

    print(f"\n[Step 1] Qualifying ICP firms from {LATEST_YEAR} snapshot...")
    df_latest = _load_csv(LATEST_YEAR, YEAR_FILES[LATEST_YEAR])
    if df_latest is None:
        raise FileNotFoundError(f"Latest year file missing: {YEAR_FILES[LATEST_YEAR]}")
    df_latest = _apply_qualification_filters(df_latest)
    qualified_crds = set(df_latest["Organization CRD#"].str.strip().tolist())
    print(f"    Qualified CRD universe: {len(qualified_crds):,} firms.\n")

    firms = {}
    for year in SORTED_YEARS:
        print(f"[Step 2] Extracting history block -- Year {year}...")
        df = df_latest if year == LATEST_YEAR else _load_csv(year, YEAR_FILES[year])
        if df is None:
            continue

        df_columns = set(df.columns)
        df_qualified = df[df["Organization CRD#"].str.strip().isin(qualified_crds)].copy()

        for _, row in df_qualified.iterrows():
            crd = str(row.get("Organization CRD#", "")).strip()
            if not crd:
                continue
            if crd not in firms:
                firms[crd] = {}
            firms[crd][year] = _extract_metrics(row, df_columns)

        print(f"    {len(df_qualified):,} qualified firm records extracted for {year}.\n")

    print("=" * 70)
    print(f"[PHASE 1 COMPLETE]  {len(firms):,} unique qualified RIAs in registry.")
    print("=" * 70 + "\n")
    return firms

# -- PHASE 2: 20-SIGNAL COMPOSITE SCORING --------------------------------------
def _score_firm(crd, history):
    if 2024 not in history or 2025 not in history or 2026 not in history:
        return None

    f24, f25, f26 = history[2024], history[2025], history[2026]
    aum_24, aum_25, aum_26    = f24["total_aum"],    f25["total_aum"],    f26["total_aum"]
    emp_24, emp_25, emp_26    = f24["team_size"],     f25["team_size"],    f26["team_size"]
    adv_24, adv_25, adv_26    = f24["advisor_count"], f25["advisor_count"], f26["advisor_count"]
    disc_acc_24, disc_acc_26  = f24["disc_accounts"], f26["disc_accounts"]
    acc_24, acc_25, acc_26    = f24["total_accounts"],f25["total_accounts"],f26["total_accounts"]

    if any(v <= 0 for v in [aum_24, aum_25, aum_26, emp_24, emp_25, emp_26, adv_24, adv_25, adv_26, acc_24, acc_25, acc_26]):
        return None

    score = 0
    aum_yoy_1 = (aum_25 - aum_24) / aum_24
    aum_yoy_2 = (aum_26 - aum_25) / aum_25
    emp_yoy_1 = (emp_25 - emp_24) / emp_24
    emp_yoy_2 = (emp_26 - emp_25) / emp_25
    adv_yoy_1 = (adv_25 - adv_24) / adv_24
    adv_yoy_2 = (adv_26 - adv_25) / adv_25
    aum_grow_3yr = (aum_26 - aum_24) / aum_24
    acc_grow_3yr = (acc_26 - acc_24) / acc_24

    # HC1: Headcount spikes then contraction
    if (emp_25 - emp_24) / emp_24 > 0.20 and emp_yoy_2 < -0.10: score += 8
    # HC2: Advisor attrition accelerating
    if (adv_25 - adv_24) < 0 and (adv_26 - adv_25) < 0 and (adv_26 - adv_25) < (adv_25 - adv_24): score += 9
    # HC3: Advisor collapse drop >= 25%
    if adv_yoy_1 < -0.25 or adv_yoy_2 < -0.25: score += 8
    # HC4 offset: Co-scaling health
    if (aum_yoy_1 >= 0.10 and emp_yoy_1 >= 0.10 and adv_yoy_1 >= 0.10) or (aum_yoy_2 >= 0.10 and emp_yoy_2 >= 0.10 and adv_yoy_2 >= 0.10): score -= 3
    # LV1: Unstable leverage
    if abs((emp_25/adv_25) - (emp_24/adv_24)) > 0.5 or abs((emp_26/adv_26) - (emp_25/adv_25)) > 0.5: score += 7
    # LV2: AUM-per-advisor spikes without underlying growth
    if ((aum_26/adv_26) - (aum_25/adv_25)) / (aum_25/adv_25) > 0.30 and aum_yoy_2 < 0.05: score += 7
    # LV3 offset: Advisor share improving
    lv3_flag = int(((adv_26/emp_26) - (adv_24/emp_24)) > 0.08)
    if lv3_flag: score -= 6
    # AC1: Discretionary drift
    if ((disc_acc_24/acc_24) - (disc_acc_26/acc_26)) > 0.10: score += 8
    # AC2: Account density compression
    if ((aum_26/acc_26) - (aum_24/acc_24)) / (aum_24/acc_24) < -0.15: score += 7
    # AC3: Volume-over-value trap
    if acc_grow_3yr > 0.10 and aum_grow_3yr < 0.03: score += 5
    # AC4 offset: Account quality upgrading
    if ((aum_26/acc_26) - (aum_24/acc_24)) / (aum_24/acc_24) > 0.20 and acc_grow_3yr >= 0.0: score -= 5
    # AV1: AUM stagnation
    if aum_grow_3yr < 0.05: score += 8
    # AV2: Boom-bust arc
    if aum_yoy_1 > 0.10 and aum_yoy_2 <= 0.0: score += 8
    # AV3: Persistent micro-decline
    if (aum_26 / aum_24 < 0.90) and (aum_yoy_1 > -0.05 and aum_yoy_2 > -0.05): score += 7
    # AV4 offset: Sustained positive growth momentum
    if aum_26 > aum_25 > aum_24 and aum_yoy_1 > 0 and aum_yoy_2 > 0: score -= 5
    # OP1: Operational friction flag
    op1_flag = int((emp_yoy_1 > 0 and aum_yoy_1 <= 0) or (emp_yoy_2 > 0 and aum_yoy_2 <= 0))
    if op1_flag: score += 7
    # OP2: HNW concentration risk
    if f26["hnw_dependency_ratio"] > 0.40: score += 7

    mk24, mk25, mk26 = f24["has_marketing_infrastructure"], f25["has_marketing_infrastructure"], f26["has_marketing_infrastructure"]
    mk1_flag = 0
    if None not in (mk24, mk25, mk26):
        if not mk24 and not mk25 and not mk26:
            score += 5
            mk1_flag = 1
        elif not mk24 and not mk25 and mk26:
            score -= 5

    disc_y1 = f24["regulatory_disclosures_reported"] == "Yes"
    disc_y2 = f25["regulatory_disclosures_reported"] == "Yes"
    disc_y3 = f26["regulatory_disclosures_reported"] == "Yes"
    if not disc_y1 and not disc_y2 and disc_y3: score += 10

    if score >= 70: tier = "Critical Turbulence"
    elif score >= 45: tier = "Structural Strain"
    elif score >= 20: tier = "Mild Friction"
    elif score > 0: tier = "Scaling Firm (Low Signal)"
    else: tier = "Stable"

    severe_crash_flag = int(aum_26 < aum_24 * 0.80)
    propensity_index  = op1_flag + mk1_flag + lv3_flag - severe_crash_flag

    return {
        "crd_number":      crd,
        "composite_score": score,
        "priority_tier":   tier,
        "propensity_index": propensity_index,
        "signal_flags": {
            "op1_operational_friction":    bool(op1_flag),
            "mk1_marketing_void":          bool(mk1_flag),
            "lv3_advisor_share_improving": bool(lv3_flag),
            "severe_aum_crash":            bool(severe_crash_flag),
        },
    }

def run_scoring_engine(firms):
    print("=" * 70)
    print(" ADVANTAGE DATA ENGINE -- PHASE 2: 20-SIGNAL SCORING ENGINE")
    print("=" * 70 + "\n")

    scored, skipped = [], 0
    for crd, history in firms.items():
        result = _score_firm(crd, history)
        if result is None: skipped += 1
        else: scored.append(result)

    print(f"  Scored : {len(scored):,} firms")
    print(f"  Skipped: {skipped:,} (insufficient historical data)\n")

    df = pd.DataFrame(scored)
    if df.empty: raise RuntimeError("Scoring loop failed to resolve registers.")

    # Apply Goldilocks filtration windows
    df_gk = df[(df["composite_score"] >= 20) & (df["composite_score"] <= 65)].copy()
    df_ranked = df_gk.sort_values(by=["propensity_index", "composite_score"], ascending=[False, False])
    
    # Target the entire unified pool length dynamically
    universal_pool = df_ranked.head(len(df_ranked))

    return universal_pool["crd_number"].tolist(), universal_pool

# -- DERIVED MULTI-YEAR METRICS -------------------------------------------------
def _compute_derived_metrics(history):
    available_years = sorted(history.keys())
    first_yr = available_years[0]
    last_yr  = available_years[-1]
    n_years  = last_yr - first_yr

    aum_start = history[first_yr]["total_aum"]
    aum_end   = history[last_yr]["total_aum"]
    aum_cagr  = compute_cagr(aum_start, aum_end, n_years)
    aum_total_growth = round(safe_div(aum_end - aum_start, aum_start) * 100, 2) if aum_start > 0 else None

    return {
        "years_available":         available_years,
        "first_year":              first_yr,
        "last_year":               last_yr,
        "aum_cagr_pct":           round(aum_cagr * 100, 2) if aum_cagr is not None else None,
        "aum_total_growth_pct":   aum_total_growth,
        "aum_by_year_m":          {yr: round(history[yr]["total_aum"] / 1e6, 3) for yr in available_years},
        "advisor_count_by_year":  {yr: history[yr]["advisor_count"] for yr in available_years},
        "avg_account_size_by_year": {yr: history[yr]["avg_account_size"] for yr in available_years},
        "hnw_dependency_by_year": {yr: history[yr]["hnw_dependency_ratio"] for yr in available_years},
        "aum_per_advisor_by_year": {yr: history[yr]["aum_per_advisor"] for yr in available_years},
    }

# -- REFACTORED OUTPUT GENERATION LAYER -----------------------------------------
def generate_outputs(universal_crds, all_score_df, firms):
    """
    Completely eliminates flat CSV files. Synchronizes and commits two clean JSON caches:
      1. prospects_top100.json   -- prioritized display layer for fast dashboard loads
      2. financial_profiles.json -- master core memory tree holding the entire universe
    """
    os.makedirs(os.path.dirname(OUTPUT_MASTER_JSON), exist_ok=True)
    score_lookup = {r["crd_number"]: r for r in all_score_df.to_dict("records")}

    top100_profiles = {}
    universal_profiles = {}

    for rank, crd in enumerate(universal_crds, start=1):
        if crd not in firms or crd not in score_lookup: 
            continue

        history   = firms[crd]
        score_rec = score_lookup[crd]
        derived   = _compute_derived_metrics(history)
        f26       = history[2026]

        # Standard master schema layout
        firm_payload = {
            "identity": {
                "crd_number":             crd,
                "firm_name":              f26["firm_name"],
                "address":                f26["address"],
                "city":                   f26["city"],
                "state":                  f26["state"],
                "phone":                  f26["phone"],
                "website_URL":            f26["website_url"], # Clean case mapping variable
                "iapd_url":               f"https://adviserinfo.sec.gov/firm/summary/{crd}",
                "fiscal_year_end_month":  f26["fiscal_year_end_month"],
                "latest_adv_filing_date": f26["latest_adv_filing_date"],
            },
            "scoring": {
                "rank":            rank,
                "composite_score": score_rec["composite_score"],
                "priority_tier":   score_rec["priority_tier"],
                "propensity_index": score_rec["propensity_index"],
                "signal_flags":    score_rec["signal_flags"],
            },
            "derived_metrics": derived,
            "history": {
                str(yr): metrics for yr, metrics in sorted(history.items())
            },
        }

        # Route to universal file databank
        universal_profiles[crd] = firm_payload

        # Route to priority cache slice if in Top 100 allocation
        if rank <= 100:
            top100_profiles[crd] = firm_payload

    # Write Priority Dashboard JSON
    with open(OUTPUT_TOP100_JSON, "w", encoding="utf-8") as fh:
        json.dump(top100_profiles, fh, indent=2, default=str)
    print(f"  [[OK]] Priority Cache Pool saved -> prospects_top100.json ({len(top100_profiles)} profiles)")

    # Write Master Databank JSON 
    with open(OUTPUT_MASTER_JSON, "w", encoding="utf-8") as fh:
        json.dump(universal_profiles, fh, indent=2, default=str)
    print(f"  [[OK]] Global Universal Database saved -> financial_profiles.json ({len(universal_profiles)} profiles)")

    return top100_profiles, universal_profiles

def main():
    print("\n" + "=" * 70)
    print("  ADVANTAGE DATA ENGINE  |  math_processor.py (JSON-PURE GLOBAL ENGINE)")
    print("=" * 70 + "\n")

    # Run processing tree
    firms = build_firms_database()
    universal_crds, all_score_df = run_scoring_engine(firms)
    
    print("Generating pure JSON output layers...")
    generate_outputs(universal_crds, all_score_df, firms)

    print(f"\n{'='*70}\n [[OK]] ADVantage Math Ingestion Engine completely converged.\n{'='*70}\n")

if __name__ == "__main__":
    main()