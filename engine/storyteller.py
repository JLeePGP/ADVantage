import os
import json
import sys
from pathlib import Path
from anthropic import Anthropic

# ── CONFIGURATION & API PATH RESOLUTION ─────────────────────────────────────
current_script_dir = Path(__file__).resolve().parent
project_root = current_script_dir.parent

config_path = project_root / "advantage_config.json"

if config_path.exists():
    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"[!] CONFIG PARSING ERROR: Your JSON file is malformed. Details: {str(e)}")
        sys.exit(1)
else:
    print(f"[!] CONFIG TARGET ERROR: Could not locate 'advantage_config.json' at {config_path.resolve()}")
    sys.exit(1)

IF_KEY = config_data.get("CLAUDE_ADV_API_KEY")
if not IF_KEY:
    print("[!] ERROR: 'CLAUDE_ADV_API_KEY' key not found inside your advantage_config.json file.")
    sys.exit(1)

client = Anthropic(api_key=IF_KEY)
INPUT_JSON = "data/output/financial_profiles.json"

# ── AGENTIC STORYTELLING SYNTHESIS FUNCTION ──────────────────────────────────
def synthesize_storyline(firm_name, financial_inferences, marketing_gaps):
    """Fuses diagnostic data loops into a single hyper-compelling outreach hook and structured page copy."""
    
    system_instruction = (
        "You are an elite, highly persuasive sales engineer and executive speechwriter for a premium "
        "growth acceleration agency targeting Registered Investment Advisors (RIAs).\n\n"
        "Your job is to take raw operational pain points and marketing gaps, and transform them into "
        "a highly intentional presentation narrative that makes the prospect feel validated, intrigued, and empowered.\n\n"
        "CRITICAL OUTPUT FORMAT CRITERIA:\n"
        "You must return your output STRICTLY as a raw JSON object with exactly three root keys. Do not include markdown blocks, backticks (e.g., no ```json), or wrapping text. Return raw JSON text only.\n\n"
        "THE JSON SCHEMA:\n"
        "{\n"
        '  "story_hook": "A single masterfully crafted narrative string designed as an internal operator speech script.",\n'
        '  "capacity_diagnostics": [\n'
        "    {\n"
        '      "headline": "A 2-3 word confident headline (e.g., Scale Horizon, Asset Velocity)",\n'
        '      "insight": "A single sentence acknowledging or validating their operational foundation/current state.",\n'
        '      "opportunity": "A single sentence framing how optimizing this specific element unlocks their next growth horizon."\n'
        "    }\n"
        "  ],\n"
        '  "positioning_audits": [\n'
        "    {\n"
        '      "headline": "A 2-3 word brand positioning headline (e.g., Market Differentiation, Value Clarity)",\n'
        '      "insight": "A single sentence identifying an exact positioning gap or message mismatch on their site.",\n'
        '      "opportunity": "A single sentence framing how sharpening this message elevates their profile to premium clients."\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "CRITICAL WRITING CONTRAINTS:\n"
        "1. Generate EXACTLY 3 items for 'capacity_diagnostics' and EXACTLY 3 items for 'positioning_audits'.\n"
        "2. Avoid blunt, defensive, or overly aggressive AI phrasing. The tone must be strategic, elite, welcoming, and collaborative.\n"
        "3. Every single 'insight' must feel respectful of what they've built, and every 'opportunity' must feel deeply inspiring."
    )
    
    user_context = (
        f"Firm Name: {firm_name}\n\n"
        f"Raw Financial Trajectory Pain Points:\n{json.dumps(financial_inferences, indent=2)}\n\n"
        f"Raw Website Positioning Gaps:\n{json.dumps(marketing_gaps, indent=2)}"
    )
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000, # Increased slightly to accommodate structured lists
            temperature=0.4,
            system=system_instruction,
            messages=[
                {"role": "user", "content": user_context}
            ]
        )
        raw_text = response.content[0].text.strip()
        return json.loads(raw_text)
    except Exception as e:
        print(f"    [!] Storyteller Agent loop failure: {str(e)}")
        return None

# ── RUNTIME EXECUTION DISPATCHER ───────────────────────────────────────────
def build_personalized_story(target_crd):
    json_absolute_path = project_root / INPUT_JSON
    if not json_absolute_path.exists():
        print(f" [!] ERROR: Data baseline profile file missing.")
        return

    with open(json_absolute_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)
        
    if str(target_crd) not in profiles:
        print(f" [!] CRD #{target_crd} not found inside the active data vault profiles.")
        return
        
    firm_payload = profiles[str(target_crd)]
    
    firm_name = firm_payload.get("identity", {}).get("firm_name", "Your Practice")
    fin_inf = firm_payload.get("financial_inferences")
    mkt_gaps = firm_payload.get("marketing_gaps")
    
    if not fin_inf or not mkt_gaps:
        print(" [!] CANCELLED: Missing required insights from Stage 1 or Stage 2 agents.")
        print(f"     Has financial_inferences? {bool(fin_inf)} | Has marketing_gaps? {bool(mkt_gaps)}")
        return
        
    print(f" -> Synthesizing insights for: {firm_name}")
    print(" -> Engineering personalized hook via Claude Sonnet...")
    
    story_results = synthesize_storyline(firm_name, fin_inf, mkt_gaps)
    
    if story_results and "story_hook" in story_results:
        # Save the polished structured copy straight into the database dictionary
        profiles[str(target_crd)]["story_hook"] = story_results.get("story_hook")
        profiles[str(target_crd)]["capacity_diagnostics_clean"] = story_results.get("capacity_diagnostics", [])
        profiles[str(target_crd)]["positioning_audits_clean"] = story_results.get("positioning_audits", [])
        
        with open(json_absolute_path, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2)
            
        print("\n[✔] STAGE 3 SUCCESSFUL: Polished copy metrics saved to master database record.")
        print("-" * 75)
        print(story_results["story_hook"])
        print("-" * 75)
    else:
        print(" [!] Execution broken. AI narrative synthesis error.")