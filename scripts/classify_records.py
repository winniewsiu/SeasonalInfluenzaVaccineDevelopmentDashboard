#!/usr/bin/env python3
"""Convert raw automated surveillance hits into unverified evidence-map candidates.

Output records are intentionally marked auto-unverified and saved separately.
Curators should edit, verify, and move accepted records into data/evidence_records.json.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTO = ROOT / "data" / "auto"
OUT = ROOT / "data" / "evidence_records_auto.json"
TODAY = date.today().isoformat()

PRODUCT_KEYWORDS = [
    ("moderna-mrna-1010", "mFLUSIVA / mRNA-1010", ["mrna-1010", "mflusiva"]),
    ("moderna-mrna-1083", "mCOMBRIAX / mRNA-1083", ["mrna-1083", "mcombriax"]),
    ("pfizer-biontech-modrna-flu", "Pfizer/BioNTech modified mRNA seasonal influenza vaccine", ["pfizer", "biontech", "modrna", "modified-rna"]),
    ("pfizer-biontech-combo", "Pfizer/BioNTech mRNA COVID-19 + influenza combination vaccine", ["pfizer", "biontech", "covid-19", "combination"]),
    ("gsk-gsk4382276", "GSK seasonal influenza mRNA vaccine programme / GSK4382276", ["gsk4382276", "gsk", "flumha"]),
    ("sanofi-novavax-combo", "Sanofi + Novavax non-mRNA COVID-19 + influenza combination candidates", ["sanofi", "novavax", "combination"]),
    ("novavax-tniv-cic", "Novavax stand-alone influenza vaccine / COVID-19 influenza combination programme", ["novavax", "nanoflu", "tniv"]),
    ("osivax-ovx836", "OVX836", ["ovx836", "osivax"]),
    ("niaid-bpl-1357", "BPL-1357", ["bpl-1357", "flugen"]),
]


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def pick_product(text: str):
    lower = text.lower()
    for product_id, product_name, keywords in PRODUCT_KEYWORDS:
        if any(k in lower for k in keywords):
            return product_id, product_name
    return "auto-crosscutting", "Auto-classified influenza vaccine evidence"


def classify_domain(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in ["efficacy", "effectiveness", "challenge", "protection"]):
        return "Clinical efficacy"
    if any(k in lower for k in ["immunogenicity", "hai", "antibody", "seroconversion", "neutralizing", "immune response"]):
        return "Immunogenicity"
    if any(k in lower for k in ["safety", "reactogenicity", "adverse", "tolerability"]):
        return "Safety/reactogenicity"
    if any(k in lower for k in ["correlate", "mucosal", "cellular", "t-cell", "nucleoprotein"]):
        return "Correlates/mechanism"
    return "Pipeline landscape"


def classify_type(text: str, source: str) -> str:
    lower = text.lower()
    if source == "ctgov":
        if "phase 3" in lower:
            return "Phase 3 / randomized trial"
        if "phase 2" in lower:
            return "Phase 2"
        if "phase 1" in lower:
            return "Phase 1"
        if "challenge" in lower:
            return "Challenge study"
        return "Clinical trial registry"
    if "phase 3" in lower:
        return "Phase 3 / randomized trial"
    if "phase 2" in lower:
        return "Phase 2"
    if "phase 1" in lower:
        return "Phase 1"
    if "challenge" in lower:
        return "Challenge study"
    return "Observational/RWE"


def pubmed_to_record(item: dict) -> dict:
    text = f"{item.get('title','')} {item.get('abstract','')}"
    product_id, product = pick_product(text)
    return {
        "id": f"AUTO-PUBMED-{item.get('pmid','unknown')}",
        "title": item.get("title", "Untitled PubMed record"),
        "product_id": product_id,
        "product": product,
        "developer": "Auto-classified",
        "platform": "Auto-classified",
        "development_stage": "Auto-classified",
        "jurisdictions": ["Global"],
        "evidence_domain": classify_domain(text),
        "evidence_type": classify_type(text, "pubmed"),
        "population": "Auto-classified; curator review required",
        "outcomes": [],
        "source_group": "Peer-reviewed",
        "source_title": item.get("journal", "PubMed"),
        "source_url": item.get("source_url", ""),
        "source_date": item.get("publication_year", ""),
        "map_updated": TODAY,
        "verification": "auto-unverified",
        "priority": "Auto",
        "summary": (item.get("abstract", "")[:500] + "...") if item.get("abstract") else "PubMed hit; curator review required.",
        "tags": ["auto-unverified", "PubMed"],
    }


def ctgov_to_record(item: dict) -> dict:
    text = json.dumps(item, ensure_ascii=False)
    product_id, product = pick_product(text)
    phases = ", ".join(item.get("phases") or [])
    return {
        "id": f"AUTO-CTGOV-{item.get('nct_id','unknown')}",
        "title": item.get("title", "Untitled ClinicalTrials.gov record"),
        "product_id": product_id,
        "product": product,
        "developer": "Auto-classified",
        "platform": "Auto-classified",
        "development_stage": phases or item.get("overall_status", "Auto-classified"),
        "jurisdictions": sorted({loc.get("country") for loc in item.get("locations", []) if loc.get("country")} or {"Global"}),
        "evidence_domain": classify_domain(text),
        "evidence_type": classify_type(text, "ctgov"),
        "population": "Auto-classified; curator review required",
        "outcomes": item.get("primary_outcomes", []),
        "source_group": "Clinical trial registry",
        "source_title": item.get("nct_id", "ClinicalTrials.gov"),
        "source_url": item.get("source_url", ""),
        "source_date": item.get("start_date") or TODAY,
        "map_updated": TODAY,
        "verification": "auto-unverified",
        "priority": "Auto",
        "summary": f"{item.get('overall_status','')} clinical trial registry hit. Phases: {phases or 'not specified'}. Curator review required.",
        "tags": ["auto-unverified", "ClinicalTrials.gov"],
    }


def main() -> int:
    records = []
    for item in read_json(AUTO / "pubmed_records_raw.json", []):
        if item.get("pmid"):
            records.append(pubmed_to_record(item))
    for item in read_json(AUTO / "ctgov_records_raw.json", []):
        if item.get("nct_id"):
            records.append(ctgov_to_record(item))

    # Deduplicate by id and source URL.
    deduped = []
    seen = set()
    for record in records:
        key = record["id"] or record.get("source_url")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)

    OUT.write_text(json.dumps(deduped, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(deduped)} auto-unverified candidate records to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
