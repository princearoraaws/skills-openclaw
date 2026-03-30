#!/usr/bin/env python3
"""
Clinical Trial Search Script

Reads API credentials from environment variables and POSTs structured
query parameters to a clinical trial database endpoint.

Dict-type fields (target, drug_name, drug_modality, drug_feature, location,
route_of_administration) accept a flat {"keywords": [...]} object.
Include/exclude filtering is not supported by the API.

Usage:
    python scripts/search.py --params '<JSON string>'
    python scripts/search.py --params-file /path/to/query.json

Environment variables:
    NOAH_API_TOKEN  — API authentication token (required)
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("[ERROR] Missing dependency: requests\nInstall it with: pip install requests", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Default query structure (mirrors backend ClinicalTrialSearchData)
# ---------------------------------------------------------------------------

DEFAULT_PARAMS = {
    "acronym": [],
    "company": [],
    "drug_feature": {},
    "drug_modality": {},
    "drug_name": {},
    "indication": [],
    "location": {},
    "nctid": [],
    "phase": [],
    "target": {},
    "route_of_administration": {},
    "has_result_summary": False,
    "official_data": False,
    "page_num": 0,
    "page_size": 10,
}


def build_payload(user_params: dict) -> dict:
    """Merge user-supplied parameters with defaults to produce a complete payload.

    Dict-type fields should be passed as {"keywords": ["val1", "val2"]}.
    Include/exclude filtering is not supported.
    """
    payload = DEFAULT_PARAMS.copy()
    for key, value in user_params.items():
        if key in payload:
            payload[key] = value
        else:
            print(f"[WARN] Unknown parameter field ignored: {key}", file=sys.stderr)
    return payload


def search(params: dict) -> dict:
    """
    POST a query to the clinical trial database API.

    :param params: Query parameter dict
    :return: Parsed JSON response from the API
    """
    api_url = os.environ.get("NOAH_API_URL", "https://noah.bio/api/skills/clinical_trial_search/").strip()
    api_token = os.environ.get("NOAH_API_TOKEN", "").strip()

    if not api_token:
        raise EnvironmentError(
            "Environment variable NOAH_API_TOKEN is not set.\n"
            "Set it before running, for example:\n"
            "  export NOAH_API_TOKEN=your_token_here"
        )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }

    payload = build_payload(params)

    print(f"[INFO] Endpoint: {api_url}", file=sys.stderr)
    print(f"[INFO] Query payload:\n{json.dumps(payload, indent=2)}", file=sys.stderr)

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(f"Cannot connect to API server: {api_url}\nDetails: {e}")
    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out (30s). Check your network or API server status.")
    except requests.exceptions.HTTPError:
        error_body = ""
        try:
            error_body = response.text
        except Exception:
            pass
        raise RuntimeError(
            f"API returned HTTP {response.status_code}\n"
            f"Response body: {error_body}"
        )

    return response.json()


def format_results(data: dict) -> str:
    """Format the API response into human-readable text."""
    lines = []

    total = data.get("total", data.get("total_count", "unknown"))
    trials = data.get("trials", data.get("results", data.get("data", [])))

    lines.append(f"=== Results: {total} trial(s) matched ===\n")

    if not trials:
        lines.append("No clinical trials found matching your query.")
        return "\n".join(lines)

    for i, trial in enumerate(trials, 1):
        lines.append(f"[{i}] {trial.get('title', trial.get('brief_title', '(no title)'))}")

        nct = trial.get("nct_id") or trial.get("nctid") or trial.get("NCTId", "")
        if nct:
            lines.append(f"  NCT ID              : {nct}")

        acronym = trial.get("acronym", "")
        if acronym:
            lines.append(f"  Acronym             : {acronym}")

        phase = trial.get("phase", "")
        if phase:
            lines.append(f"  Phase               : {phase}")

        status = trial.get("status", trial.get("overall_status", ""))
        if status:
            lines.append(f"  Status              : {status}")

        indication = trial.get("indication", trial.get("conditions", ""))
        if indication:
            if isinstance(indication, list):
                indication = ", ".join(indication)
            lines.append(f"  Indication          : {indication}")

        drugs = trial.get("drugs", trial.get("interventions", ""))
        if drugs:
            if isinstance(drugs, list):
                drugs = ", ".join(drugs) if isinstance(drugs[0], str) else ", ".join(
                    d.get("name", "") for d in drugs
                )
            lines.append(f"  Drug(s)             : {drugs}")

        sponsor = trial.get("company", trial.get("sponsor", trial.get("lead_sponsor", "")))
        if sponsor:
            lines.append(f"  Sponsor             : {sponsor}")

        if trial.get("has_result_summary"):
            lines.append(f"  Result Summary      : available")

        lines.append("")  # blank line between entries

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Query a clinical trial database via POST API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # PD-1 antibody trials in lung cancer, Phase 3, with results
  python scripts/search.py --params '{"target": {"keywords": ["PD-1"]}, "indication": ["lung cancer"], "phase": ["Phase 3"], "has_result_summary": true}'

  # Query by NCT ID
  python scripts/search.py --params '{"nctid": ["NCT04280783"]}'

  # Load parameters from a file
  python scripts/search.py --params-file /tmp/query.json

  # Output raw JSON
  python scripts/search.py --params '{"indication": ["NSCLC"]}' --raw

  # Save results to a file
  python scripts/search.py --params '{"company": ["Roche"]}' --output results.txt
        """,
    )
    parser.add_argument(
        "--params",
        type=str,
        default=None,
        help="Query parameters as a JSON string",
    )
    parser.add_argument(
        "--params-file",
        type=str,
        default=None,
        help="Path to a JSON file containing query parameters",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print raw JSON response instead of formatted output",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Save results to the specified file path",
    )

    args = parser.parse_args()

    # Parse query parameters
    if args.params:
        try:
            user_params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(f"[ERROR] --params is not valid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.params_file:
        try:
            with open(args.params_file, "r", encoding="utf-8") as f:
                user_params = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Parameter file not found: {args.params_file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Parameter file is not valid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("[ERROR] Provide either --params or --params-file", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Execute the query
    try:
        result = search(user_params)
    except (EnvironmentError, ConnectionError, TimeoutError, RuntimeError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    # Render output
    output_text = json.dumps(result, indent=2) if args.raw else format_results(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"[INFO] Results saved to: {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()