# arxiv-radar-electrochemistry

Project-specific arXiv radar for Third Matter electrochemistry.

Scope:

- CO2 electroreduction and formate production.
- Transition-metal sulfide electrocatalysts, especially Fe/Ni/S systems.
- Electrochemical interfaces, double layers, constant-potential DFT, and solvation.
- Proton/hydroxide transport, pH gradients, membranes, flow cells, and EIS.
- Redox cycles and autocatalytic electrochemical reaction networks.

This repository is intentionally narrower than the general chemistry,
chemical-engineering, physics, and polymer radars so it can track Third Matter
needs without adding project-specific noise for other users.

## Layout

- `config.yaml` - project metadata, arXiv search topics, and relevance filter.
- `tags/canonical.yaml` - canonical tag vocabulary.
- `tools/` - fetch, backfill, render, retag, and archive scripts.
- `data/` - monthly JSON shards created by backfill or daily runs.
- `docs/` - GitHub Pages site generated from the corpus.
- `.github/workflows/*.template` - disabled workflow templates.

## Initial Setup

```powershell
cd D:\home\ignat\project-third-matter\git\arxiv-radar-electrochemistry
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt -r requirements-tag-analysis.txt
```

## Validate Queries

Run a small dry backfill before collecting the full corpus:

```powershell
.venv\Scripts\python.exe tools\backfill.py --from-date 2026-01-01 --to-date 2026-01-31 --dry-run
```

If the counts look sane, run the two-year backfill:

```powershell
.venv\Scripts\python.exe tools\backfill.py --from-date 2024-05-01 --to-date 2026-05-03
```

The backfill is resumable through `data/backfill_checkpoint.json`, which is
ignored by git.

## Render

After backfill:

```powershell
.venv\Scripts\python.exe tools\render_abstracts.py
.venv\Scripts\python.exe tools\render_tag_pages.py
.venv\Scripts\python.exe tools\render_index.py
.venv\Scripts\python.exe tools\render_readme.py
```

## Retag

After editing `tags/canonical.yaml`:

```powershell
.venv\Scripts\python.exe tools\retag_corpus.py
.venv\Scripts\python.exe tools\render_tag_pages.py
.venv\Scripts\python.exe tools\render_index.py
.venv\Scripts\python.exe tools\render_readme.py
```

## Workflows

Workflow files are committed as templates so GitHub Actions will not run until
they are explicitly enabled.

To enable the daily update:

```powershell
Copy-Item .github\workflows\daily-arxiv.yml.template .github\workflows\daily-arxiv.yml
```

Run it manually once from GitHub Actions. If it succeeds, uncomment the cron
schedule inside `.github/workflows/daily-arxiv.yml`.

To enable monthly archive pruning:

```powershell
Copy-Item .github\workflows\monthly-archive.yml.template .github\workflows\monthly-archive.yml
```

## Tests

```powershell
.venv\Scripts\python.exe -m pytest tests -q
```
