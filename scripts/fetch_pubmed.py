#!/usr/bin/env python3
"""Fetch recent PubMed records for seasonal influenza vaccine evidence surveillance.

This script writes raw candidate records to data/auto/pubmed_records_raw.json.
Curators should review candidate records before moving them into data/evidence_records.json.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "auto"
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUERY = os.getenv(
    "PUBMED_QUERY",
    '((seasonal influenza vaccine) AND (mRNA OR "modified RNA" OR modRNA OR mRNA-1010 OR mRNA-1083 OR mCOMBRIAX OR MFLUSIVA OR GSK4382276 OR OVX836 OR BPL-1357 OR Novavax OR Pfizer OR BioNTech OR Moderna OR Sanofi) AND ("2024/01/01"[Date - Publication] : "3000"[Date - Publication]))'
)
RETMAX = int(os.getenv("PUBMED_RETMAX", "200"))
EMAIL = os.getenv("NCBI_EMAIL", "evidence-map@example.org")
API_KEY = os.getenv("NCBI_API_KEY", "")


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=45) as response:
        return response.read().decode("utf-8")


def eutils_url(endpoint: str, params: dict[str, str | int]) -> str:
    base = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{endpoint}"
    params = dict(params)
    params["tool"] = "seasonal-flu-evidence-map"
    params["email"] = EMAIL
    if API_KEY:
        params["api_key"] = API_KEY
    return base + "?" + urllib.parse.urlencode(params)


def text_or_blank(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return " ".join("".join(node.itertext()).split())


def parse_article(article: ET.Element) -> dict:
    pmid = text_or_blank(article.find(".//PMID"))
    title = text_or_blank(article.find(".//ArticleTitle"))
    abstract = " ".join(text_or_blank(x) for x in article.findall(".//AbstractText"))
    journal = text_or_blank(article.find(".//Journal/Title"))
    year = text_or_blank(article.find(".//PubDate/Year"))
    month = text_or_blank(article.find(".//PubDate/Month"))
    doi = ""
    for article_id in article.findall(".//ArticleId"):
        if article_id.attrib.get("IdType") == "doi":
            doi = text_or_blank(article_id)
            break
    return {
        "pmid": pmid,
        "title": title,
        "abstract": abstract,
        "journal": journal,
        "publication_year": year,
        "publication_month": month,
        "doi": doi,
        "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
    }


def main() -> int:
    search_url = eutils_url("esearch.fcgi", {"db": "pubmed", "term": QUERY, "retmode": "json", "retmax": RETMAX, "sort": "pub date"})
    search = fetch_json(search_url)
    pmids = search.get("esearchresult", {}).get("idlist", [])
    if not pmids:
        (OUT_DIR / "pubmed_records_raw.json").write_text("[]\n", encoding="utf-8")
        print("No PubMed records found.")
        return 0

    time.sleep(0.35)
    fetch_url = eutils_url("efetch.fcgi", {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"})
    xml = fetch_text(fetch_url)
    root = ET.fromstring(xml)
    records = [parse_article(article) for article in root.findall(".//PubmedArticle")]
    (OUT_DIR / "pubmed_records_raw.json").write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(records)} PubMed candidate records to {OUT_DIR / 'pubmed_records_raw.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
