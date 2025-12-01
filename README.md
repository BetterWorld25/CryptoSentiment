# CryptoSentiment
Crypto Market and Sentiment Dataset

This project automatically collects **hourly cryptocurrency market & sentiment data** using only free, publicly available data sources (public API providers).  
It runs hourly using **Windows Task Scheduler** and stores everything in `crypto_hourly.csv`.

---

## Features (Free, No API Keys)
- Top 10 coins by market cap (updated live)
- Hourly price, volume, and market cap (CoinGecko)
- Technical indicators:
  - RSI
  - Volatility (14-period)
  - SMA-20
- Google Trends interest (BTC, ETH) from google API
- Reddit sentiment from r/CryptoCurrency
- Crypto news sentiment (CoinTelegraph & CoinDesk RSS)
- Macro indicators:  (AlphaVantage api) 
  - S&P500 (^GSPC)
  - Gold (GC=F)
  - USD Index (DX-Y.NYB)
- Fear & Greed Index (alternative.me)
- Fully automated hourly execution
- All output saved in **crypto_hourly.csv**
  
---

## Requirment 

pycoingecko==3.1.0
pandas==2.2.3
numpy==2.1.3
matplotlib==3.8.4
ta==0.11.0
vaderSentiment==3.3.2
feedparser==6.0.11
pytrends==4.9.2
yfinance==0.2.48
requests==2.32.3


