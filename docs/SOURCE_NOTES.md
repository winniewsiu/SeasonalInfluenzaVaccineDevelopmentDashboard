# Source notes for seed evidence map

The seed dashboard uses manually curated source URLs in `data/evidence_records.json`. This file summarizes why the sources were chosen and how they should be weighted.

## Highest-priority cross-cutting source

- CIDRAP Universal Influenza Vaccine Technology Landscape  
  Use for structured pipeline surveillance, candidate stage, platform, and recent status changes. Reconcile with sponsor and regulatory sources before making authorization or availability claims.

## Regulatory and public-health sources

- FDA VRBPAC and FDA vaccine composition pages  
  Use for US BLA/advisory committee evidence and annual US vaccine composition.

- EMA EPAR pages and seasonal composition updates  
  Use for EU authorization, CHMP opinions, product characteristics, and EU seasonal composition.

- Health Canada / NACI / PHAC  
  Use for Canadian recommendation context, priority populations, and programme implications. Add separate Health Canada product monograph records when a new vaccine is approved in Canada.

- WHO influenza composition recommendations  
  Use as global/seasonal context for strain selection and comparator interpretation.

- CDC / ACIP  
  Use for US annual recommendation context and vaccine composition.

## Peer-reviewed and registry sources

- PubMed-indexed phase 1, 2, 3, challenge, effectiveness, and correlates studies  
  Use for evidence summaries, outcome extraction, and direct study interpretation.

- ClinicalTrials.gov, ISRCTN, CTIS/EU Clinical Trials Register  
  Use for trial status, locations, design, and primary outcomes. Do not treat a registry entry as evidence of benefit unless results are posted or linked.

## Developer communications

Developer communications are useful for horizon scanning, regulatory-submission signals, and commercial status, but they should not be treated as final clinical evidence without corroborating peer-reviewed, registry, or regulatory material.

## Curator-defined gaps

Gap records are intentionally not external evidence. They are included so the matrix shows where further surveillance and synthesis are needed.
