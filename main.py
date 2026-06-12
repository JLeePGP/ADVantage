import os
import sys
import json
from pathlib import Path

# Import your validated multi-agent execution steps from the engine module
from engine.financial_analyst import analyze_single_crd
from engine.digital_footprint import analyze_digital_footprint
from engine.storyteller import build_personalized_story

# 🌟 NEW INTEGRATION HOOK: Connect your GitHub/Netlify publishing pipeline module
from engine.lp_generator import generate_landing_page

# Pure JSON pathing metrics resolution
project_root = Path(__file__).resolve().parent
INPUT_JSON = project_root / "data" / "output" / "financial_profiles.json"
TOP_100_JSON = project_root / "data" / "output" / "prospects_top100.json"

def run_agentic_pipeline(crd_number):
    """Executes the sequential cognitive stack for a single target firm."""
    crd_str = str(crd_number).strip()
    
    print("\n" + "="*80)
    print(f" 🚀 PROJECT ADVANTAGE — ENGAGING AUTOMATED AGENT CONSOLE")
    print(f" TARGET REGULATORY IDENTIFIER: CRD #{crd_str}")
    print("="*80 + "\n")
    
    # Stage 1: Financial Analysis Trajectory Tracking
    print("[STAGE 1/4] Activating Sovereign Financial Analyst Agent...")
    analyze_single_crd(crd_str)
    print("\n" + "-"*50 + "\n")
    
    # Stage 2: Public Footprint Scraper Audit
    print("[STAGE 2/4] Activating Digital Footprint Scraper Agent...")
    stage2_result = analyze_digital_footprint(crd_str)
    print("\n" + "-"*50 + "\n")

    if stage2_result is False:
        print("[i] Pipeline halted at Stage 2. Returning to Command Console.")
        return
    
    # Stage 3: Narrative Synthesis Copywriting Block
    print("[STAGE 3/4] Activating Orchestrator Storyteller Agent...")
    build_personalized_story(crd_str)
    print("\n" + "-"*50 + "\n")
    
    # 🌟 NEW PIPELINE STEP: Stage 4 Landing Page Generation & GitHub Deploy Push
    print("[STAGE 4/4] Activating Autopilot Web Presentation Builder...")
    generate_landing_page(crd_str)
    
    print("\n" + "="*80)
    print(f" 🎉 AGENTIC INFRASTRUCTURE CONVERGED FOR CRD #{crd_str}")
    print(" Operational memory updated, files synced, and live links updated.")
    print("="*80 + "\n")

def launch_command_console():
    print("\n==================================================")
    print("  PROJECT ADVANTAGE // OPERATIONAL COMMAND CONSOLE   ")
    print("==================================================")
    print("  • Type a list number to select a pipeline firm.")
    print("  • Type '#' followed by any CRD (e.g., #299405) for wildcards.")
    print("  • Press ENTER with no input to view the next page.")
    print("==================================================")

    # Validate infrastructure states cleanly
    if not TOP_100_JSON.exists() or not INPUT_JSON.exists():
        print(f"[!] SYSTEM ERROR: Required JSON storage cache files are missing.")
        print(f"    Please run: python engine/math_processor.py first to compile logs.")
        return

    # Load our processed high-propensity targets priority JSON loop
    with open(TOP_100_JSON, "r", encoding="utf-8") as f:
        top100_data = json.load(f)
        
    # Convert dict items to an indexable list for clean pagination loops
    pipeline_list = list(top100_data.values())
    total_firms = len(pipeline_list)
    
    current_row = 0
    page_size = 10

    while True:
        end_row = min(current_row + page_size, total_firms)
        print(f"\n--- PRIORITIZED PIPELINE (Firms {current_row + 1} to {end_row} of {total_firms}) ---")
        
        for i in range(current_row, end_row):
            firm = pipeline_list[i]
            identity = firm.get("identity", {})
            scoring = firm.get("scoring", {})
            print(f"  [{i + 1}] Score: {scoring.get('composite_score', 'N/A')} | PI: {scoring.get('propensity_index', 0):+d} | {identity.get('firm_name')[:50]}")
        
        print("──────────────────────────────────────────────────")
        user_selection = input("  ➔ Select [Number], enter [#CRD], or press [ENTER] for next page: ").strip()

        # Case 1: Paginate Forward
        if not user_selection:
            current_row += page_size
            if current_row >= total_firms:
                print("\n  [i] Reached the end of your prioritized prospects. Looping to top.")
                current_row = 0
            continue

        # Case 2: Master Vault Wildcard Lookup Override
        if user_selection.startswith("#"):
            target_crd = user_selection.replace("#", "").strip()
            print(f"\n[!] Vault Override Detected. Locating target metadata for CRD: {target_crd}...")
            
            with open(INPUT_JSON, "r", encoding="utf-8") as f:
                master_vault = json.load(f)
                
            if target_crd in master_vault:
                run_agentic_pipeline(target_crd)
                input("\n[➔] Press ENTER to return to the Command Console...")
                continue
            else:
                print(f"  [!] Error: CRD '{target_crd}' is not registered anywhere inside your master JSON registry.")
                continue

        # Case 3: Standard Numerical Menu Selection
        if user_selection.isdigit():
            val = int(user_selection)
            if 1 <= val <= total_firms:
                selected_firm = pipeline_list[val - 1]
                target_crd = str(selected_firm["identity"]["crd_number"])
                
                run_agentic_pipeline(target_crd)
                input("\n[➔] Press ENTER to return to the Command Console...")
                continue
            else:
                print(f"  [!] Selection out of bounds. Enter an active number between 1 and {total_firms}.")
                continue
        else:
            print("  [!] Invalid entry. Pick an active menu index or look up via '#CRD_NUMBER'.")
            continue

if __name__ == "__main__":
    try:
        launch_command_console()
    except KeyboardInterrupt:
        print("\n\n[i] Shutting down Project ADVantage command systems safely. Goodbye.\n")
        sys.exit(0)