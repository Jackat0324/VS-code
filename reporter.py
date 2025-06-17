# reporter.py

import os
import pandas as pd
from datetime import datetime

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# === 將分析結果輸出為 CSV 檔案 ===
def export_to_csv(df: pd.DataFrame, filename: str = None) -> str:
    if filename is None:
        today = datetime.today().strftime("%Y%m%d")
        filename = f"report_{today}.csv"

    file_path = os.path.join(DATA_DIR, filename)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"📄 已輸出分析報告至：{file_path}")
    return file_path


# === 將分析結果輸出為 CSV 檔案（僅保留資料中最新日期） ===
def export_to_latest_csv(df: pd.DataFrame, filename: str = None) -> str:
    latest_date = df["日期"].max()
    df_today = df[df["日期"] == latest_date][["日期", "代號", "名稱", "篩選"]]

    if filename is None:
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"report_{latest_date.strftime('%Y%m%d')}_{timestamp}.csv"

    file_path = os.path.join(DATA_DIR, filename)
    df_today.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"📄 已輸出分析報告至：{file_path}（僅保留 {latest_date.date()} 資料）")
    return file_path