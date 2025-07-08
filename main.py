import requests
import time
from datetime import datetime

# === 參數區 ===
TELEGRAM_TOKEN = "7828733751:AAE3SS52AxkoZ7gkXlM0fRAOH9SL6Kj0zek"
TELEGRAM_CHAT_ID = "5693384529"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT","AAVEUSDT","XRPUSDT","SUIUSDT","LINKUSDT","ICPUSDT"]  # 可自行擴增
INTERVAL = "15m"
LIMIT = 50  # 保險起見抓多一點
SLEEP_SECONDS = 60  # 每幾秒輪巡一次

# === 發送 telegram 訊息 ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, data=data)

# === 抓 K 線資料 ===
def get_klines(symbol, interval="15m", limit=50):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    return [{
        "open_time": k[0],
        "open": float(k[1]),
        "high": float(k[2]),
        "low": float(k[3]),
        "close": float(k[4]),
        "volume": float(k[5]),
    } for k in data]

# === 判斷信號 ===
def check_signal(k1, k2):
    # Bullish Engulfing
    if (k1['close'] < k1['open'] and
        k2['close'] > k2['open'] and
        k2['open'] < k1['close'] and
        k2['close'] > k1['open'] and
        k2['volume'] < k1['volume']):
        return "BP"
    
    # Bearish Engulfing
    if (k1['close'] > k1['open'] and
        k2['close'] < k2['open'] and
        k2['open'] > k1['close'] and
        k2['close'] < k1['open'] and
        k2['volume'] < k1['volume']):
        return "SP"
    
    return None

# === 主迴圈 ===
def main():
    print("🔍 開始監控中...")

    while True:
        for symbol in SYMBOLS:
            try:
                data = get_klines(symbol, INTERVAL, LIMIT)
                k1, k2 = data[-2], data[-1]
                signal = check_signal(k1, k2)
                if signal:
                    ts = datetime.fromtimestamp(k2['open_time'] / 1000).strftime("%Y-%m-%d %H:%M")
                    msg = f"🚨 {symbol} 出現 {signal} 信號\n時間：{ts}\n價格：{k2['close']:.2f}"
                    print(msg)
                    send_telegram_message(msg)
            except Exception as e:
                print(f"[錯誤] {symbol}: {e}")
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
