# FMP Stock Downloader

This CLI pulls a curated set of stock-related datasets from Financial Modeling Prep (FMP) and saves them as JSON files on disk. It is designed to respect the free-tier limits (250 requests/day, 5 req/sec burst) by offering batching controls, request throttling, and resume-friendly output.

## What it collects

The default endpoint bundle covers fundamentals, quotes, and historical context:

- `stock_list` – universe of supported tickers
- `profile` – company profile metadata
- `quote`, `quote_short` – real-time quote snapshots
- `key_metrics`, `financial_ratios`, `financial_growth` – valuation and growth metrics (5 annual periods)
- `income_statement`, `balance_sheet`, `cash_flow`, `enterprise_values` – core fundamentals (5 annual filings)
- `rating` – FMP composite rating snapshot
- `historical_price_full` – up to 1,000 trading days of end-of-day prices (`serietype=line`)
- `dividends`, `splits` – historical dividend and split events

Tweak the include/exclude lists to pull a smaller subset, or add new entries to `ENDPOINTS` in `src/tools/fmp_stock_downloader.py` for additional APIs.

## Usage

```bash
python3 src/tools/fmp_stock_downloader.py \
  --api-key "$FMP_KEY" \
  --all-tickers \
  --max-tickers 200 \
  --output data/fmp \
  --sleep 1.2 \
  --max-requests 240 \
  --skip-existing
```

Key flags:

- `--api-key` (or `FMP_KEY` env var): your FMP token.
- `--all-tickers`: pull the stock universe first and then iterate every symbol.
- `--tickers`, `--tickers-file`: scope the run to a manual list when you want a faster subset.
- `--max-tickers`: guardrail to test the pipeline before unleashing a full download.
- `--include`, `--exclude`: select endpoint names to fetch (see the `ENDPOINTS` dict for options).
- `--sleep`: seconds paused after each call; keep ≥1s for the free tier.
- `--max-requests`: stop before breaking the daily allowance; combine with cron to chunk the workload across days.
- `--skip-existing`: resume mode—skips files that already exist on disk.

Output layout:

```
data/fmp/
├── stock_list.json
├── profile/
│   ├── AAPL.json
│   ├── MSFT.json
│   └── ...
└── historical_price_full/
    ├── AAPL.json
    └── ...
```

## Operational tips

- The free tier quota resets daily; schedule multiple partial runs (e.g., 200 tickers per night) to collect everything over time.
- Large historical endpoints can still return several hundred KB per symbol; ensure you have disk space and consider compressing archives after download.
- FMP updates financial statements shortly after filings; rerun the downloader periodically or pair it with `--skip-existing` to focus on fresh tickers.
- Handle HTTP 429 (rate limit) by increasing `--sleep` or waiting for the next quota window; the script will raise a runtime error so you can retry later.
- If you extend `ENDPOINTS`, stick to the same signature (`{symbol}` placeholder, default params) so the CLI can format URLs automatically.
