# Seasonal Influenza Vaccine Evidence Map

A GitHub Pages-ready evidence dashboard for seasonal influenza vaccines and flu-containing combination vaccines, prioritizing candidates and products likely to matter for Canada, the United States, Europe, and similar regulatory settings.

The scaffold mirrors common evidence-map features:

- Source and provenance panel
- Filters by product, evidence domain, evidence type, jurisdiction, stage, source group, priority, and date
- Domain × evidence-type matrix
- Evidence record cards with source URLs
- Product/candidate tracking cards
- Evidence-gap panel
- Automated surveillance scripts for PubMed and ClinicalTrials.gov candidates

**Current seed version:** 2026-07-03  
**Use case:** evidence surveillance, policy synthesis support, and internal horizon scanning.  
**Not for:** clinical advice, regulatory advice, or direct medical decision-making.

---

## 1. Repository structure

```text
.
├── index.html                         # Static dashboard page
├── assets/
│   ├── app.js                         # Filtering, matrix, cards, CSV export
│   └── styles.css                     # Dashboard styles
├── data/
│   ├── evidence_records.json          # Curated evidence records loaded by dashboard
│   ├── products.json                  # Product/candidate metadata
│   ├── evidence_domains.json          # Matrix rows
│   ├── evidence_types.json            # Matrix columns
│   ├── evidence_gaps.json             # Gap cards
│   └── source_groups.json             # Source strategy
├── scripts/
│   ├── fetch_pubmed.py                # PubMed evidence surveillance
│   ├── fetch_clinicaltrials.py        # ClinicalTrials.gov evidence surveillance
│   ├── classify_records.py            # Auto-classifies unverified hits
│   └── validate_data.py               # JSON validation
├── .github/workflows/
│   └── update-evidence.yml            # Weekly source-surveillance PR
├── CONTRIBUTING.md                    # Curation SOP
└── LICENSE
```

---

## 2. What is included in the seed map

The seed records prioritize:

1. **Near-term regulatory or availability signals**
   - Moderna mRNA-1010 / mFLUSIVA
   - Moderna mRNA-1083 / mCOMBRIAX
   - Pfizer/BioNTech seasonal modified mRNA influenza programme
   - Pfizer/BioNTech COVID-19 + influenza combination programme
   - GSK seasonal influenza mRNA programme
   - Sanofi/Novavax COVID-19 + influenza combination candidates

2. **Watchlist broad-protection or uncertain-commercial-pathway candidates**
   - Novavax stand-alone influenza and CIC programme
   - Osivax OVX836
   - NIAID/FluGen BPL-1357

3. **Policy/comparator context**
   - WHO Northern Hemisphere composition
   - CDC/FDA/ACIP US seasonal composition and recommendations
   - EMA EU composition recommendation
   - NACI/PHAC Canadian recommendation context

4. **Curator-defined evidence gaps**
   - Canadian access and submission signals
   - Older-adult real-world effectiveness
   - B-lineage immunogenicity and trivalent composition implications
   - Correlates beyond HAI
   - Safety/reactogenicity of COVID-19 + influenza combination vaccines
   - Paediatric, pregnancy, and immunocompromised population gaps

---

## 3. Build the dashboard locally

### Step 1 — Download or clone the repository

```bash
git clone https://github.com/YOUR-USER/YOUR-REPO.git
cd YOUR-REPO
```

### Step 2 — Validate the seed data

```bash
python3 scripts/validate_data.py
```

Expected output:

```text
Validated 33 evidence records and 9 products.
```

### Step 3 — Serve the site locally

Do not open `index.html` directly from the filesystem. Browsers often block `fetch()` from local files.

```bash
python3 -m http.server 8000
```

Open the local server in a browser:

```text
http://localhost:8000
```

### Step 4 — Edit source data

Most updates happen in JSON files:

- Add or edit evidence records in `data/evidence_records.json`
- Add or edit products in `data/products.json`
- Add matrix categories in `data/evidence_domains.json` and `data/evidence_types.json`
- Add/update gap priorities in `data/evidence_gaps.json`

Re-run validation after every edit:

```bash
python3 scripts/validate_data.py
```

### Step 5 — Commit changes

```bash
git add .
git commit -m "Update seasonal influenza evidence map"
git push
```

---

## 4. Publish with GitHub Pages

### Step 1 — Create a new GitHub repository

Create an empty repository, for example:

```text
seasonal-influenza-evidence-map
```

### Step 2 — Push this folder to GitHub

From the dashboard folder:

```bash
git init
git branch -M main
git add .
git commit -m "Initial seasonal influenza evidence dashboard"
git remote add origin https://github.com/YOUR-USER/seasonal-influenza-evidence-map.git
git push -u origin main
```

### Step 3 — Enable GitHub Pages

In GitHub:

1. Open the repository.
2. Go to **Settings**.
3. Select **Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**.
5. Select branch **main** and folder **/** root.
6. Save.

The dashboard will be published at a URL like:

```text
https://YOUR-USER.github.io/seasonal-influenza-evidence-map/
```

### Step 4 — Confirm the dashboard loads data

After GitHub Pages deploys:

1. Open the published site.
2. Confirm the evidence-record count is visible.
3. Test a matrix-cell click.
4. Test a search term such as `mRNA-1010`, `Canada`, or `B lineage`.
5. Test CSV export.

---

## 5. Turn on automated evidence surveillance

The repository includes a weekly GitHub Actions workflow:

```text
.github/workflows/update-evidence.yml
```

It runs these steps:

1. Fetch PubMed candidate records.
2. Fetch ClinicalTrials.gov candidate records.
3. Auto-classify the raw hits as `auto-unverified`.
4. Validate curated dashboard data.
5. Open a pull request containing `data/evidence_records_auto.json` and raw surveillance files.

### Step 1 — Enable workflow write permissions

In GitHub:

1. Open **Settings**.
2. Select **Actions** → **General**.
3. Under **Workflow permissions**, choose **Read and write permissions**.
4. Allow GitHub Actions to create and approve pull requests if your organization permits it.

### Step 2 — Add optional PubMed configuration

In **Settings** → **Secrets and variables** → **Actions**:

- Add optional secret `NCBI_API_KEY` for higher NCBI request limits.
- Add optional variable `NCBI_EMAIL` with a maintainer email.

### Step 3 — Run the workflow manually

1. Open the **Actions** tab.
2. Select **Update evidence surveillance candidates**.
3. Click **Run workflow**.

### Step 4 — Review the automated pull request

The automated output is intentionally not merged into the dashboard. Review `data/evidence_records_auto.json` and move accepted items into `data/evidence_records.json` only after curation.

Use these rules:

- Replace `Auto-classified` fields with verified product, platform, population, stage, and jurisdiction values.
- Set `verification` to `seed-manual` or another reviewed label.
- Add a concise summary of the evidence.
- Confirm the source URL resolves.
- Confirm that the evidence domain and evidence type are correct.
- Re-run `python3 scripts/validate_data.py`.

---

## 6. Data schema

Each object in `data/evidence_records.json` uses this structure:

```json
{
  "id": "FLU-MRNA1010-P304-NEJM-2026",
  "title": "Evidence record title",
  "product_id": "moderna-mrna-1010",
  "product": "mFLUSIVA / mRNA-1010",
  "developer": "Moderna",
  "platform": "mRNA",
  "development_stage": "Regulatory review / phase 3 evidence",
  "jurisdictions": ["United States", "European Union", "Canada"],
  "evidence_domain": "Clinical efficacy",
  "evidence_type": "Phase 3 / randomized trial",
  "population": "Adults ≥50 years",
  "outcomes": ["RT-PCR-confirmed influenza-like illness"],
  "source_group": "Peer-reviewed",
  "source_title": "Source title",
  "source_url": "https://example.org/source",
  "source_date": "2026-05-07",
  "map_updated": "2026-07-03",
  "verification": "seed-manual",
  "priority": "High",
  "summary": "Concise source-backed summary.",
  "tags": ["phase 3", "mRNA"]
}
```

### Required fields

All fields above are required. `source_url` may be blank only for curator-defined gap records.

### Verification labels

| Label | Meaning |
|---|---|
| `seed-manual` | Manually entered and source-checked seed record |
| `auto-unverified` | Automatically harvested; not yet suitable for synthesis |
| `curator-gap` | Evidence-gap or synthesis-priority entry |

### Priority labels

| Label | Meaning |
|---|---|
| `High` | Near-term availability or decision relevance for Canada/US/EU |
| `Medium` | Important but less immediate or less direct availability signal |
| `Watchlist` | Relevant technology, uncertain commercial path, or early development |
| `Auto` | Automated candidate requiring review |

---

## 7. Recommended curation workflow

### Weekly

1. Review automated PRs from PubMed and ClinicalTrials.gov.
2. Check FDA, EMA, Health Canada, NACI/PHAC, CDC/ACIP, WHO, and ECDC pages for updates.
3. Review sponsor investor and pipeline pages for status changes.
4. Move verified records into `data/evidence_records.json`.
5. Add or update evidence gaps.
6. Validate and merge.

### Monthly

1. Reconcile candidate status against CIDRAP's landscape and sponsor pipeline pages.
2. Review ClinicalTrials.gov and EU/UK trial registries for new trial locations and status changes.
3. Check whether Canada-specific evidence or submissions have appeared.
4. Archive a release with the month and evidence-map version.

### Seasonal key dates

1. WHO Northern Hemisphere composition recommendations.
2. FDA VRBPAC strain-composition meetings.
3. EMA seasonal flu composition updates.
4. CDC/ACIP annual recommendations.
5. NACI/PHAC seasonal statement release.
6. Sponsor regulatory decisions or launch announcements before influenza season.

---

## 8. Add new dashboard views

The app is dependency-free JavaScript. To add a view:

1. Add an HTML section to `index.html`.
2. Add a rendering function in `assets/app.js`.
3. Load any new JSON file in `DATA_PATHS`.
4. Update `renderAll()` if the new view responds to filters.
5. Add CSS in `assets/styles.css`.
6. Validate all JSON and test locally.

Useful extensions:

- **Country readiness tab:** Health Canada, FDA, EMA, MHRA, and national programme status.
- **Trial map:** Use trial-location countries from ClinicalTrials.gov and CTIS.
- **Outcome dashboard:** Compare HAI, seroconversion, PCR-confirmed influenza, hospitalization, and adverse-event endpoints.
- **Comparator view:** Standard-dose, high-dose, adjuvanted, recombinant, and combination vaccine comparators.
- **Evidence confidence score:** Weight by source group, design, sample size, population relevance, and directness to Canada/US/EU decisions.

---

## 9. Source hierarchy

Use higher-authority sources whenever possible:

1. Regulatory agency pages, product labels, advisory committee documents, and official assessment reports.
2. Peer-reviewed publications and trial registry results.
3. Public health agency recommendations and surveillance reports.
4. Curated landscape databases.
5. Developer press releases and investor materials.
6. News or market wires only as signposts to primary sources.

Developer press releases should not be treated as final evidence of clinical benefit unless supported by peer-reviewed, registry, or regulatory records.

---

## 10. License

This scaffold is provided under the MIT License. Validate all source use and licensing requirements for your organization before publication.
