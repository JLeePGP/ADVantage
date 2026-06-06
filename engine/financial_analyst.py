import os
import json
import sys
import re
from pathlib import Path
from anthropic import Anthropic

# ── CONFIGURATION & API PATH RESOLUTION ─────────────────────────────────────
current_script_dir = Path(__file__).resolve().parent
project_root = current_script_dir.parent
config_path = project_root / "advantage_config.json"

if config_path.exists():
    with open(config_path, "r") as f:
        config_data = json.load(f)
else:
    print("[!] Configuration file missing.")
    sys.exit(1)

IF_KEY = config_data.get("CLAUDE_ADV_API_KEY")
client = Anthropic(api_key=IF_KEY)
INPUT_JSON = "data/output/financial_profiles.json"

def get_sovereign_analysis(firm_data):
    system_instruction = (
        "You are an elite B2B wealth-management growth consultant.\n"
        "Review the 5-year data vectors and infer exactly 3 distinct operational pain points.\n\n"
        "CRITICAL RULES:\n"
        "1. Return your output STRICTLY as a JSON object with a single root key called 'financial_inferences' containing an array of exactly 3 strings.\n"
        "2. Avoid any markdown blocks or formatting backticks. Return raw JSON text only.\n"
        "3. Ensure the array elements are clean strings with no literal newlines inside the quotes."
    )
    
    user_context = f"Profile payload:\n{json.dumps(firm_data)}"
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6", 
            max_tokens=800,
            temperature=0.3,
            system=system_instruction,
            messages=[{"role": "user", "content": user_context}]
        )
        raw_text = response.content[0].text.strip()
        
        # Robust regex fallback extraction to clean up trailing text or markdown backticks
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            clean_json_str = match.group(0)
            # Normalize internal newlines inside strings that choke json.loads()
            clean_json_str = clean_json_str.replace('\n', ' ').replace('\r', '')
            return json.loads(clean_json_str)
            
        return json.loads(raw_text)
    except Exception as e:
        print(f"    [!] Stage 1 Agent loop failure: {str(e)}")
        return None

def analyze_single_crd(target_crd):
    json_absolute_path = project_root / INPUT_JSON
    with open(json_absolute_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)
        
    if str(target_crd) not in profiles:
        print(f" [!] CRD #{target_crd} not found inside the active data vault.")
        return
        
    firm_payload = profiles[str(target_crd)]
    print(f" -> Extracting trajectory markers for: {firm_payload.get('identity', {}).get('firm_name')}")
    
    analysis_context = {
        "derived_metrics": firm_payload.get("derived_metrics", {}),
        "history": firm_payload.get("history", {})
    }
    
    analysis_results = get_sovereign_analysis(analysis_context)
    
    if analysis_results and "financial_inferences" in analysis_results:
        profiles[str(target_crd)]["financial_inferences"] = analysis_results["financial_inferences"]
        with open(json_absolute_path, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2)
        print("[✔] STAGE 1 SUCCESSFUL: Financial inferences saved.")
    else:
        print(" [!] Stage 1 analytical runtime error.")

if __name__ == "__main__":
    # Test execution block to verify Stage 1 on your exact target firm
    if len(sys.argv) > 1:
        analyze_single_crd(sys.argv[1])