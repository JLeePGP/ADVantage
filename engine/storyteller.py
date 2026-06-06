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
    """Fuses diagnostic data loops into a single hyper-compelling outreach hook."""
    
    system_instruction = (
        "You are an elite, highly persuasive sales engineer and executive speechwriter for a premium "
        "growth acceleration agency targeting Registered Investment Advisors (RIAs).\n\n"
        "Your job is to look at a firm's operational pain points and marketing gaps, and combine them "
        "into a single masterly crafted narrative hook designed to immediately capture a founder's attention.\n\n"
        "CRITICAL CRITERIA:\n"
        "1. Return your output strictly as a JSON object with a single root key called 'story_hook' containing a string.\n"
        "2. Do not include markdown blocks, backticks (e.g., no ```json), or wrapping text. Return raw JSON text only.\n"
        "3. Tone: Bold, deeply strategic, challenging, yet highly professional. Avoid generic marketing hype or sales clichés.\n"
        "4. Your narrative must bridge the gap between their real metrics (e.g., advisor burnout) and their website messaging blindspots."
    )
    
    user_context = (
        f"Firm Name: {firm_name}\n\n"
        f"Financial Trajectory Pain Points:\n{json.dumps(financial_inferences, indent=2)}\n\n"
        f"Website Positioning Gaps:\n{json.dumps(marketing_gaps, indent=2)}"
    )
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
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
        profiles[str(target_crd)]["story_hook"] = story_results["story_hook"]
        
        with open(json_absolute_path, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2)
            
        print("\n[✔] STAGE 3 SUCCESSFUL: Unified narrative saved to master database record.")
        print("-" * 75)
        print(story_results["story_hook"])
        print("-" * 75)
    else:
        print(" [!] Execution broken. AI narrative synthesis error.")