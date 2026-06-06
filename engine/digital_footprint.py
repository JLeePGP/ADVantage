import os
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from anthropic import Anthropic

current_script_dir = Path(__file__).resolve().parent
project_root = current_script_dir.parent
config_path = project_root / "advantage_config.json"

with open(config_path, "r") as f:
    config_data = json.load(f)

IF_KEY = config_data.get("CLAUDE_ADV_API_KEY")
client = Anthropic(api_key=IF_KEY)
INPUT_JSON = "data/output/financial_profiles.json"

def scrape_website_with_jina(url):
    """Uses Jina AI's Reader API with character sanitation filters."""
    if not url:
        return None
    
    # Absolute cleaning of text string properties
    url_str = str(url).strip().replace(" ", "")
    url_str = url_str.replace("https://", "").replace("http://", "")
    url_str = url_str.replace("HTTP://", "").replace("HTTPS://", "")
    url_str = url_str.strip("/")
    
    # Strip any accidental brackets or characters remaining from dataframe splits
    url_str = re.sub(r'[\[\]\'\"]', '', url_str)
    
    clean_target_url = "https://" + url_str
    # URL encode the target path component to secure standard url formats
    jina_endpoint = f"https://r.jina.ai/{clean_target_url}"
    print(f" -> Contacting Jina AI to scrape: {clean_target_url}")
    
    try:
        req = urllib.request.Request(
            jina_endpoint, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"    [!] Jina AI scrape failed: {str(e)}")
        return None

def get_marketing_analysis(web_markdown):
    system_instruction = (
        "You are an elite brand strategist targeting financial advisors.\n"
        "Identify exactly 3 distinct website messaging gaps or positioning flaws.\n\n"
        "CRITICAL RULES:\n"
        "1. Return your output STRICTLY as a JSON object with a root key called 'marketing_gaps' containing an array of exactly 3 strings.\n"
        "2. No markdown blocks or trailing notes."
    )
    user_context = f"Web contents:\n\n{web_markdown[:10000]}"
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            temperature=0.3,
            system=system_instruction,
            messages=[{"role": "user", "content": user_context}]
        )
        raw_text = response.content[0].text.strip()
        
        import re
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0).replace('\n', ' '))
            
        return json.loads(raw_text)
    except Exception as e:
        print(f"    [!] Stage 2 Agent loop failure: {str(e)}")
        return None

def analyze_digital_footprint(target_crd):
    json_absolute_path = project_root / INPUT_JSON
    with open(json_absolute_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)
        
    if str(target_crd) not in profiles:
        print(f" [!] CRD #{target_crd} not found inside the profiles mapping database.")
        return
        
    firm_payload = profiles[str(target_crd)]
    url = firm_payload.get("identity", {}).get("website_URL")
    
    scraped_text = scrape_website_with_jina(url)
    if not scraped_text or len(scraped_text.strip()) < 100:
        print(" [!] ERROR: Empty or unreadable web data stream return layout.")
        return
        
    print(" -> Data parsed. Generating positioning audit...")
    analysis_results = get_marketing_analysis(scraped_text)
    
    if analysis_results and "marketing_gaps" in analysis_results:
        profiles[str(target_crd)]["marketing_gaps"] = analysis_results["marketing_gaps"]
        with open(json_absolute_path, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2)
        print("[✔] STAGE 2 SUCCESSFUL: Brand marketing gaps saved.")
    else:
        print(" [!] Stage 2 execution structural error.")

import re
if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_digital_footprint(sys.argv[1])