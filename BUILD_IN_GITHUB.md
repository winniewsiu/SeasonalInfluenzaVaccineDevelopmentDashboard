# Step-by-step GitHub build guide

This guide turns the dashboard folder into a live GitHub Pages site.

## A. Create the repository

1. Go to GitHub.
2. Select **New repository**.
3. Name it, for example: `seasonal-influenza-evidence-map`.
4. Keep it public if you want GitHub Pages available on the standard free plan.
5. Do not initialize with a README if you are pushing this scaffold from your computer.
6. Click **Create repository**.

## B. Push the dashboard files

From the folder containing `index.html`:

```bash
git init
git branch -M main
git add .
git commit -m "Initial seasonal influenza evidence dashboard"
git remote add origin https://github.com/YOUR-USER/seasonal-influenza-evidence-map.git
git push -u origin main
```

## C. Enable GitHub Pages

1. Open the repository in GitHub.
2. Go to **Settings**.
3. Select **Pages**.
4. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
5. Choose branch **main**.
6. Choose folder **/** root.
7. Click **Save**.
8. Wait for the Pages deployment to finish.

The dashboard will be published at:

```text
https://YOUR-USER.github.io/seasonal-influenza-evidence-map/
```

## D. Test the published dashboard

1. Confirm the four summary cards populate.
2. Confirm source groups load.
3. Search for `mRNA-1010`.
4. Click a populated matrix cell.
5. Export a CSV.
6. Open a source URL from an evidence card.

## E. Enable weekly evidence-surveillance pull requests

1. In the repository, go to **Settings** → **Actions** → **General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Enable pull request creation if your organization settings allow it.
4. Go to **Actions**.
5. Open **Update evidence surveillance candidates**.
6. Click **Run workflow**.

The workflow creates or updates:

```text
data/auto/pubmed_records_raw.json
data/auto/ctgov_records_raw.json
data/evidence_records_auto.json
```

Review the auto file before moving any records into `data/evidence_records.json`.

## F. Optional PubMed settings

For better PubMed API etiquette and rate limits:

1. Go to **Settings** → **Secrets and variables** → **Actions**.
2. Add secret `NCBI_API_KEY`.
3. Add variable `NCBI_EMAIL`.

## G. Routine update workflow

For each dashboard update:

```bash
git pull
python3 scripts/validate_data.py
python3 -m http.server 8000
```

Open `http://localhost:8000`, check the dashboard, then commit:

```bash
git add data index.html assets scripts README.md CONTRIBUTING.md BUILD_IN_GITHUB.md
git commit -m "Update evidence map"
git push
```

## H. Common problems

### The dashboard loads locally but not on GitHub Pages

Check that GitHub Pages is deploying from `main` and `/` root. Also check the Actions/Pages deployment log.

### The dashboard does not load when double-clicking `index.html`

Serve the site over HTTP instead:

```bash
python3 -m http.server 8000
```

### A JSON edit breaks the dashboard

Run:

```bash
python3 scripts/validate_data.py
python3 -m json.tool data/evidence_records.json > /tmp/checked.json
```

Fix the first reported JSON syntax or schema error.

### Automated PRs include irrelevant records

That is expected. Edit the search terms in:

```text
scripts/fetch_pubmed.py
scripts/fetch_clinicaltrials.py
```

Then keep only manually reviewed records in `data/evidence_records.json`.
