#!/usr/bin/env python3
"""Validate core dashboard JSON files."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_RECORD_FIELDS = [
    "id", "title", "product_id", "product", "developer", "platform", "development_stage",
    "jurisdictions", "evidence_domain", "evidence_type", "population", "outcomes",
    "source_group", "source_title", "source_date", "map_updated", "verification", "priority", "summary", "tags"
]


def load(name: str):
    path = DATA / name
    return json.loads(path.read_text(encoding="utf-8"))


def valid_url(url: str) -> bool:
    if not url:
        return True
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def main() -> int:
    records = load("evidence_records.json")
    products = load("products.json")
    domain_labels = {d["label"] for d in load("evidence_domains.json")}
    type_labels = {t["label"] for t in load("evidence_types.json")}
    source_names = {s["name"] for s in load("source_groups.json")}
    product_ids = {p["id"] for p in products}
    allowed_pseudo_product_ids = {"landscape-crosscutting", "policy-crosscutting", "gap-crosscutting"}

    errors: list[str] = []
    seen_ids: set[str] = set()
    for i, record in enumerate(records, start=1):
        for field in REQUIRED_RECORD_FIELDS:
            if field not in record:
                errors.append(f"Record {i} missing field: {field}")
        record_id = record.get("id")
        if record_id in seen_ids:
            errors.append(f"Duplicate record id: {record_id}")
        seen_ids.add(record_id)
        if record.get("product_id") not in product_ids | allowed_pseudo_product_ids:
            errors.append(f"Record {record_id} has unknown product_id: {record.get('product_id')}")
        if record.get("evidence_domain") not in domain_labels:
            errors.append(f"Record {record_id} has invalid evidence_domain: {record.get('evidence_domain')}")
        if record.get("evidence_type") not in type_labels:
            errors.append(f"Record {record_id} has invalid evidence_type: {record.get('evidence_type')}")
        if record.get("source_group") not in source_names:
            errors.append(f"Record {record_id} has invalid source_group: {record.get('source_group')}")
        if not isinstance(record.get("jurisdictions"), list):
            errors.append(f"Record {record_id} jurisdictions must be a list")
        if not isinstance(record.get("outcomes"), list):
            errors.append(f"Record {record_id} outcomes must be a list")
        if not valid_url(record.get("source_url", "")):
            errors.append(f"Record {record_id} has invalid source_url")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(records)} evidence records and {len(products)} products.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
