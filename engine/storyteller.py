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
def synthesize_storyline(firm_name, financial_inferences, marketing_gaps, derived_metrics=None):
    """Fuses diagnostic data and raw metrics into a structured operator briefing and LP copy."""

    system_instruction = (
        "You are a sharp financial analyst briefing a sales operator before they record a "
        "personalized outreach video for a Registered Investment Advisor (RIA).\n\n"
        "Your output is a REFERENCE BRIEFING — not a speech. The operator scans it in 60 seconds "
        "before hitting record, then speaks naturally. Every line must earn its place: data-backed, "
        "specific, and direct. No generic openers. No flattery. No scripted sentences.\n\n"
        "CRITICAL OUTPUT FORMAT CRITERIA:\n"
        "Return STRICTLY a raw JSON object with exactly three root keys. No markdown, no backticks, "
        "no wrapping text. Raw JSON only.\n\n"
        "THE JSON SCHEMA:\n"
        "{\n"
        '  "story_hook": "Multi-line operator briefing. Use EXACTLY this section structure with literal \\n newlines:\\n\\n'
        "OPENING:\\n"
        "[One sentence — a specific, genuine compliment grounded in something real the firm has built or achieved. "
        "Must cite an actual data point or observable fact (e.g., sustained HNW concentration, consistent AUM growth, "
        "client retention implied by account size, team expansion). This is the first thing the operator says on camera. "
        "It must feel earned — no generic praise.]\\n\\n"
        "KEY METRICS:\\n"
        "• [metric label]: [value in most recent year] ([direction + magnitude vs. earliest year with specific numbers])\\n"
        "• [repeat for 3-4 most diagnostic metrics]\\n\\n"
        "INSIGHT INTERSECTIONS:\\n"
        "• [Cross-reference 2+ data points that together tell one story — e.g., advisor headcount grew X% while AUM/advisor fell Y%, "
        "or HNW concentration dropped Z points as client count expanded. Each bullet must name both data points and the tension between them.]\\n"
        "• [second intersection]\\n\\n"
        "TALKING POINTS:\\n"
        "1. [2-3 word label] — [one punchy sentence: what the number shows and why it matters to their growth]\\n"
        "2. [2-3 word label] — [same]\\n"
        "3. [2-3 word label] — [same]\\n\\n"
        "DIGITAL GAPS:\\n"
        '• [gap observed on site] — [specific consequence for client acquisition or positioning]\\n",\n'
        '  "capacity_diagnostics": [\n'
        "    {\n"
        '      "headline": "2-3 word headline grounded in a specific metric trend",\n'
        '      "insight": "One sentence stating what the data shows — cite at least one specific number or year-over-year change.",\n'
        '      "opportunity": "One sentence on the specific lever that addresses this — concrete, not inspirational."\n'
        "    }\n"
        "  ],\n"
        '  "positioning_audits": [\n'
        "    {\n"
        '      "headline": "2-3 word headline tied to an observed site gap",\n'
        '      "insight": "One sentence naming the exact gap or mismatch on their site.",\n'
        '      "opportunity": "One sentence on what closing that gap unlocks — tied to their client profile or AUM stage."\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "STORY_HOOK RULES:\n"
        "1. OPENING must reference one specific, verifiable positive — a sustained metric, a milestone, a visible strength in the data. "
        "No platitudes ('you've built something incredible'). One sentence, then move on.\n"
        "2. Every KEY METRICS bullet must cite specific numbers (dollar amounts, percentages, year labels).\n"
        "3. INSIGHT INTERSECTIONS must connect two or more data points that amplify the same underlying problem — "
        "look for dilution signals, concentration erosion, growth/revenue mismatches, headcount vs. asset divergence.\n"
        "4. TALKING POINTS are ammunition for the operator — direct and memorable, not scripted. "
        "Give them something to say, not something to read.\n"
        "5. Do not use the firm name in the OPENING. Do not use greeting phrases.\n"
        "6. Tone is analytical and confident — peer-to-peer, not pitch-to-prospect.\n\n"
        "CAPACITY_DIAGNOSTICS & POSITIONING_AUDITS RULES:\n"
        "1. Generate EXACTLY 3 items for each.\n"
        "2. Every insight must reference a specific observable — a metric, a trend, or a site element. No vague statements.\n"
        "3. Opportunities must be specific actions or pivots, not abstract aspirations."
    )

    metrics_block = (
        f"\nRaw Year-by-Year Metrics:\n{json.dumps(derived_metrics, indent=2)}\n"
        if derived_metrics else ""
    )

    user_context = (
        f"Firm Name: {firm_name}\n"
        f"{metrics_block}\n"
        f"Financial Trajectory Pain Points:\n{json.dumps(financial_inferences, indent=2)}\n\n"
        f"Website Positioning Gaps:\n{json.dumps(marketing_gaps, indent=2)}"
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
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
    derived_metrics = firm_payload.get("derived_metrics")

    if not fin_inf or not mkt_gaps:
        print(" [!] CANCELLED: Missing required insights from Stage 1 or Stage 2 agents.")
        print(f"     Has financial_inferences? {bool(fin_inf)} | Has marketing_gaps? {bool(mkt_gaps)}")
        return

    print(f" -> Synthesizing insights for: {firm_name}")
    print(" -> Engineering briefing script via Claude Sonnet...")

    story_results = synthesize_storyline(firm_name, fin_inf, mkt_gaps, derived_metrics)
    
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