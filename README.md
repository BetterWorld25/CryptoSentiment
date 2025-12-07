
# CryptoSentiment: Hourly Crypto Market & Sentiment Dataset
## DSCI 511 Term Project

This project automatically collects **hourly cryptocurrency market and sentiment data** using free, publicly available data sources.  
The pipeline runs as a single Python script (`CryptoMarketSentiment.py`) and appends each new run to a growing dataset `crypto_hourly.csv`.

The goal is to create a reproducible, real-time dataset that combines **price/volume**, **technical indicators**, **online attention**, and **macro context** for the top cryptocurrencies.

---

## 1. Description

At each run, the script:

1. Pulls the **top 10 coins by market cap** from CoinGecko.
2. Collects:
   - Live market data (price, 24h % change, volume, market cap)
   - Intraday prices for each coin to compute technical indicators
3. Computes technical indicators:
   - 14-period **RSI**
   - 14-period **volatility** of returns
   - 20-period **SMA** (simple moving average)
4. Adds **sentiment / attention features**:
   - Google Trends interest for “Bitcoin” and “Ethereum”
   - Reddit sentiment from titles of top posts in r/CryptoCurrency (VADER sentiment)
   - Crypto Fear & Greed Index
5. Adds **macro features**:
   - S&P500 price proxy (SPY)
   - Gold price proxy (GLD)
   - USD index proxy derived from USD/EUR FX rate
6. Appends the new rows to `crypto_hourly.csv`, avoiding duplicates.

Each row in the dataset represents a combination of a **timestamp** and **coin**, enriched with multiple market, sentiment, and macro signals.

---

## 2. Data Sources & Rights

All data is collected from free, public APIs and public web endpoints:

- **CoinGecko API**  
  - Market data, coin prices, market cap, volume, top-10 coins.  
  - Docs: https://www.coingecko.com/en/api

- **Google Trends (pytrends)**  
  - Relative search interest for “Bitcoin” and “Ethereum”.  
  - Service: https://trends.google.com/

- **Reddit (`r/CryptoCurrency`)**  
  - Top posts’ titles pulled via the public JSON endpoint.  
  - Example endpoint:  
    `https://www.reddit.com/r/CryptoCurrency/top.json?limit=50&t=hour`

- **Crypto Fear & Greed Index (alternative.me)**  
  - Overall crypto market sentiment index value.  
  - API: https://api.alternative.me/fng/

- **Alpha Vantage** (macro signals)  
  - S&P500, Gold, FX rate for USD/EUR used to build a simple USD index.  
  - Docs: https://www.alphavantage.co/documentation/  
  - Requires a **free API key** (see Setup below). If no key is configured, these columns will be `NaN`.

### Our contribution

- We **do not** host or redistribute the original upstream data as a static dump from each provider.
- We provide:
  - The **collection script** (`CryptoMarketSentiment.py`)
  - A growing **derived dataset** `crypto_hourly.csv` on our local machines
  - A **data dictionary** describing each column (`data_dictionary.csv`)

This project is for **educational purposes** as part of DSCI 511 at Drexel University. Please review each provider’s terms of service before using the data for production or commercial applications.

---

## 3. Dataset Contents

Each run appends one row per coin (top 10 coins by market cap at that moment). Over time, `crypto_hourly.csv` will look like:

- Rows ≈ `10 × number_of_runs`
- Columns ≈ 16 features (market, technical, sentiment, macro)

### 3.1 Columns (high-level overview)

See `data_dictionary.csv` for a full machine-readable version. Briefly:

| Column              | Type      | Description                                                    |
|---------------------|-----------|----------------------------------------------------------------|
| `timestamp`         | datetime  | UTC time when this row was collected                          |
| `coin`              | string    | CoinGecko coin ID (e.g. `bitcoin`, `ethereum`)                |
| `price`             | float     | Latest market price in USD                                    |
| `change_24h_%`      | float     | 24h percentage price change                                   |
| `volume_24h`        | float     | 24h trading volume (USD)                                      |
| `market_cap`        | float     | Market capitalization (USD)                                   |
| `rsi`               | float     | 14-period RSI computed from recent intraday price series      |
| `volatility`        | float     | 14-period rolling standard deviation of returns               |
| `sma_20`            | float     | 20-period simple moving average of price                      |
| `google_trend_btc`  | float     | Google Trends interest level for “Bitcoin”                    |
| `google_trend_eth`  | float     | Google Trends interest level for “Ethereum”                   |
| `fear_greed_index`  | float     | Crypto Fear & Greed Index value                               |
| `reddit_sentiment`  | float     | Average VADER compound sentiment score of top subreddit posts |
| `SP500`             | float     | S&P500 proxy price (SPY)                                      |
| `Gold`              | float     | Gold proxy price (GLD)                                        |
| `USD_Index`         | float     | Simple USD index derived from USD/EUR rate                    |

Missing values (e.g. when an API fails or rate limits hit) are stored as `NaN`.

---

## 4. Getting Started

### 4.1 Installation

Clone the repository:

```bash
git clone https://github.com/BetterWorld25/CryptoSentiment.git
cd CryptoSentiment
```

Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 4.2 Alpha Vantage API key (optional but recommended)

Sign up for a free key at:  
https://www.alphavantage.co/support/#api-key

Set an environment variable before running:

```bash
# Windows (PowerShell)
$env:ALPHAVANTAGE_API_KEY="YOUR_KEY_HERE"

# macOS / Linux
export ALPHAVANTAGE_API_KEY="YOUR_KEY_HERE"
```

Inside `CryptoMarketSentiment.py`, make sure it reads:

```python
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "")
```

If you skip this step, macro columns (`SP500`, `Gold`, `USD_Index`) will typically be `NaN`, but the rest of the dataset will still be collected.

---

## 5. Executing the Collection Script

### 5.1 One-off run

From the repo root:

```bash
python CryptoMarketSentiment.py
```

What happens:

- The script fetches data for the current hour.
- A small `pandas` DataFrame is created (one row per coin).
- It merges with any existing `crypto_hourly.csv` (if present), avoiding duplicates by `["coin", "timestamp"]`.
- It writes the updated dataset back to `crypto_hourly.csv`.
- It appends a short entry to `run_log.txt` with timestamp and number of rows added.

### 5.2 Scheduling hourly runs (Windows Task Scheduler)

1. Open **Task Scheduler** in Windows.
2. Create a **Basic Task**:
   - Trigger: “Daily” (repeat every 1 day).
   - In the advanced trigger options, repeat task every **1 hour** for **24 hours**.
3. Action:
   - Program/script: `python`
   - Arguments: `C:\path\to\CryptoSentiment\CryptoMarketSentiment.py`
   - Start in: `C:\path\to\CryptoSentiment`
4. Ensure the virtual environment (if used) and dependencies are installed for the same user account that Task Scheduler runs under.

> For the class project, you can also run the script manually in a loop instead of using Task Scheduler if continuous hourly data is not required.

---

## 6. Example Usage

Once you have collected some data:

```python
import pandas as pd

df = pd.read_csv("crypto_hourly.csv", parse_dates=["timestamp"])
print(df.shape)
print(df["coin"].value_counts())
print(df["timestamp"].min(), "->", df["timestamp"].max())
```

You can also group by coin and plot basic indicators (e.g. BTC price vs RSI over time) in a separate notebook such as `Exploration.ipynb`.

---

## 7. Challenges, Limitations, and Alternatives

### 7.1 API limits and failures

- CoinGecko, Reddit, and Google Trends can all rate limit or temporarily fail.
- When an error occurs, the script:
  - Prints an error message to the console
  - Falls back to `NaN` for the affected feature

This means some rows will be partially incomplete; the **data dictionary** notes which features are more likely to be missing.

### 7.2 Timing & alignment

- Each run is a “snapshot”: we don’t perfectly align all sources to the exact same millisecond.
- Google Trends is aggregated over a small time window (“now 4-H”), so it is a coarse signal.
- Reddit sentiment is based only on top posts in `r/CryptoCurrency` during the last hour and does not represent all crypto social media.

### 7.3 Macro features

- Macro features depend on Alpha Vantage and a free API key. If the key is invalid or rate limits are hit, macro columns will be `NaN`.
- Alternative sources (e.g. Yahoo Finance via `yfinance`) are possible and could replace or supplement the current macro implementation.

### 7.4 Ethical & practical considerations

- All data is scraped from public endpoints, but APIs can change their terms of service at any time.
- This dataset is intended for **research and educational exploration only**, not for automated trading or production systems.

---

## 8. GitHub File Structure

A minimal expected layout:

```text
CryptoSentiment/
├── CryptoMarketSentiment.py
├── crypto_hourly.csv             # created after first run (not in repo by default)
├── data/
│   ├── data_dictionary.csv       # column names, types, descriptions
│   └── sample_crypto_hourly.csv  # optional small sample
├── Exploration.ipynb             # optional: example EDA
├── requirements.txt
├── run_log.txt                   # appended to after each run
└── README.md
```

---

## 9. Help / Common Issues

- `ModuleNotFoundError: No module named 'pycoingecko'`  
  → Run `pip install -r requirements.txt` in the correct environment.

- `HTTPError` or `429 Too Many Requests` from an API  
  → You may have hit rate limits. Wait a bit and run again. Some features will be `NaN` if a provider is temporarily unavailable.

- `KeyError` in Alpha Vantage parsing  
  → Check that `ALPHAVANTAGE_API_KEY` is set and valid. If not, set it or comment out macro feature calls.

- `UnicodeEncodeError` when writing `run_log.txt`  
  → Ensure the file is opened with UTF-8 encoding (already handled in the script).

---

## 10. Authors

- Zain Al Bassam – DSCI 511, Drexel University  
- Muhammad Imran Mushtaq – DSCI 511, Drexel University

---

## 11. Version History

- **v1.0** (December 2025)  
  - Initial release of crypto market + sentiment collection script  
  - Hourly aggregation for top 10 coins  
  - First version of dataset schema and data dictionary

---

## 12. License & Acknowledgments

This project is for **educational use only** as part of DSCI 511 coursework at Drexel University.

Data and APIs:

- CoinGecko API  
- Reddit public endpoints (`r/CryptoCurrency`)  
- Google Trends / pytrends  
- Crypto Fear & Greed Index (alternative.me)  
- Alpha Vantage  

Plus Python libraries: `pandas`, `numpy`, `matplotlib`, `ta`, `vaderSentiment`, `feedparser`, `pytrends`, `yfinance`, `requests`.
