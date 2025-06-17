# analyzer.py

import os
import sqlite3
import pandas as pd
import numpy as np

DB_PATH = os.path.join(os.getcwd(), "data", "twse_data.db")

# === 讀取資料並計算 MA ===
def read_df(ma_list=[5, 10, 20]):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT * FROM stock_prices", conn)
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.sort_values(["代號", "日期"])
    for ma in ma_list:
        df[f"{ma}MA"] = df["收盤"].rolling(window=ma).mean()
    return df

  
# === 讀取部分資料並計算 MA ===
def read_df_with_filters(ma_list=[5, 10, 20], start_date=None, days=None):
    with sqlite3.connect(DB_PATH) as conn:
        query = "SELECT * FROM stock_prices"
        if start_date:
            query += f" WHERE 日期 >= '{start_date}'"
        elif days:
            extra = max(ma_list)
            query += f"""
                WHERE 日期 IN (
                    SELECT 日期 FROM stock_prices 
                    GROUP BY 日期 ORDER BY 日期 DESC LIMIT {days + extra}
                )
            """
        df = pd.read_sql(query, conn)

    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    df = df.sort_values(["代號", "日期"]).copy()

    for ma in ma_list:
        df[f"{ma}MA"] = df.groupby("代號")["收盤"].transform(lambda x: x.rolling(window=ma).mean())

    return df


# === 篩選器定義 ===
def 篩選_多頭排列(df):
    cond = (df["收盤"] > df["5MA"]) & (df["5MA"] > df["10MA"]) & (df["10MA"] > df["20MA"])
    return df[cond]

def 篩選_5日內有發生5MA等於10MA(df):
    result_ids = []
    for code, group in df.groupby("代號"):
        recent = group.tail(5)
        if any(np.isclose(recent["5MA"], recent["10MA"], atol=0.001)):
            result_ids.append(code)
    return df[df["代號"].isin(result_ids)]

def 篩選_10MA最大交叉(df):
    result_ids = []
    for code, group in df.groupby("代號"):
        recent = group.tail(5).copy()
        if len(recent) < 5:
            continue
        sorted_10ma = recent.sort_values("10MA", ascending=False)
        max_row = sorted_10ma.iloc[0]
        second_row = sorted_10ma.iloc[1]
        today = recent.iloc[-1]
        if (
            np.isclose(second_row["5MA"], second_row["10MA"], atol=0.001)
            and today["日期"] == max_row["日期"]
        ):
            result_ids.append(code)
    return df[df["代號"].isin(result_ids)]

def 篩選_10MA最大5MA等於20MA(df):
    result_ids = []
    for code, group in df.groupby("代號"):
        recent = group.tail(5).copy()
        if len(recent) < 5:
            continue
        sorted_10ma = recent.sort_values("10MA", ascending=False)
        max_row = sorted_10ma.iloc[0]
        second_row = sorted_10ma.iloc[1]
        today = recent.iloc[-1]
        if (
            np.isclose(second_row["5MA"], second_row["20MA"], atol=0.001)
            and today["日期"] == max_row["日期"]
        ):
            result_ids.append(code)
    return df[df["代號"].isin(result_ids)]

def 篩選_10MA最大10MA等於20MA(df):
    result_ids = []
    for code, group in df.groupby("代號"):
        recent = group.tail(5).copy()
        if len(recent) < 5:
            continue
        sorted_10ma = recent.sort_values("10MA", ascending=False)
        max_row = sorted_10ma.iloc[0]
        second_row = sorted_10ma.iloc[1]
        today = recent.iloc[-1]
        if (
            np.isclose(second_row["10MA"], second_row["20MA"], atol=0.001)
            and today["日期"] == max_row["日期"]
        ):
            result_ids.append(code)
    return df[df["代號"].isin(result_ids)]

# === 分析主函數（AND） ===
def run_analysis(filters):
    df = read_df_with_filters(days=30)
    篩選器 = {
        "多頭排列": 篩選_多頭排列,
        "5日5MA=10MA": 篩選_5日內有發生5MA等於10MA,
        "10MA最大交叉": 篩選_10MA最大交叉,
        "10MA最大5MA=20MA": 篩選_10MA最大5MA等於20MA,
        "10MA最大10MA=20MA": 篩選_10MA最大10MA等於20MA,
    }
    fns = [篩選器[name] for name in filters if name in 篩選器]
    for f in fns:
        df = f(df)
    if not df.empty:
        df["篩選"] = " & ".join(filters)
    return df

# === 分析主函數（OR） ===
def run_analysis_or(filters):
    df = read_df_with_filters(days=30)
    篩選器 = {
        "多頭排列": 篩選_多頭排列,
        "5日5MA=10MA": 篩選_5日內有發生5MA等於10MA,
        "10MA最大交叉": 篩選_10MA最大交叉,
        "10MA最大5MA=20MA": 篩選_10MA最大5MA等於20MA,
        "10MA最大10MA=20MA": 篩選_10MA最大10MA等於20MA,
    }
    fns = [篩選器[name] for name in filters if name in 篩選器]
    results = [f(df) for f in fns]
    df_out = pd.concat(results).drop_duplicates().reset_index(drop=True)
    if not df_out.empty:
        df_out["篩選"] = " | ".join(filters)
    return df_out
