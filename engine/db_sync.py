"""
ADVantage PostgreSQL Sync Layer — db_sync.py
=============================================
Handles all CRM persistence to the local ADVantage DBeaver database.
Tables: public.firms (parent) and public.ai_insights (child).

Schema (create in DBeaver before first run):

    CREATE TABLE public.firms (
        id SERIAL PRIMARY KEY,
        crd_number VARCHAR(50) UNIQUE NOT NULL,
        firm_name VARCHAR(255) NOT NULL,
        website_url TEXT,
        url_slug VARCHAR(255),
        propensity_index NUMERIC,
        aum_2022_m NUMERIC,
        aum_2023_m NUMERIC,
        aum_2024_m NUMERIC,
        aum_2025_m NUMERIC,
        aum_2026_m NUMERIC,
        advisor_count_2026 INT,
        total_clients_raw INT,
        aum_growth_pct NUMERIC,
        hnw_pct NUMERIC,
        advisor_aum_str VARCHAR(50),
        avg_client_str VARCHAR(50)
    );

    CREATE TABLE public.ai_insights (
        id SERIAL PRIMARY KEY,
        firm_id INT REFERENCES public.firms(id) ON DELETE CASCADE,
        story_hook TEXT,
        capacity_diagnostics JSONB,
        positioning_audits JSONB,
        raw_response_payload JSONB,
        youtube_embed_id VARCHAR(50),
        insight_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

import json
from datetime import datetime
from urllib.parse import quote_plus

try:
    from sqlalchemy import create_engine, text
    _SQLALCHEMY_AVAILABLE = True
except ImportError:
    _SQLALCHEMY_AVAILABLE = False

_DB_USER = "pgp_admin"
_DB_RAW_PASSWORD = "Myd@tAYuh!$5"
_DB_HOST = "localhost"
_DB_PORT = 5432
_DB_NAME = "ADVantage"


def _get_engine():
    safe_password = quote_plus(_DB_RAW_PASSWORD)
    return create_engine(
        f"postgresql://{_DB_USER}:{safe_password}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}",
        pool_pre_ping=True
    )


def upsert_firm(crd, firm_name, website_url, url_slug, propensity_index,
                aum_data_points, advisor_count_2026, total_clients_raw,
                aum_growth_pct, hnw_pct, advisor_aum_str, avg_client_str):
    """
    UPSERT a firm record into public.firms.

    aum_data_points must be a list of 5 floats indexed as:
        [0]=2022, [1]=2023, [2]=2024, [3]=2025, [4]=2026

    Returns the firm's primary key (id) on success, None on failure.
    """
    if not _SQLALCHEMY_AVAILABLE:
        print("  [!] SQLAlchemy not installed — DB sync skipped.")
        return None

    def _safe_aum(points, idx):
        try:
            return float(points[idx]) if idx < len(points) else 0.0
        except (TypeError, ValueError):
            return 0.0

    query = text("""
        INSERT INTO public.firms (
            crd_number, firm_name, website_url, url_slug, propensity_index,
            aum_2022_m, aum_2023_m, aum_2024_m, aum_2025_m, aum_2026_m,
            advisor_count_2026, total_clients_raw,
            aum_growth_pct, hnw_pct, advisor_aum_str, avg_client_str
        )
        VALUES (
            :crd, :firm_name, :website_url, :url_slug, :propensity_index,
            :aum_2022, :aum_2023, :aum_2024, :aum_2025, :aum_2026,
            :advisor_count, :total_clients,
            :aum_growth_pct, :hnw_pct, :advisor_aum_str, :avg_client_str
        )
        ON CONFLICT (crd_number) DO UPDATE SET
            firm_name          = EXCLUDED.firm_name,
            website_url        = EXCLUDED.website_url,
            url_slug           = EXCLUDED.url_slug,
            propensity_index   = EXCLUDED.propensity_index,
            aum_2022_m         = EXCLUDED.aum_2022_m,
            aum_2023_m         = EXCLUDED.aum_2023_m,
            aum_2024_m         = EXCLUDED.aum_2024_m,
            aum_2025_m         = EXCLUDED.aum_2025_m,
            aum_2026_m         = EXCLUDED.aum_2026_m,
            advisor_count_2026 = EXCLUDED.advisor_count_2026,
            total_clients_raw  = EXCLUDED.total_clients_raw,
            aum_growth_pct     = EXCLUDED.aum_growth_pct,
            hnw_pct            = EXCLUDED.hnw_pct,
            advisor_aum_str    = EXCLUDED.advisor_aum_str,
            avg_client_str     = EXCLUDED.avg_client_str
        RETURNING id;
    """)

    try:
        engine = _get_engine()
        with engine.begin() as conn:
            result = conn.execute(query, {
                "crd":              str(crd),
                "firm_name":        str(firm_name),
                "website_url":      str(website_url or ""),
                "url_slug":         str(url_slug),
                "propensity_index": float(propensity_index) if propensity_index is not None else 0.0,
                "aum_2022":         _safe_aum(aum_data_points, 0),
                "aum_2023":         _safe_aum(aum_data_points, 1),
                "aum_2024":         _safe_aum(aum_data_points, 2),
                "aum_2025":         _safe_aum(aum_data_points, 3),
                "aum_2026":         _safe_aum(aum_data_points, 4),
                "advisor_count":    int(advisor_count_2026) if advisor_count_2026 else 0,
                "total_clients":    int(total_clients_raw) if total_clients_raw else 0,
                "aum_growth_pct":   float(aum_growth_pct),
                "hnw_pct":          float(hnw_pct),
                "advisor_aum_str":  str(advisor_aum_str),
                "avg_client_str":   str(avg_client_str),
            })
            firm_id = result.fetchone()[0]
            print(f"  [✔] CRM: firms record synced (id={firm_id}).")
            return firm_id
    except Exception as e:
        print(f"  [!] DB firms upsert error: {e}")
        return None


def insert_insight(firm_id, story_hook, capacity_diagnostics, positioning_audits,
                   raw_response_payload, youtube_embed_id):
    """
    INSERT a new row into public.ai_insights.

    capacity_diagnostics  — list of 3 objects {headline, insight, opportunity}
    positioning_audits    — list of 3 objects {headline, insight, opportunity}
    raw_response_payload  — dict with full audit trail (inferences, gaps, metrics, web markdown)
    youtube_embed_id      — 11-char YouTube ID string
    """
    if not _SQLALCHEMY_AVAILABLE or firm_id is None:
        return

    query = text("""
        INSERT INTO public.ai_insights (
            firm_id, story_hook,
            capacity_diagnostics, positioning_audits,
            raw_response_payload, youtube_embed_id,
            insight_timestamp
        )
        VALUES (
            :firm_id, :story_hook,
            CAST(:capacity_diagnostics AS JSONB),
            CAST(:positioning_audits AS JSONB),
            CAST(:raw_response_payload AS JSONB),
            :youtube_embed_id,
            :insight_timestamp
        );
    """)

    try:
        engine = _get_engine()
        with engine.begin() as conn:
            conn.execute(query, {
                "firm_id":              int(firm_id),
                "story_hook":           str(story_hook),
                "capacity_diagnostics": json.dumps(capacity_diagnostics, default=str),
                "positioning_audits":   json.dumps(positioning_audits, default=str),
                "raw_response_payload": json.dumps(raw_response_payload, default=str),
                "youtube_embed_id":     str(youtube_embed_id),
                "insight_timestamp":    datetime.utcnow(),
            })
            print(f"  [✔] CRM: ai_insights record inserted (firm_id={firm_id}).")
    except Exception as e:
        print(f"  [!] DB ai_insights insert error: {e}")
