# 1. WINDOWS ASYNCIO FIX
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 2. IMPORTS
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timezone
import pandas as pd, numpy as np, requests, os, time
from pytrends.request import TrendReq
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# 3. INITIALIZE APIS
cg = CoinGeckoAPI()
pytrends = TrendReq(hl="en-US", tz=0)
analyzer = SentimentIntensityAnalyzer()

# 4. RSI FUNCTION
def compute_rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# 5. FETCH COIN DATA
def fetch_top10_data():
    rows = []
    top10 = cg.get_coins_markets(vs_currency="usd", per_page=10)
    coins = [c["id"] for c in top10]

    for coin in coins:
        try:
            market = cg.get_coins_markets(vs_currency="usd", ids=coin)[0]
            hist = cg.get_coin_market_chart_by_id(id=coin, vs_currency="usd", days=1)

            prices = pd.DataFrame(hist["prices"], columns=["ts", "price"])
            prices["price"] = prices["price"].astype(float)

            prices["rsi"] = compute_rsi(prices["price"])
            prices["vol"] = prices["price"].pct_change().rolling(14).std()
            prices["sma20"] = prices["price"].rolling(20).mean()

            last = prices.dropna().iloc[-1]

            rows.append({
                "timestamp": datetime.now(timezone.utc),
                "coin": coin,
                "price": market["current_price"],
                "change_24h_%": market["price_change_percentage_24h"],
                "volume_24h": market["total_volume"],
                "market_cap": market["market_cap"],
                "rsi": last["rsi"],
                "volatility": last["vol"],
                "sma_20": last["sma20"],
            })
            time.sleep(0.25)

        except Exception as e:
            print(f"Error fetching {coin}:", e)

    return pd.DataFrame(rows)

# 6. GOOGLE TRENDS
def add_google_trends(df):
    try:
        pytrends.build_payload(["Bitcoin", "Ethereum"], timeframe="now 4-H")
        time.sleep(2)
        tdf = pytrends.interest_over_time()

        if tdf.empty:
            df["google_trend_btc"] = np.nan
            df["google_trend_eth"] = np.nan
        else:
            last = tdf.iloc[-1]
            df["google_trend_btc"] = last.get("Bitcoin", np.nan)
            df["google_trend_eth"] = last.get("Ethereum", np.nan)

    except Exception as e:
        print("Google Trends error:", e)
        df["google_trend_btc"] = np.nan
        df["google_trend_eth"] = np.nan

    return df

# 7. FEAR & GREED INDEX
def add_fear_greed(df):
    try:
        fg = requests.get("https://api.alternative.me/fng/").json()
        df["fear_greed_index"] = float(fg["data"][0]["value"])
    except:
        df["fear_greed_index"] = np.nan
    return df

# 8. REDDIT SENTIMENT
def add_reddit_sentiment(df):
    try:
        time.sleep(2)

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }

        r = requests.get(
            "https://www.reddit.com/r/CryptoCurrency/top.json?limit=50&t=hour",
            headers=headers,
            timeout=10
        )

        if r.status_code != 200:
            df["reddit_sentiment"] = np.nan
            return df

        try:
            data_json = r.json()

            if "data" not in data_json:
                df["reddit_sentiment"] = np.nan
            else:
                titles = [p["data"]["title"] for p in data_json["data"]["children"]]
                df["reddit_sentiment"] = np.mean([
                    analyzer.polarity_scores(t)["compound"] for t in titles
                ])

        except Exception as e:
            print("Reddit JSON decode error:", e)
            df["reddit_sentiment"] = np.nan

    except Exception as e:
        print("Reddit error:", e)
        df["reddit_sentiment"] = np.nan

    return df

# 9. ALPHA VANTAGE
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "")

def get_global_quote(symbol):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
        data = requests.get(url).json()

        # prevent KeyError
        if "Global Quote" not in data or "05. price" not in data["Global Quote"]:
            return np.nan

        return float(data["Global Quote"]["05. price"])

    except Exception:
        return np.nan


def get_usd_index():
    try:
        url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=EUR&apikey={API_KEY}"
        data = requests.get(url).json()

        # prevent KeyError
        if "Realtime Currency Exchange Rate" not in data or \
           "5. Exchange Rate" not in data["Realtime Currency Exchange Rate"]:
            return np.nan

        rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
        return (1 / rate) * 100

    except Exception:
        return np.nan


def add_macro(df):
    df["SP500"] = get_global_quote("SPY")
    df["Gold"] = get_global_quote("GLD")
    df["USD_Index"] = get_usd_index()
    return df

# 10. MAIN EXECUTION
df = fetch_top10_data()
df = add_google_trends(df)
df = add_fear_greed(df)
df = add_reddit_sentiment(df)
df = add_macro(df)

# 11. SAVE RESULTS
file = "crypto_hourly.csv"

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

if os.path.exists(file):
    old = pd.read_csv(file)
    old["timestamp"] = pd.to_datetime(old["timestamp"], errors="coerce")

    combined = pd.concat([old, df]).drop_duplicates(subset=["coin", "timestamp"])
    combined.to_csv(file, index=False)

else:
    df.to_csv(file, index=False)

print("Data saved at", datetime.utcnow())

# 12. LOG
with open("run_log.txt", "a", encoding="utf-8") as f:
    f.write(
        f"[{datetime.utcnow()}] Hourly crypto data collected. Rows added: {len(df)}\n"
    )

print("Logged run")
