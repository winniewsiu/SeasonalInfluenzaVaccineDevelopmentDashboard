# Contributing and curation SOP

## Curation principles

1. Prefer primary sources over secondary reporting.
2. Capture both positive and negative evidence.
3. Separate efficacy, immunogenicity, safety, regulatory, and access evidence.
4. Do not infer authorization, recommendation, or availability from a trial result alone.
5. Mark automated records as `auto-unverified` until a curator confirms the source.
6. Keep Canada, US, Europe, and comparable-market relevance explicit in `jurisdictions`, `summary`, and `priority`.

## Adding an evidence record

1. Open `data/evidence_records.json`.
2. Copy an existing record with the same evidence type.
3. Create a stable record ID using the pattern:

```text
FLU-<PRODUCT>-<SOURCE-OR-STUDY>-<YEAR>
```

Examples:

```text
FLU-MRNA1010-P304-NEJM-2026
FLU-MCOMBRIAX-EMA-AUTH-2026
FLU-BPL1357-CHALLENGE-NCT07215858-2026
```

4. Fill all required fields.
5. Use a direct source URL whenever possible.
6. Keep `summary` concise and source-specific.
7. Set `map_updated` to the date the record was curated.
8. Run validation:

```bash
python3 scripts/validate_data.py
```

## Reviewing automated records

Automated records are written to:

```text
data/evidence_records_auto.json
```

Before moving an automated record into the curated dataset:

- Confirm product/candidate name.
- Confirm platform.
- Confirm phase and current trial status.
- Confirm study population and geography.
- Confirm whether results are available or the record is only a study registration.
- Rewrite the summary manually.
- Remove vague automated tags.
- Set `verification` to `seed-manual` or another reviewed label.

## Evidence domains

Use one primary evidence domain per record:

- Clinical efficacy
- Immunogenicity
- Safety/reactogenicity
- Correlates/mechanism
- Regulatory/policy
- Programmatic/access
- Pipeline landscape
- Real-world effectiveness

When a source covers multiple domains, create multiple records only if the source has separable decision-relevant evidence. Example: an FDA briefing document can support one immunogenicity record and one safety/reactogenicity record.

## Evidence type rules

- Use `Phase 3 / randomized trial` for phase 3 efficacy or immunogenicity trials.
- Use `Regulatory` for FDA, EMA, Health Canada, or formal authorization/review documents.
- Use `Policy/guideline` for WHO, CDC/ACIP, NACI/PHAC, EMA strain-composition, and national immunization guidance.
- Use `Landscape / market intelligence` for pipeline or commercial status sources.
- Use `Observational/RWE` only for real-world effectiveness or post-authorization surveillance designs.

## Pull request checklist

- [ ] JSON validates.
- [ ] All source URLs resolve.
- [ ] No duplicate record IDs.
- [ ] Automated records were manually reviewed before being moved.
- [ ] New product IDs exist in `data/products.json` unless intentionally cross-cutting.
- [ ] Priority label is justified.
- [ ] Canada/US/EU relevance is explicit when claiming priority.
- [ ] Dashboard tested locally with `python3 -m http.server 8000`.
