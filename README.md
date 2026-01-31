# eBay Automation Framework — Quick & Simple

Lightweight Playwright automation using Page Object Model (POM). Designed to:
- Search eBay for a configured term (e.g., "mazda mx-5")
- Validate results and count them
- Apply a transmission filter (Manual) and report the filtered count

Quick highlights:
- Tests use `config.json` (no hardcoded test data)
- Page objects encapsulate actions (home → search → results)
- Simple pytest test delegates work to page helpers

---

## Quick Start

1. Create and activate venv:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
```

2. Run the simple pytest test:

```powershell
pytest test_simple_flow.py
```

---

## Key files

- `config.json` — test data & settings
- `home_page.py` — search helper (`search_and_open_results`)
- `search_results_page.py` — helpers (`validate_results_and_count`, `apply_transmission_and_get_count`)
- `test_simple_flow.py` — one-line test that calls page helpers
- `logger_report.py` — logging and HTML report generation

---

## Config (example)

Edit `config.json` to change the search term or filter.

---

## Outputs

- HTML report: `reports/test_report.html`
- Logs: `logs/test_execution.log`
- Screenshot: `screenshots/final_results.png`

---

## Troubleshooting (short)

- If browser won't launch: `python -m playwright install chromium`
- If elements not found: increase `element_wait` in `config.json` or run headful (`headless:false`) to inspect

---

That’s it — concise, actionable, and ready to run.
