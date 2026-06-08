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
        avg_client_str VARCHAR(50),
        address TEXT,
        city VARCHAR(100),
        state VARCHAR(10),
        phone VARCHAR(30),
        iapd_url TEXT,
        latest_adv_filing_date VARCHAR(20),
        composite_score INT,
        priority_tier VARCHAR(100),
        rank_position INT,
        signal_flags JSONB,
        aum_cagr_pct NUMERIC,
        aum_by_year_m JSONB,
        hnw_by_year_m JSONB,
        advisor_count_by_year JSONB,
        avg_account_size_by_year JSONB,
        hnw_dependency_by_year JSONB,
        aum_per_advisor_by_year JSONB,
        live_url TEXT,
        last_deployed_at TIMESTAMP
    );

    CREATE TABLE public.ai_insights (
        id SERIAL PRIMARY KEY,
        firm_id INT REFERENCES public.firms(id) ON DELETE CASCADE,
        story_hook TEXT,
        capacity_diagnostics JSONB,
        positioning_audits JSONB,
        raw_response_payload JSONB,
        youtube_embed_id VARCHAR(50),
        live_url TEXT,
        model_version VARCHAR(50),
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
                aum_growth_pct, hnw_pct, advisor_aum_str, avg_client_str,
                address=None, city=None, state=None, phone=None, iapd_url=None,
                latest_adv_filing_date=None, composite_score=None, priority_tier=None,
                rank_position=None, signal_flags=None, aum_cagr_pct=None,
                aum_by_year_m=None, hnw_by_year_m=None, advisor_count_by_year=None,
                avg_account_size_by_year=None, hnw_dependency_by_year=None,
                aum_per_advisor_by_year=None, live_url=None, last_deployed_at=None):
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
            aum_growth_pct, hnw_pct, advisor_aum_str, avg_client_str,
            address, city, state, phone, iapd_url, latest_adv_filing_date,
            composite_score, priority_tier, rank_position, signal_flags,
            aum_cagr_pct, aum_by_year_m, hnw_by_year_m,
            advisor_count_by_year, avg_account_size_by_year,
            hnw_dependency_by_year, aum_per_advisor_by_year,
            live_url, last_deployed_at
        )
        VALUES (
            :crd, :firm_name, :website_url, :url_slug, :propensity_index,
            :aum_2022, :aum_2023, :aum_2024, :aum_2025, :aum_2026,
            :advisor_count, :total_clients,
            :aum_growth_pct, :hnw_pct, :advisor_aum_str, :avg_client_str,
            :address, :city, :state, :phone, :iapd_url, :latest_adv_filing_date,
            :composite_score, :priority_tier, :rank_position,
            CAST(:signal_flags AS JSONB),
            :aum_cagr_pct,
            CAST(:aum_by_year_m AS JSONB),
            CAST(:hnw_by_year_m AS JSONB),
            CAST(:advisor_count_by_year AS JSONB),
            CAST(:avg_account_size_by_year AS JSONB),
            CAST(:hnw_dependency_by_year AS JSONB),
            CAST(:aum_per_advisor_by_year AS JSONB),
            :live_url, :last_deployed_at
        )
        ON CONFLICT (crd_number) DO UPDATE SET
            firm_name                = EXCLUDED.firm_name,
            website_url              = EXCLUDED.website_url,
            url_slug                 = EXCLUDED.url_slug,
            propensity_index         = EXCLUDED.propensity_index,
            aum_2022_m               = EXCLUDED.aum_2022_m,
            aum_2023_m               = EXCLUDED.aum_2023_m,
            aum_2024_m               = EXCLUDED.aum_2024_m,
            aum_2025_m               = EXCLUDED.aum_2025_m,
            aum_2026_m               = EXCLUDED.aum_2026_m,
            advisor_count_2026       = EXCLUDED.advisor_count_2026,
            total_clients_raw        = EXCLUDED.total_clients_raw,
            aum_growth_pct           = EXCLUDED.aum_growth_pct,
            hnw_pct                  = EXCLUDED.hnw_pct,
            advisor_aum_str          = EXCLUDED.advisor_aum_str,
            avg_client_str           = EXCLUDED.avg_client_str,
            address                  = EXCLUDED.address,
            city                     = EXCLUDED.city,
            state                    = EXCLUDED.state,
            phone                    = EXCLUDED.phone,
            iapd_url                 = EXCLUDED.iapd_url,
            latest_adv_filing_date   = EXCLUDED.latest_adv_filing_date,
            composite_score          = EXCLUDED.composite_score,
            priority_tier            = EXCLUDED.priority_tier,
            rank_position            = EXCLUDED.rank_position,
            signal_flags             = EXCLUDED.signal_flags,
            aum_cagr_pct             = EXCLUDED.aum_cagr_pct,
            aum_by_year_m            = EXCLUDED.aum_by_year_m,
            hnw_by_year_m            = EXCLUDED.hnw_by_year_m,
            advisor_count_by_year    = EXCLUDED.advisor_count_by_year,
            avg_account_size_by_year = EXCLUDED.avg_account_size_by_year,
            hnw_dependency_by_year   = EXCLUDED.hnw_dependency_by_year,
            aum_per_advisor_by_year  = EXCLUDED.aum_per_advisor_by_year,
            live_url                 = EXCLUDED.live_url,
            last_deployed_at         = EXCLUDED.last_deployed_at
        RETURNING id;
    """)

    try:
        print(f"  [DEBUG] address={address}, city={city}, state={state}, composite_score={composite_score}, priority_tier={priority_tier}, aum_cagr_pct={aum_cagr_pct}, live_url={live_url}")
        engine = _get_engine()
        with engine.begin() as conn:
            result = conn.execute(query, {
                "crd":                      str(crd),
                "firm_name":                str(firm_name),
                "website_url":              str(website_url or ""),
                "url_slug":                 str(url_slug),
                "propensity_index":         float(propensity_index) if propensity_index is not None else 0.0,
                "aum_2022":                 _safe_aum(aum_data_points, 0),
                "aum_2023":                 _safe_aum(aum_data_points, 1),
                "aum_2024":                 _safe_aum(aum_data_points, 2),
                "aum_2025":                 _safe_aum(aum_data_points, 3),
                "aum_2026":                 _safe_aum(aum_data_points, 4),
                "advisor_count":            int(advisor_count_2026) if advisor_count_2026 else 0,
                "total_clients":            int(total_clients_raw) if total_clients_raw else 0,
                "aum_growth_pct":           float(aum_growth_pct),
                "hnw_pct":                  float(hnw_pct),
                "advisor_aum_str":          str(advisor_aum_str),
                "avg_client_str":           str(avg_client_str),
                "address":                  str(address) if address else None,
                "city":                     str(city) if city else None,
                "state":                    str(state) if state else None,
                "phone":                    str(phone) if phone else None,
                "iapd_url":                 str(iapd_url) if iapd_url else None,
                "latest_adv_filing_date":   str(latest_adv_filing_date) if latest_adv_filing_date else None,
                "composite_score":          int(composite_score) if composite_score is not None else None,
                "priority_tier":            str(priority_tier) if priority_tier else None,
                "rank_position":            int(rank_position) if rank_position is not None else None,
                "signal_flags":             json.dumps(signal_flags) if signal_flags else None,
                "aum_cagr_pct":             float(aum_cagr_pct) if aum_cagr_pct is not None else None,
                "aum_by_year_m":            json.dumps(aum_by_year_m) if aum_by_year_m else None,
                "hnw_by_year_m":            json.dumps(hnw_by_year_m) if hnw_by_year_m else None,
                "advisor_count_by_year":    json.dumps(advisor_count_by_year) if advisor_count_by_year else None,
                "avg_account_size_by_year": json.dumps(avg_account_size_by_year) if avg_account_size_by_year else None,
                "hnw_dependency_by_year":   json.dumps(hnw_dependency_by_year) if hnw_dependency_by_year else None,
                "aum_per_advisor_by_year":  json.dumps(aum_per_advisor_by_year) if aum_per_advisor_by_year else None,
                "live_url":                 str(live_url) if live_url else None,
                "last_deployed_at":         last_deployed_at or datetime.utcnow(),
            })
            firm_id = result.fetchone()[0]
            print(f"  [✔] CRM: firms record synced (id={firm_id}).")
            return firm_id
    except Exception as e:
        print(f"  [!] DB firms upsert error: {e}")
        return None


def insert_insight(firm_id, story_hook, capacity_diagnostics, positioning_audits,
                   raw_response_payload, youtube_embed_id, live_url=None, model_version=None):
    if not _SQLALCHEMY_AVAILABLE or firm_id is None:
        return

    query = text("""
        INSERT INTO public.ai_insights (
            firm_id, story_hook,
            capacity_diagnostics, positioning_audits,
            raw_response_payload, youtube_embed_id,
            live_url, model_version,
            insight_timestamp
        )
        VALUES (
            :firm_id, :story_hook,
            CAST(:capacity_diagnostics AS JSONB),
            CAST(:positioning_audits AS JSONB),
            CAST(:raw_response_payload AS JSONB),
            :youtube_embed_id,
            :live_url, :model_version,
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
                "live_url":             str(live_url) if live_url else None,
                "model_version":        str(model_version) if model_version else None,
                "insight_timestamp":    datetime.utcnow(),
            })
            print(f"  [✔] CRM: ai_insights record inserted (firm_id={firm_id}).")
    except Exception as e:
        print(f"  [!] DB ai_insights insert error: {e}")
