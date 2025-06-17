# reader.py

import os
import time
import sqlite3
import pandas as pd
import requests
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "twse_data.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_prices (
                日期 TEXT,
                代號 TEXT,
                名稱 TEXT,
                開盤 REAL,
                最高 REAL,
                最低 REAL,
                收盤 REAL,
                成交金額 REAL,
                資料來源 TEXT,
                下載時間 TEXT,
                PRIMARY KEY (日期, 代號)
            )
        """)
        conn.commit()


def get_twse_day_ohlcv_with_cache(date: datetime):
    filename = f"ohlcv_{date.strftime('%Y%m%d')}.csv"
    file_path = os.path.join(DATA_DIR, filename)

    if os.path.exists(file_path):
        return pd.read_csv(file_path)

    url = "https://www.twse.com.tw/exchangeReport/MI_INDEX"
    params = {"response": "json", "date": date.strftime("%Y%m%d"), "type": "ALL"}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
    except Exception:
        return None

    if data.get("stat") != "OK":
        return None

    for table in data.get("tables", []):
        if "fields" in table and "data" in table and table["fields"][:2] == ["證券代號", "證券名稱"]:
            df = pd.DataFrame(table["data"], columns=table["fields"])
            df = df.rename(columns={
                "證券代號": "代號",
                "證券名稱": "名稱",
                "開盤價": "開盤",
                "最高價": "最高",
                "最低價": "最低",
                "收盤價": "收盤",
                "成交金額": "成交金額"
            })
            df = df[df["代號"].str.match(r"^[1-9]\d{3}$")]
            for col in ["開盤", "最高", "最低", "收盤", "成交金額"]:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "").replace(["--", ""], None), errors='coerce')

            df["日期"] = date.strftime("%Y-%m-%d")
            df["資料來源"] = "TWSE"
            df["下載時間"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df = df[["日期", "代號", "名稱", "開盤", "最高", "最低", "收盤", "成交金額", "資料來源", "下載時間"]].dropna(subset=["收盤"])
            df.to_csv(file_path, index=False, encoding="utf-8-sig")
            return df
    return None


def fetch_valid_twse_ohlcv_last_n_days(n=30, sleep_seconds=0.01):
    results = []
    today = datetime.today()
    found = 0
    delta = 0

    while found < n:
        date = today - timedelta(days=delta)
        delta += 1
        df = get_twse_day_ohlcv_with_cache(date)
        if df is not None and not df.empty:
            results.append(df)
            found += 1
        time.sleep(sleep_seconds)

    return pd.concat(results, ignore_index=True)


def save_to_db(df):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO stock_prices (
                    日期, 代號, 名稱, 開盤, 最高, 最低, 收盤, 成交金額, 資料來源, 下載時間
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(row[col] for col in [
                "日期", "代號", "名稱", "開盤", "最高", "最低", "收盤", "成交金額", "資料來源", "下載時間"]))
        conn.commit()


def fetch_data_to_db(days=60):
    init_db()
    df_all = fetch_valid_twse_ohlcv_last_n_days(n=days)
    save_to_db(df_all)
    print(f"✅ 已儲存 {len(df_all)} 筆資料")

