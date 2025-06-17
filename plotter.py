# plotter.py

import os
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.getcwd(), "data")

# === 畫出某股票收盤與均線走勢圖 ===
def plot_stock(df: pd.DataFrame, stock_id: str, save: bool = False):
    df_stock = df[df["代號"] == stock_id].copy()
    df_stock = df_stock.sort_values("日期")

    if df_stock.empty:
        print(f"⚠ 找不到代號 {stock_id} 的資料")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(df_stock["日期"], df_stock["收盤"], label="收盤價", linewidth=1.5)
    for ma in [5, 10, 20]:
        ma_col = f"{ma}MA"
        if ma_col in df_stock.columns:
            plt.plot(df_stock["日期"], df_stock[ma_col], label=f"{ma}MA")

    plt.title(f"{stock_id} 收盤與移動平均線走勢圖")
    plt.xlabel("日期")
    plt.ylabel("價格")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save:
        file_path = os.path.join(DATA_DIR, f"plot_{stock_id}.png")
        plt.savefig(file_path)
        print(f"📈 已儲存圖表：{file_path}")
    else:
        plt.show()

# === 畫出多支股票的圖（限制前 N 支）===
def plot_top_stocks(df: pd.DataFrame, stock_ids: list, top_n=5):
    for stock_id in stock_ids[:top_n]:
        plot_stock(df, stock_id, save=True)