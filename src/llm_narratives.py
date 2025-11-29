import os
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI


# 0) Setup paths & OpenAI client

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SCENARIO_PATH = RESULTS_DIR / "llm_scenarios.json"
OUT_JSONL = RESULTS_DIR / "llm_narratives.jsonl"
OUT_JSON = RESULTS_DIR / "llm_narratives.json"


# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in environment or .env file.")

client = OpenAI(api_key=OPENAI_API_KEY)

# Allow overriding model via env; default to a strong but affordable model
llm_model = os.getenv("LLM_MODEL", "gpt-4.1-mini")


# 1) Utilities

def load_scenarios(path: Path) -> List[Dict[str, Any]]:
    """Load the llm_scenarios.json file."""
    if not path.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("llm_scenarios.json must contain a list of scenario records.")
    return data


def find_baseline(scenarios: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Return the baseline scenario record, if present."""
    for s in scenarios:
        if s.get("family") == "baseline" or s.get("scenario") == "baseline_actual":
            return s
    return None



def format_macro_block(macro: Dict[str, Any]) -> str:
    """
    Turn macro dict into a short text block for the prompt.
    Only include keys that exist; keep order roughly macro → labor → prices → rates.
    """
    if not macro:
        return "Macro inputs: not provided for this scenario."

    # Friendly labels for common macro variables
    label_map = {
        "GDPC1": "Real GDP level",
        "UNRATE": "Unemployment rate",
        "CPIAUCSL": "Price level (CPI index)",
        "FEDFUNDS": "Policy rate (federal funds rate)",
        "GDPC1_delta_qoq": "Real GDP quarterly change",
        "UNRATE_delta_qoq": "Unemployment quarterly change",
        "CPIAUCSL_delta_qoq": "CPI quarterly change",
        "FEDFUNDS_delta_qoq": "Policy rate quarterly change",
        "inflation_qoq": "Quarterly inflation rate",
        "real_rate_qoq": "Real interest rate (approx.)",
    }

    # Order keys in a sensible way
    preferred_order = [
        "GDPC1",
        "GDPC1_delta_qoq",
        "UNRATE",
        "UNRATE_delta_qoq",
        "CPIAUCSL",
        "CPIAUCSL_delta_qoq",
        "inflation_qoq",
        "FEDFUNDS",
        "FEDFUNDS_delta_qoq",
        "real_rate_qoq",
    ]

    lines = []
    for key in preferred_order:
        if key in macro and macro[key] is not None:
            label = label_map.get(key, key)
            val = macro[key]
            # Format numbers nicely
            if isinstance(val, (int, float)):
                lines.append(f"- {label}: {val:.4f}")
            else:
                lines.append(f"- {label}: {val}")
    # Add any other leftover keys
    for key, val in macro.items():
        if key in preferred_order:
            continue
        if val is None:
            continue
        label = label_map.get(key, key)
        if isinstance(val, (int, float)):
            lines.append(f"- {label}: {val:.4f}")
        else:
            lines.append(f"- {label}: {val}")

    if not lines:
        return "Macro inputs: provided but not numeric / interpretable."
    return "Macro inputs:\n" + "\n".join(lines)



def format_risk_block(risk: Dict[str, Any]) -> str:
    """
    Turn risk dict into a short text block for the prompt.
    """
    if not risk:
        return "Risk metrics: not provided."

    def f(x: Any) -> str:
        if isinstance(x, (int, float)):
            return f"{x:.6f}"
        return str(x)

    lines = []
    for key in ["mean_pd", "p50_pd", "p90_pd", "p99_pd", "EL", "uplift_vs_baseline_pct", "EL_change_vs_baseline_pct"]:
        if key in risk and risk[key] is not None:
            if key == "uplift_vs_baseline_pct":
                label = "Change in PD vs baseline (%)"
            elif key == "EL_change_vs_baseline_pct":
                label = "Change in expected loss vs baseline (%)"
            elif key == "mean_pd":
                label = "Mean probability of default"
            elif key == "p50_pd":
                label = "Median PD (p50)"
            elif key == "p90_pd":
                label = "Tail PD (p90)"
            elif key == "p99_pd":
                label = "Extreme tail PD (p99)"
            elif key == "EL":
                label = "Expected loss (currency units)"
            else:
                label = key
            lines.append(f"- {label}: {f(risk[key])}")

    if not lines:
        return "Risk metrics: provided but empty."
    return "Risk metrics:\n" + "\n".join(lines)



def build_user_prompt(
    scenario: Dict[str, Any],
    baseline: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Construct a rich user prompt summarizing the scenario's macro + risk,
    plus the baseline for comparison (if available).
    """
    scen_name = scenario.get("scenario", "UNKNOWN_SCENARIO")
    family = scenario.get("family", "unknown_family")

    macro = scenario.get("macro", {}) or {}
    risk = scenario.get("risk", {}) or {}

    macro_text = format_macro_block(macro)
    risk_text = format_risk_block(risk)

    # Baseline info for comparison
    baseline_block = "No explicit baseline scenario was found."
    if baseline is not None and baseline is not scenario:
        base_macro = baseline.get("macro", {}) or {}
        base_risk = baseline.get("risk", {}) or {}
        base_macro_txt = format_macro_block(base_macro)
        base_risk_txt = format_risk_block(base_risk)
        base_name = baseline.get("scenario", "baseline")
        baseline_block = (
            f"Baseline scenario: {base_name}\n"
            f"{base_macro_txt}\n"
            f"{base_risk_txt}"
        )

    # High-level description of what we want from the LLM
    prompt = f"""
You are a senior financial risk officer at a large bank. You are reviewing a stress-testing scenario.

SCENARIO METADATA
- Scenario name: {scen_name}
- Scenario family/type: {family} (e.g. baseline, data_driven, Fed, GenAI)

CURRENT SCENARIO DETAILS
{macro_text}

{risk_text}

BASELINE REFERENCE (for comparison)
{baseline_block}

TASK
Write a clear, concise narrative describing this scenario in the style of a risk report for senior management.

Please:
1. Describe the macroeconomic environment (growth, labor market, inflation, interest rates).
2. Explain how this environment translates into credit risk (PD and expected loss) relative to baseline.
3. Highlight which risk drivers dominate the stress (e.g. unemployment, GDP collapse, rate shocks, inflation).
4. Comment on whether the scenario is mild, adverse, or severe compared with the baseline.
5. Suggest 2–3 high-level risk management or capital planning actions.

OUTPUT FORMAT
Return a single JSON object with the following fields:

- "scenario_name": string, same as above.
- "headline": one-sentence summary of the scenario.
- "macro_story": 3–5 sentences explaining the macro environment.
- "credit_risk_impact": 3–6 sentences linking macro conditions to PD and expected loss.
- "comparison_to_baseline": 2–4 sentences explicitly comparing to baseline risk.
- "key_risks": bullet-style text listing the main risk drivers.
- "management_actions": bullet-style text suggesting actions (capital, pricing, limits, monitoring).
- "tone": one of ["benign", "cautious", "adverse", "severe"].

Use simple, professional language suitable for a board-level risk report.
"""
    return prompt.strip()



def call_llm_for_scenario(
    scenario: Dict[str, Any],
    baseline: Optional[Dict[str, Any]],
    max_retries: int = 3,
    backoff_sec: float = 5.0,
) -> Dict[str, Any]:
    """
    Call OpenAI Chat Completions with JSON output for a single scenario.
    """
    scen_name = scenario.get("scenario", "UNKNOWN")
    user_prompt = build_user_prompt(scenario, baseline)

    for attempt in range(1, max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=llm_model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a financial risk analyst specialized in bank stress testing. "
                            "Always answer with a valid JSON object following the requested schema."
                        ),
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
            )
            content = resp.choices[0].message.content
            parsed = json.loads(content)

            # Ensure we always know which scenario this belongs to
            parsed.setdefault("scenario_name", scen_name)
            parsed["scenario_family"] = scenario.get("family", "unknown")
            return parsed

        except Exception as e:
            print(f"[{scen_name}] LLM call failed on attempt {attempt}: {e}")
            if attempt == max_retries:
                # Return a minimal error record instead of crashing the script
                return {
                    "scenario_name": scen_name,
                    "scenario_family": scenario.get("family", "unknown"),
                    "error": str(e),
                    "raw_output": None,
                }
            time.sleep(backoff_sec * attempt)


# 2) Main execution

def main() -> None:
    print(f"Loading scenarios from: {SCENARIO_PATH}")
    scenarios = load_scenarios(SCENARIO_PATH)
    print(f"Loaded {len(scenarios)} scenarios.")

    baseline = find_baseline(scenarios)
    if baseline is None:
        print("No explicit baseline scenario found. Narratives will be relative to generic 'normal' conditions.")
    else:
        print(f"Baseline scenario detected: {baseline.get('scenario')} ({baseline.get('family')})")

    narratives: List[Dict[str, Any]] = []

    for i, scen in enumerate(scenarios, start=1):
        scen_name = scen.get("scenario", f"scenario_{i}")
        print(f"\n=== [{i}/{len(scenarios)}] Generating narrative for: {scen_name} ===")
        narrative = call_llm_for_scenario(scen, baseline)
        narratives.append(narrative)

        # Append to JSONL incrementally (safe even if script stops later)
        with OUT_JSONL.open("a", encoding="utf-8") as f_out:
            f_out.write(json.dumps(narrative, ensure_ascii=False) + "\n")

    # Also save entire list as JSON
    with OUT_JSON.open("w", encoding="utf-8") as f_out:
        json.dump(narratives, f_out, ensure_ascii=False, indent=2)

    print(f"\nFinished. Saved {len(narratives)} narratives to:")

if __name__ == "__main__":
    main()