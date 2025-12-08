# CryptoSentiment: Hourly Crypto Market & Sentiment Dataset  
### DSCI 511 — Final Project

This project builds a continuously growing dataset of **hourly cryptocurrency market data**, **technical indicators**, **online sentiment**, and **macro-economic context** using freely available public APIs.  

The dataset is produced by a single automated script:  
`crypto_data_acquisition.py`  

Each execution adds one row per top-10 cryptocurrency to `crypto_hourly.csv`, enabling time-series analysis, forecasting, and sentiment–price relationship studies.

---

## 1. Project Overview

The goal of this project is to create a reproducible dataset that integrates:

- **Market data** (price, 24h change, volume, market cap)  
- **Technical indicators** (RSI, volatility, SMA-20)  
- **Attention metrics** (Google Trends)  
- **Online sentiment** (Reddit VADER scores, Fear & Greed Index)  
- **Macro environment** (S&P500, Gold, USD Index)

This dataset can support many downstream tasks, including exploratory data analysis, econometric modeling, crypto–sentiment correlation studies, and machine-learning prediction pipelines.

---

## 2. Data Sources

All data sources used in this project are **public and free**:

| Category | Source | Description |
|---------|--------|-------------|
| Crypto Market Data | CoinGecko API | Prices, 24h change, volume, market cap, intraday price series |
| Technical Indicators | Computed locally | RSI(14), Volatility(14), SMA-20 |
| Search Trends | Google Trends (pytrends) | Search interest for “Bitcoin” and “Ethereum” |
| Market Sentiment | Reddit (public JSON) | Sentiment of top posts in r/CryptoCurrency |
| Fear & Greed | Alternative.me API | Global crypto sentiment index |
| Macro Indicators | Alpha Vantage API | SP500 proxy (SPY), Gold (GLD), USD Index |

A full description of every dataset field appears in:  
**`data/data_dictionary.csv`**

---

## 3. Dataset Contents

Each run appends **10 new rows** (one for each top-10 cryptocurrency) to:

```
crypto_hourly.csv
```

### Main Fields (see data_dictionary.csv for details)

- Timestamp  
- Coin ID  
- Price, 24h change, volume, market cap  
- RSI(14), Volatility(14), SMA-20  
- Google Trends (BTC/ETH)  
- Fear & Greed Index  
- Reddit sentiment  
- SP500, Gold, USD Index  

Missing values are stored as **NaN** (e.g., API rate limits or temporary outages).

---

## 4. Installation & Setup

### 4.1 Clone the Repository

```bash
git clone https://github.com/BetterWorld25/CryptoSentiment.git
cd CryptoSentiment
```

### 4.2 Create & Activate Virtual Environment

**PowerShell:**
```powershell
python -m venv venv
venv\Scripts\activate
```

If activation is blocked:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.4 Alpha Vantage API Key

```powershell
$env:ALPHAVANTAGE_API_KEY="YOUR_KEY"
```

```bash
export ALPHAVANTAGE_API_KEY="YOUR_KEY"
```

Macro features are optional — missing values become **NaN**.

---

## 5. Running the Data Collection Script

```bash
python crypto_data_acquisition.py
```

The script will:

1. Fetch market & intraday data  
2. Compute technical indicators  
3. Add Google Trends values  
4. Add Fear & Greed Index  
5. Add Reddit sentiment  
6. Add macro indicators  
7. Append results to `crypto_hourly.csv`  
8. Log run info in `run_log.txt`

---

## 6. Automating Hourly Collection (Windows)

1. Open **Task Scheduler**  
2. Create **Basic Task**  
3. Trigger → Daily → Repeat every **1 hour**  
4. Action → Start a Program  
5. Program: `python`  
6. Arguments: `C:\path\to\crypto_data_acquisition.py`  
7. Start in: project folder  

---

## 7. Example Usage

```python
import pandas as pd

df = pd.read_csv("crypto_hourly.csv", parse_dates=["timestamp"])
print(df.shape)
print(df['coin'].value_counts())
print(df['timestamp'].min(), df['timestamp'].max())
```

---

## 8. Limitations & Considerations

### API Reliability
Some APIs may fail or rate-limit. Script substitutes missing values with **NaN**.

### Timing Misalignment
Data is collected per snapshot, not synchronized across APIs.

### Sentiment Scope
Reddit sentiment is based only on r/CryptoCurrency top posts (last hour).

### Intended Use
Dataset is for **education and research only**, not for financial decision-making.

---

## 9. Project Structure

```
CryptoSentiment/
│
├── crypto_data_acquisition.py
│
├── data/
│   ├── data_dictionary.csv
│   └── sample_crypto_hourly.csv
│   └── crypto_hourly.csv
│
├── requirements.txt
└── README.md
```

---

## 10. Authors

- Zain Al Bassam – DSCI 511, Drexel University  
- Muhammad Imran Mushtaq – DSCI 511, Drexel University

---

## 11. Version History

**v1.0 (Dec 2025)**  
- Initial release  
- Hourly crypto sentiment + macro dataset  
- Added technical indicators & Google Trends  

---

## 12. License & Acknowledgments

Code in this repository is released under the MIT License.
Data generated using this code is for educational and academic use only, and must comply with the terms of upstream APIs (CoinGecko, Reddit, Google Trends, Alpha Vantage, etc.).
