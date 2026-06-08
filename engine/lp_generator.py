"""
ADVantage Presentation Layer -- lp_generator.py (V3 Interactive Deploy Engine)
===============================================================================
Precision Growth Partners | Agentic ABM Infrastructure

V3 Changes:
  - Two-phase interactive deploy: push placeholder frame → pause for YouTube → push final
  - YouTube ID extraction handles all URL formats (youtu.be, watch?v=, embed/, raw ID)
  - PostgreSQL CRM sync via engine/db_sync.py (ADVantage database)
  - Combined V1+V2 HTML layout: video → CTA → chart → cards → diagnostics → CTA → disclosures
"""

import os
import json
import sys
import subprocess
import re
from pathlib import Path

current_script_dir = Path(__file__).resolve().parent
project_root = current_script_dir.parent
INPUT_JSON = project_root / "data" / "output" / "financial_profiles.json"
CONFIG_PATH = project_root / "advantage_config.json"

try:
    from engine.db_sync import upsert_firm, insert_insight
    _DB_SYNC_AVAILABLE = True
except ImportError:
    _DB_SYNC_AVAILABLE = False


def _extract_youtube_id(raw_input):
    """Parse an 11-char YouTube video ID from any input format."""
    raw = raw_input.strip()
    if "youtu.be/" in raw:
        vid = raw.split("youtu.be/")[-1].split("?")[0]
    elif "youtube.com/watch" in raw:
        vid = raw.split("v=")[-1].split("&")[0].split("?")[0]
    elif "youtube.com/embed/" in raw:
        vid = raw.split("youtube.com/embed/")[-1].split("?")[0].split('"')[0]
    else:
        vid = raw.split("?")[0]
    return vid.strip()[:11]


def format_smart_currency(raw_value, force_millions=False):
    if not raw_value:
        return "N/A"
    try:
        clean_str = str(raw_value).replace("$", "").replace(",", "").strip()
        val = float(clean_str)
        if val <= 0:
            return "N/A"
        if force_millions:
            if val >= 1000:
                return f"${val / 1000:.2f}B".replace(".00", "")
            return f"${round(val)}M"
        if val >= 1e9:
            return f"${val / 1e9:.2f}B".replace(".00", "")
        elif val >= 1e6:
            if val >= 1e8:
                return f"${round(val / 1e6)}M"
            return f"${val / 1e6:.2f}M".replace(".00", "")
        elif val >= 1e3:
            return f"${round(val / 1e3)}K"
        else:
            return f"${round(val)}"
    except (ValueError, TypeError):
        return str(raw_value)


def _build_html(firm_name, url_slug, aum_growth_pct, aum_per_advisor, avg_client_size,
                hnw_pct, aum_data_points, hnw_data_points, inferences_clean, gaps_clean,
                youtube_id=None):
    """
    Compile the full landing page HTML string.
    youtube_id=None renders a 'Video presentation loading...' placeholder frame.
    """

    if youtube_id:
        video_block = (
            f'<div class="relative w-full rounded-xl overflow-hidden shadow-2xl'
            f' border border-[#4a4a4a]/60" style="aspect-ratio: 16/9;">\n'
            f'            <iframe class="absolute inset-0 w-full h-full"\n'
            f'                src="https://www.youtube.com/embed/{youtube_id}"\n'
            f'                title="ADVantage Review: {firm_name}"\n'
            f'                frameborder="0"\n'
            f'                allow="accelerometer; autoplay; clipboard-write;'
            f' encrypted-media; gyroscope; picture-in-picture; web-share"\n'
            f'                allowfullscreen>\n'
            f'            </iframe>\n'
            f'        </div>'
        )
    else:
        video_block = (
            '<div class="relative w-full rounded-xl overflow-hidden border border-[#4a4a4a]/60'
            ' bg-[#1e1e1e] flex items-center justify-center" style="aspect-ratio: 16/9;">\n'
            '            <p class="text-slate-500 text-sm font-light tracking-wide">'
            'Video presentation loading...</p>\n'
            '        </div>'
        )

    def _diagnostic_item(item, accent_color):
        headline = item.get("headline", "Strategic Focus")
        insight = item.get("insight", "")
        opportunity = item.get("opportunity", "")
        opp_html = (
            f'<span class="text-slate-400 font-light italic block text-[11px]'
            f' border-l border-{accent_color}/30 pl-2">{opportunity}</span>'
        ) if opportunity else ""
        return (
            f'<li class="text-xs leading-relaxed font-light">'
            f'<div class="flex gap-2 items-start">'
            f'<span class="text-{accent_color} font-mono mt-0.5">•</span>'
            f'<div>'
            f'<span class="font-semibold text-white tracking-wide block mb-0.5">{headline}</span>'
            f'<span class="text-slate-300 font-light block mb-1">{insight}</span>'
            f'{opp_html}'
            f'</div></div></li>'
        )

    capacity_items = "\n".join(
        _diagnostic_item(item, "[#bf8660]") for item in inferences_clean
    )
    positioning_items = "\n".join(
        _diagnostic_item(item, "slate-400") for item in gaps_clean
    )

    cta_html = (
        '<div class="text-center py-4 max-w-2xl mx-auto">'
        '<a href="https://calendly.com/precisiongrowthpartners/adv-discovery-call"'
        ' target="_blank"'
        ' class="inline-block bg-[#bf8660] text-white font-bold text-md px-10 py-4'
        ' rounded-xl transition-all hover:bg-black shadow-lg">'
        'Book a 15-min Discovery Call'
        '</a></div>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADVantage Review: {firm_name}</title>
    <meta property="og:type" content="website">
    <meta property="og:title" content="Custom 5-Year Growth Analytics for {firm_name}">
    <meta property="og:url" content="https://advantage.precisiongrowthpartners.io/{url_slug}">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400&display=swap');
        body {{ font-family: 'Poppins', sans-serif; }}
        .brand-transition {{ transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
    </style>
</head>
<body class="bg-[#2b2b2b] text-slate-100 min-h-screen flex flex-col justify-between selection:bg-[#bf8660] selection:text-black antialiased">

    <header class="max-w-4xl w-full mx-auto px-6 pt-12 pb-4 text-left flex flex-col gap-4 border-b border-[#4a4a4a]/40">
        <a href="https://precisiongrowthpartners.io/" target="_blank" rel="noopener noreferrer" class="inline-block hover:opacity-80 transition-opacity">
            <img src="https://framerusercontent.com/images/S8VQesQNIT2grrkBle7vzbRnVZc.png?scale-down-to=512&width=8000&height=4500"
                alt="Precision Growth Partners Logo"
                class="w-28 sm:w-44 h-auto object-contain block">
        </a>
        <div>
            <h1 class="text-3xl lg:text-5xl font-bold tracking-tight text-white mb-2 sm:mb-1">{firm_name}</h1>
            <p class="text-sm sm:text-md text-[#bf8660] font-medium tracking-wide uppercase">We studied 5 years of your firm&#39;s data. Here&#39;s what we found.</p>
        </div>
    </header>

    <main class="max-w-4xl w-full mx-auto px-6 py-10 flex-1 space-y-10">

        <!-- Video Embed -->
        <section>
            {video_block}
        </section>

        <!-- Book a Call — Primary CTA -->
        {cta_html}

        <!-- 5-Year Growth Chart -->
        <section class="bg-[#2b2b2b] border border-[#4a4a4a]/60 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
            <div class="absolute top-0 left-0 w-1 h-full bg-[#bf8660]"></div>
            <div class="flex items-center justify-between mb-6">
                <h2 class="text-xs font-semibold tracking-widest text-white uppercase">5-Year Growth Trail</h2>
                <span class="text-[10px] text-slate-500 font-mono">Source: SEC Form ADV Part 1A Matrix</span>
            </div>
            <div class="h-64 relative w-full">
                <canvas id="growthChart"></canvas>
            </div>
        </section>

        <!-- Metric Snapshot Cards -->
        <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="bg-[#2b2b2b] border border-[#4a4a4a]/50 p-5 rounded-xl shadow-lg brand-transition hover:border-[#bf8660]/50">
                <span class="text-[11px] text-white font-medium uppercase tracking-wider block">AUM Growth (5yr)</span>
                <span class="text-3xl lg:text-4xl font-bold text-[#bf8660] my-1 block tracking-tight">{aum_growth_pct}%</span>
            </div>
            <div class="bg-[#2b2b2b] border border-[#4a4a4a]/50 p-5 rounded-xl shadow-lg brand-transition hover:border-[#bf8660]/50">
                <span class="text-[11px] text-white font-medium uppercase tracking-wider block">AVG AUM per Advisor</span>
                <span class="text-3xl lg:text-4xl font-bold text-[#bf8660] my-1 block tracking-tight">{aum_per_advisor}</span>
            </div>
            <div class="bg-[#2b2b2b] border border-[#4a4a4a]/50 p-5 rounded-xl shadow-lg brand-transition hover:border-[#bf8660]/50">
                <span class="text-[11px] text-white font-medium uppercase tracking-wider block">Avg Client Size</span>
                <span class="text-3xl lg:text-4xl font-bold text-[#bf8660] my-1 block tracking-tight">{avg_client_size}</span>
            </div>
            <div class="bg-[#2b2b2b] border border-[#4a4a4a]/50 p-5 rounded-xl shadow-lg brand-transition hover:border-[#bf8660]/50">
                <span class="text-[11px] text-white font-medium uppercase tracking-wider block">HNW % of Book</span>
                <span class="text-3xl lg:text-4xl font-bold text-[#bf8660] my-1 block tracking-tight">{hnw_pct}%</span>
            </div>
        </section>

        <!-- Diagnostics Grid -->
        <section class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            <div class="bg-[#242424] border border-[#4a4a4a]/40 p-6 rounded-xl relative shadow-xl">
                <h4 class="text-xs font-bold uppercase tracking-wider text-white border-b border-[#4a4a4a]/30 pb-3 mb-4 flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-[#bf8660]"></span> Capacity Diagnostics
                </h4>
                <ul class="space-y-4">
                    {capacity_items}
                </ul>
            </div>
            <div class="bg-[#242424] border border-[#4a4a4a]/40 p-6 rounded-xl relative shadow-xl">
                <h4 class="text-xs font-bold uppercase tracking-wider text-white border-b border-[#4a4a4a]/30 pb-3 mb-4 flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Positioning Audits
                </h4>
                <ul class="space-y-4">
                    {positioning_items}
                </ul>
            </div>
        </section>

        <!-- Book a Call — Secondary CTA -->
        {cta_html}

    </main>

    <footer class="w-full border-t border-[#4a4a4a]/30 bg-[#2b2b2b] py-8 text-center px-6 space-y-2">
        <p class="text-xs text-slate-400 font-light tracking-wide">Secure PGP Protected ADVantage Array Engine</p>
        <p class="text-[10px] text-slate-500 max-w-2xl mx-auto leading-normal font-light">
            Analysis built using verified, publicly accessible SEC Form ADV Part 1A filings (2022&#8211;2026).
            All data sourced directly from IAPD regulatory databases. This presentation is intended for
            informational and business development purposes only and does not constitute investment advice
            or a solicitation. Past performance and AUM trajectories are not indicative of future results.
        </p>
    </footer>

    <script>
        const ctx = document.getElementById('growthChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: ['2022', '2023', '2024', '2025', '2026'],
                datasets: [{{
                    label: 'Total AUM ($M)',
                    data: {json.dumps(aum_data_points)},
                    backgroundColor: '#bf8660',
                    borderColor: '#bf8660',
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.8,
                    categoryPercentage: 0.6
                }}, {{
                    label: 'HNW AUM ($M)',
                    data: {json.dumps(hnw_data_points)},
                    backgroundColor: 'rgba(255, 255, 255, 0.25)',
                    borderColor: 'rgba(255, 255, 255, 0.4)',
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.8,
                    categoryPercentage: 0.6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'top',
                        labels: {{ color: '#e2e8f0', font: {{ family: 'Poppins', size: 11, weight: '500' }} }}
                    }}
                }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#cbd5e1', font: {{ size: 11, family: 'Poppins' }} }} }},
                    y: {{ grid: {{ color: 'rgba(74, 74, 74, 0.25)' }}, ticks: {{ color: '#cbd5e1' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>"""


def generate_landing_page(target_crd):
    """
    V3 Two-Phase Interactive Deploy:
      Phase 1 — Build placeholder frame, push to Netlify so the URL is live for screen recording.
      [PAUSE]  — Terminal halts; operator records video and pastes YouTube link.
      Phase 2 — Rebuild with embedded video, sync CRM, push final production asset.
    """
    print("=" * 75)
    print(f"  PROJECT ADVANTAGE V3 — INTERACTIVE DEPLOY ENGINE")
    print("=" * 75)

    if not CONFIG_PATH.exists():
        print("[!] ERROR: advantage_config.json missing from workspace.")
        return
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    if not INPUT_JSON.exists():
        print(f"[!] ERROR: financial_profiles.json missing. Run math_processor first.")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        profiles = json.load(f)

    if str(target_crd) not in profiles:
        print(f"  [!] CRD #{target_crd} not found in working memory registers.")
        return

    firm = profiles[str(target_crd)]
    identity = firm.get("identity", {})
    derived = firm.get("derived_metrics", {})
    history = firm.get("history", {})
    scoring = firm.get("scoring", {})

    firm_name = identity.get("firm_name", "Your Practice").strip()
    website_url = identity.get("website_URL", "") or identity.get("website_url", "")

    # Pull V3 structured narrative objects from storyteller output
    inferences_clean = firm.get("capacity_diagnostics_clean", [])
    gaps_clean = firm.get("positioning_audits_clean", [])
    story_hook = firm.get("story_hook", "")

    # Backwards-compatibility: convert legacy flat string arrays to structured objects
    if not inferences_clean:
        raw_inf = firm.get("financial_inferences", [])
        inferences_clean = [
            {"headline": "Operational Focus", "insight": b, "opportunity": ""}
            for b in raw_inf if str(b).strip()
        ]
    if not gaps_clean:
        raw_gaps = firm.get("marketing_gaps", [])
        gaps_clean = [
            {"headline": "Positioning Shift", "insight": b, "opportunity": ""}
            for b in raw_gaps if str(b).strip()
        ]

    if not inferences_clean or not gaps_clean or not story_hook:
        print(f"  [!] ERROR: Missing agent states for CRD #{target_crd}. Run stages 1-3 first.")
        return

    # Slug: "IKE CAPITAL, LLC" → "ike-capital"
    raw_name = firm_name.lower()
    for ext in ["llc", "l.l.c.", "inc.", "inc", "corp", "co.", "limited", "ltd.", "ltd"]:
        if raw_name.endswith(ext):
            raw_name = raw_name.rsplit(ext, 1)[0].strip()
    url_slug = re.sub(r'[^a-z0-9]+', '-', raw_name).strip('-')

    firm_folder = project_root / url_slug
    os.makedirs(firm_folder, exist_ok=True)
    destination = firm_folder / "index.html"
    print(f"  -> Directory: {url_slug}/index.html")

    # ── AUM DATA NORMALIZATION ────────────────────────────────────────────────
    years_5 = ["2022", "2023", "2024", "2025", "2026"]
    aum_by_year = derived.get("aum_by_year_m", {})

    aum_data_points = []
    for yr in years_5:
        val = aum_by_year.get(yr, 0.0)
        aum_data_points.append(round(val / 1e6) if val > 1e6 else round(val))

    print(f"  [*] AUM Points ($M): {aum_data_points}")

    hnw_data_points = []
    for yr in years_5:
        yr_data = history.get(yr) or history.get(int(yr)) or {}
        hnw_raw = (yr_data.get("hnw_aum_raw") or yr_data.get("hnw_aum")
                   or yr_data.get("hnw_assets") or 0.0)
        try:
            hnw_val = float(hnw_raw)
        except (ValueError, TypeError):
            hnw_val = 0.0

        if hnw_val == 0.0:
            ratio = (yr_data.get("hnw_dependency_ratio") or yr_data.get("hnw_pct")
                     or yr_data.get("hnw_ratio")
                     or derived.get("hnw_dependency_by_year", {}).get(yr, 0.0))
            try:
                r = float(ratio)
                if r > 1.0:
                    r /= 100.0
                hnw_val = aum_data_points[years_5.index(yr)] * 1e6 * r
            except (ValueError, TypeError):
                hnw_val = 0.0

        if hnw_val > 1e6:
            hnw_data_points.append(round(hnw_val / 1e6))
        elif hnw_val > 1e3:
            hnw_data_points.append(round(hnw_val / 1e3))
        else:
            hnw_data_points.append(round(hnw_val))

    print(f"  [*] HNW Points ($M): {hnw_data_points}")

    # ── DERIVED SNAPSHOT METRICS ──────────────────────────────────────────────
    f26 = history.get("2026") or history.get(2026) or {}
    aum_start = aum_data_points[0]
    aum_end = aum_data_points[-1]
    aum_growth_pct = round(((aum_end - aum_start) / aum_start) * 100) if aum_start > 0 else 0
    hnw_pct = round((hnw_data_points[-1] / aum_data_points[-1]) * 100) if aum_data_points[-1] > 0 else 0

    raw_apa = f26.get("aum_per_advisor", 0)
    aum_per_advisor = (format_smart_currency(raw_apa, force_millions=True)
                       if 0 < raw_apa < 1e4 else format_smart_currency(raw_apa))

    raw_avg = f26.get("avg_account_size", 0) or f26.get("avg_client_size", 0) or 0
    if raw_avg > 1e8:
        raw_avg /= 1e3
    avg_client_size = format_smart_currency(raw_avg)

    advisor_count_2026 = f26.get("advisor_count", 0) or f26.get("advisor_employees_raw", 0) or 0
    total_clients_raw = f26.get("total_clients", 0) or f26.get("total_clients_raw", 0) or 0
    propensity_index = scoring.get("propensity_index", 0)

    # ── PHASE 1: PUSH PLACEHOLDER FRAME ──────────────────────────────────────
    print("\n  [PHASE 1] Building initial placeholder frame for video recording...")

    phase1_html = _build_html(
        firm_name=firm_name, url_slug=url_slug,
        aum_growth_pct=aum_growth_pct, aum_per_advisor=aum_per_advisor,
        avg_client_size=avg_client_size, hnw_pct=hnw_pct,
        aum_data_points=aum_data_points, hnw_data_points=hnw_data_points,
        inferences_clean=inferences_clean, gaps_clean=gaps_clean,
        youtube_id=None
    )
    with open(destination, "w", encoding="utf-8") as fh:
        fh.write(phase1_html)

    _git_push(project_root, f"ADVantage frame: {url_slug}")

    live_url = f"https://advantage.precisiongrowthpartners.io/{url_slug}"
    print(f"\n{'='*60}")
    print(f"  FRAMEWORK IS LIVE")
    print(f"{'='*60}")
    print(f"  Live URL: {live_url}")
    print(f"\n  Instructions:")
    print(f"  1. Open the link above — your firm dashboard is live.")
    print(f"  2. Record your YouTube video using the briefing script below.")
    print(f"  3. Upload to YouTube and copy the share URL.")
    print(f"{'─'*60}")
    print(f"\n  OPERATOR BRIEFING SCRIPT:\n")
    print(f'  "{story_hook}"\n')
    print(f"{'─'*60}")

    # ── INTERACTIVE HALT: CAPTURE YOUTUBE LINK ────────────────────────────────
    raw_yt_input = input("\n  ➔ Paste YouTube Link or 11-char ID here when finished: ").strip()

    if not raw_yt_input:
        print("  [!] No input received. Skipping video embed and proceeding with placeholder.")
        youtube_id = ""
    else:
        youtube_id = _extract_youtube_id(raw_yt_input)
        print(f"\n  [*] Isolated clean YouTube ID: '{youtube_id}'")

    # ── PHASE 2: REBUILD WITH VIDEO + DB SYNC + FINAL PUSH ───────────────────
    print("\n  [PHASE 2] Compiling final production asset with video embed...")

    final_html = _build_html(
        firm_name=firm_name, url_slug=url_slug,
        aum_growth_pct=aum_growth_pct, aum_per_advisor=aum_per_advisor,
        avg_client_size=avg_client_size, hnw_pct=hnw_pct,
        aum_data_points=aum_data_points, hnw_data_points=hnw_data_points,
        inferences_clean=inferences_clean, gaps_clean=gaps_clean,
        youtube_id=youtube_id if youtube_id else None
    )
    with open(destination, "w", encoding="utf-8") as fh:
        fh.write(final_html)
    print(f"  [✔] Final HTML written: {url_slug}/index.html")

    # ── CRM PERSISTENCE ───────────────────────────────────────────────────────
    if _DB_SYNC_AVAILABLE:
        print("\n  [DB] Syncing to ADVantage PostgreSQL database...")
        try:
            firm_id = upsert_firm(
                crd=str(target_crd),
                firm_name=firm_name,
                website_url=website_url,
                url_slug=url_slug,
                propensity_index=propensity_index,
                aum_data_points=aum_data_points,
                advisor_count_2026=advisor_count_2026,
                total_clients_raw=total_clients_raw,
                aum_growth_pct=aum_growth_pct,
                hnw_pct=hnw_pct,
                advisor_aum_str=aum_per_advisor,
                avg_client_str=avg_client_size,
            )
            if firm_id:
                raw_response_payload = {
                    "computed_aum_growth_pct": aum_growth_pct,
                    "derived_hnw_concentration_pct": hnw_pct,
                    "formatted_advisor_efficiency": aum_per_advisor,
                    "formatted_avg_client_size": avg_client_size,
                    "aum_data_points_m": aum_data_points,
                    "hnw_data_points_m": hnw_data_points,
                    "financial_inferences": firm.get("financial_inferences", []),
                    "marketing_gaps": firm.get("marketing_gaps", []),
                    "website_url": website_url,
                }
                insert_insight(
                    firm_id=firm_id,
                    story_hook=story_hook,
                    capacity_diagnostics=inferences_clean,
                    positioning_audits=gaps_clean,
                    raw_response_payload=raw_response_payload,
                    youtube_embed_id=youtube_id,
                )
        except Exception as db_err:
            print(f"  [!] CRM sync error (non-blocking): {db_err}")
    else:
        print("  [i] DB sync module unavailable — skipping CRM persistence.")

    # ── FINAL GIT PUSH ────────────────────────────────────────────────────────
    _git_push(project_root, f"Automated ADVantage deploy: {url_slug}")

    print(f"\n{'[✔]':>5} SUCCESS — Production asset deployed on autopilot!")
    print(f"       Live URL: {live_url}")
    print("\n" + "═" * 75)
    print(f"\n{'='*75}\n")


def _git_push(root_path, commit_message):
    """Execute git add / commit / push from the project root."""
    original_dir = os.getcwd()
    try:
        os.chdir(root_path)
        subprocess.run("git add .", shell=True, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(
            f'git commit --allow-empty -m "{commit_message}"',
            shell=True, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        result = subprocess.run(
            "git push origin main", shell=True,
            capture_output=True, text=True
        )
        os.chdir(original_dir)
        if result.returncode != 0:
            print(f"  [!] Git push failed:")
            print(f"      stdout: {result.stdout.strip()}")
            print(f"      stderr: {result.stderr.strip()}")
        else:
            print(f"  [✔] Git: '{commit_message}'")
    except subprocess.CalledProcessError as e:
        print(f"  [!] Git add/commit failed: {e}")
        os.chdir(original_dir)
    except Exception as e:
        print(f"  [!] Git push exception: {e}")
        os.chdir(original_dir)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_landing_page(sys.argv[1])
