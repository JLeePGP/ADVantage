"""
ADVantage Presentation Layer -- lp_generator.py (Directory-Based Deploy Engine)
===============================================================================
Precision Growth Partners | Agentic ABM Infrastructure
"""

import os
import json
import sys
import subprocess
import re
import shutil
from pathlib import Path

current_script_dir = Path(__file__).resolve().parent
project_root = current_script_dir.parent
INPUT_JSON = project_root / "data" / "output" / "financial_profiles.json"
CONFIG_PATH = project_root / "advantage_config.json"

def generate_landing_page(target_crd):
    """
    Transforms true multi-agent outputs into an index.html file housed inside 
    a custom firm-named folder at the repository root level.
    """
    print("=" * 75)
    print(f" 🎨 PROJECT ADVANTAGE — COMMITTING DIRECTORY TREE GENERATION")
    print("=" * 75)
    
    if not CONFIG_PATH.exists():
        print("[!] ERROR: advantage_config.json missing from workspace.")
        return
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    if not INPUT_JSON.exists():
        print(f"[!] ERROR: Base file missing at {INPUT_JSON}. Run math_processor first.")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        profiles = json.load(f)
        
    if str(target_crd) not in profiles:
        print(f" [!] CRD #{target_crd} not found inside working memory registers.")
        return
        
    firm = profiles[str(target_crd)]
    
    identity = firm.get("identity", {})
    derived = firm.get("derived_metrics", {})
    history = firm.get("history", {})
    
    firm_name = identity.get("firm_name", "Your Practice").strip()
    
    inferences = firm.get("financial_inferences", [])
    gaps = firm.get("marketing_gaps", [])
    story_hook = firm.get("story_hook", "")

    if not inferences or not gaps or not story_hook:
        print(f"[!] ERROR: Missing agent states for CRD #{target_crd}. Run main.py stages 1-3 first.")
        return

    # SLUG GENERATION: Turn "IKE CAPITAL, LLC" into "ike-capital"
    raw_name = identity.get("firm_name", "your-practice").strip().lower()
    for extension in ["llc", "l.l.c.", "inc.", "inc", "corp", "co.", "limited", "ltd.", "ltd"]:
        if raw_name.endswith(extension):
            raw_name = raw_name.rsplit(extension, 1)[0].strip()
    url_slug = re.sub(r'[^a-z0-9]+', '-', raw_name).strip('-')

    # 🌟 FILE POSITION RESOLUTION: Root Folder / {url_slug} / index.html
    firm_folder_path = project_root / url_slug
    os.makedirs(firm_folder_path, exist_ok=True)
    
    # Place the layout file cleanly inside as index.html
    destination_path = firm_folder_path / "index.html"
    print(f" -> System check: Creating directory structure at: {firm_folder_path.name}/index.html")

    # 🌟 NEW DEFENSIVE DATA PIPELINE FOR HNW SNAPSHOTS & CLEAN METRICS
    years_5 = ["2022", "2023", "2024", "2025", "2026"]
    aum_by_year_dict = derived.get("aum_by_year_m", {})
    aum_data_points = [round(aum_by_year_dict.get(yr, 0.0)) for yr in years_5]
    
    hnw_data_points = []
    for yr in years_5:
        yr_data = history.get(yr, {}) or history.get(int(yr), {})
        
        # 1. Look for direct raw or scaled HNW values
        hnw_raw = yr_data.get("hnw_aum_raw") or yr_data.get("hnw_aum") or yr_data.get("hnw_assets", 0.0)
        
        try:
            hnw_val = float(hnw_raw)
        except (ValueError, TypeError):
            hnw_val = 0.0
            
        # 2. Dynamic Calculation Fallback: Compute if direct value is missing
        if hnw_val == 0.0:
            ratio = yr_data.get("hnw_dependency_ratio") or yr_data.get("hnw_pct") or derived.get("hnw_dependency_by_year", {}).get(yr, 0.0)
            try:
                float_ratio = float(ratio)
                if float_ratio > 1.0:
                    float_ratio = float_ratio / 100.0
                
                total_aum_m = aum_by_year_dict.get(yr, 0.0)
                hnw_val = total_aum_m * float_ratio * 1e6
            except (ValueError, TypeError):
                hnw_val = 0.0

        if hnw_val > 1e4:
            hnw_data_points.append(round(hnw_val / 1e6))
        else:
            hnw_data_points.append(round(hnw_val))

    # Metric Snapshot Calculations
    f26 = history.get("2026", history.get(2026, {})) or {}
    aum_start = aum_by_year_dict.get(years_5[0], 0.0)
    aum_end = aum_by_year_dict.get(years_5[-1], 0.0)
    aum_growth_pct = round(((aum_end - aum_start) / aum_start) * 100) if aum_start > 0 else 0
    
    # Unified 2026 HNW Percentage Metric Snapshot Box calculation
    hnw_ratio_raw = f26.get("hnw_dependency_ratio") or f26.get("hnw_pct") or derived.get("hnw_dependency_by_year", {}).get("2026", 0.0)
    try:
        hnw_float = float(hnw_ratio_raw)
        if hnw_float < 1.0 and hnw_float > 0:
            hnw_pct = round(hnw_float * 100)
        else:
            hnw_pct = round(hnw_float)
    except (ValueError, TypeError):
        if aum_data_points[-1] > 0:
            hnw_pct = round((hnw_data_points[-1] / aum_data_points[-1]) * 100)
        else:
            hnw_pct = 0

    aum_per_advisor = f"${round(f26.get('aum_per_advisor', 0) / 1e6)}M" if f26.get('aum_per_advisor', 0) else "N/A"
    
    # 🌟 FIXED AVERAGE CLIENT SIZE FORMATTER: Dropped /1e3 division and 'K' suffix
    raw_avg_size = f26.get('avg_account_size', 0) or f26.get('avg_client_size', 0)
    avg_client_size = f"${round(raw_avg_size):,}" if raw_avg_size else "N/A"

    # HTML Template Layout
    html_template = f"""<!DOCTYPE html>
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
            <p class="text-sm sm:text-md text-[#bf8660] font-medium tracking-wide uppercase">We studied 5 years of your firm's data. Here's what we found.</p>
        </div>
    </header>

    <main class="max-w-4xl w-full mx-auto px-6 py-10 flex-1 space-y-10">
        
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

        <section class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            <div class="bg-[#242424] border border-[#4a4a4a]/40 p-6 rounded-xl relative shadow-xl">
                <h4 class="text-xs font-bold uppercase tracking-wider text-white border-b border-[#4a4a4a]/30 pb-3 mb-4 flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-[#bf8660]"></span> Capacity Diagnostics
                </h4>
                <ul class="space-y-3">
                    <li class="text-xs text-slate-300 leading-relaxed flex gap-2 font-light">
                        <span class="text-[#bf8660] font-mono">•</span> <span>{inferences[0]}</span>
                    </li>
                    <li class="text-xs text-slate-300 leading-relaxed flex gap-2 font-light">
                        <span class="text-[#bf8660] font-mono">•</span> <span>{inferences[1]}</span>
                    </li>
                    <li class="text-xs text-slate-300 leading-relaxed flex gap-2 font-light">
                        <span class="text-[#bf8660] font-mono">•</span> <span>{inferences[2]}</span>
                    </li>
                </ul>
            </div>

            <div class="bg-[#242424] border border-[#4a4a4a]/40 p-6 rounded-xl relative shadow-xl">
                <h4 class="text-xs font-bold uppercase tracking-wider text-white border-b border-[#4a4a4a]/30 pb-3 mb-4 flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span> Positioning Audits
                </h4>
                <ul class="space-y-3">
                    <li class="text-xs text-slate-300 leading-relaxed flex gap-2 font-light">
                        <span class="text-slate-400 font-mono">•</span> <span>{gaps[0]}</span>
                    </li>
                    <li class="text-xs text-slate-300 leading-relaxed flex gap-2 font-light">
                        <span class="text-slate-400 font-mono">•</span> <span>{gaps[1]}</span>
                    </li>
                    <li class="text-xs text-slate-300 leading-relaxed flex gap-2 font-light">
                        <span class="text-slate-400 font-mono">•</span> <span>{gaps[2]}</span>
                    </li>
                </ul>
            </div>
        </section>

        <div class="text-center pt-4 max-w-2xl mx-auto space-y-4">
            <a href="https://calendly.com/precisiongrowthpartners/adv-discovery-call" 
               target="_blank"
               class="inline-block bg-[#bf8660] text-white font-bold text-md px-10 py-4 rounded-xl transition-all hover:bg-black shadow-lg shadow-brand-copper/10">
                Book a 15-min Discovery Call
            </a>
        </div>

    </main>

    <footer class="w-full border-t border-[#4a4a4a]/30 bg-[#2b2b2b] py-8 text-center px-6 space-y-2">
        <p class="text-xs text-slate-400 font-light tracking-wide">Secure PGP Protected ADVantage Array Engine</p>
        <p class="text-[10px] text-slate-500 max-w-2xl mx-auto leading-normal font-light">
            Analysis built natively using verified, publicly accessible SEC Form ADV Part 1A filings historical dataset matrices (2022–2026).
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
</html>
"""
    
    # Write the index file into the newly targeted nested folder location
    with open(destination_path, "w", encoding="utf-8") as fh:
        fh.write(html_template)
    print(f" -> Compiled dynamic layout layout safely: {url_slug}/index.html")

    # ── AUTOMATED DEPLOYMENT PUSH TO GITHUB/NETLIFY ───────────────────────
    print("  Syncing incremental directory tree to GitHub repository...")
    try:
        script_dir = os.getcwd()
        os.chdir(project_root)
        
        # Execute automated Git command sequence natively
        subprocess.run("git add .", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(f'git commit --allow-empty -m "Automated ADVantage deploy: {url_slug}"', shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("git push origin main", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        os.chdir(script_dir)

        site_verification = config.get('NETLIFY_SITE_ID', 'unlinked')
        
        print(f"\n[✔] SUCCESS: Custom telemetry array deployed on complete autopilot!")
        print(f"    Live Secure URL: https://advantage.precisiongrowthpartners.io/{url_slug}")
        print("\n" + "═"*75)
        print(" 🎙️ INTERNAL OPERATOR BRIEFING SCRIPT (READ TO PROSPECT / JUDGES):")
        print("═"*75)
        print(f'\n "{story_hook}" \n')
        print("═"*75 + "\n") 
    except subprocess.CalledProcessError as e:
        print(f"  [!] Git command failed to execute natively: {str(e)}")
        os.chdir(script_dir)
    except Exception as e:
        print(f"  [!] Git deployment pipeline encountered an exception: {str(e)}")
        os.chdir(script_dir)
        
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_landing_page(sys.argv[1])