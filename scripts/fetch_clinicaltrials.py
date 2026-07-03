#!/usr/bin/env python3
"""Fetch ClinicalTrials.gov v2 candidate records for influenza vaccine surveillance."""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "auto"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TERMS = os.getenv(
    "CTGOV_TERMS",
    "mRNA-1010;mRNA-1083;MFLUSIVA;mCOMBRIAX;modified RNA influenza vaccine;GSK4382276;OVX836;BPL-1357;COVID-19 influenza combination vaccine;seasonal influenza mRNA vaccine"
).split(";")
PAGE_SIZE = int(os.getenv("CTGOV_PAGE_SIZE", "100"))


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def simplify_study(study: dict, term: str) -> dict:
    protocol = study.get("protocolSection", {})
    ident = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    conditions = protocol.get("conditionsModule", {})
    arms = protocol.get("armsInterventionsModule", {})
    outcomes = protocol.get("outcomesModule", {})
    contacts = protocol.get("contactsLocationsModule", {})
    nct_id = ident.get("nctId", "")
    interventions = [i.get("name", "") for i in arms.get("interventions", [])]
    locations = []
    for loc in contacts.get("locations", []) or []:
        locations.append({
            "facility": loc.get("facility", ""),
            "city": loc.get("city", ""),
            "state": loc.get("state", ""),
            "country": loc.get("country", ""),
        })
    return {
        "query_term": term,
        "nct_id": nct_id,
        "title": ident.get("briefTitle") or ident.get("officialTitle") or "",
        "official_title": ident.get("officialTitle", ""),
        "overall_status": status.get("overallStatus", ""),
        "start_date": (status.get("startDateStruct") or {}).get("date", ""),
        "primary_completion_date": (status.get("primaryCompletionDateStruct") or {}).get("date", ""),
        "phases": design.get("phases", []),
        "study_type": design.get("studyType", ""),
        "conditions": conditions.get("conditions", []),
        "interventions": interventions,
        "primary_outcomes": [o.get("measure", "") for o in outcomes.get("primaryOutcomes", [])],
        "locations": locations,
        "source_url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else "",
    }


def main() -> int:
    seen = set()
    records = []
    for term in TERMS:
        term = term.strip()
        if not term:
            continue
        url = "https://clinicaltrials.gov/api/v2/studies?" + urllib.parse.urlencode({
            "query.term": term,
            "format": "json",
            "pageSize": PAGE_SIZE,
        })
        payload = fetch_json(url)
        for study in payload.get("studies", []):
            record = simplify_study(study, term)
            if not record["nct_id"] or record["nct_id"] in seen:
                continue
            seen.add(record["nct_id"])
            records.append(record)
    (OUT_DIR / "ctgov_records_raw.json").write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(records)} ClinicalTrials.gov candidate records to {OUT_DIR / 'ctgov_records_raw.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
