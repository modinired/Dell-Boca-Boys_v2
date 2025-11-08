# EJWCS Scraper Pack (v1)

Industrial-ready scaffolding to collect **job detail data** that feeds EJWCS.

## Features
- JSON-LD JobPosting parser (schema.org)
- ATS adapters (Greenhouse/Lever stubs)
- Normalizers: compensation, location, seniority
- Provenance scoring & SimHash dedupe
- Scheduler stub with polite delays
- Golden fixture + example script

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python examples/parse_fixture.py
```

Network calls are omitted so it runs offline; integrate httpx/playwright where allowed.
