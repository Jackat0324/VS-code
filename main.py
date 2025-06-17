# main.py
import pandas as pd
from reader import fetch_data_to_db
from analyzer import run_analysis
from plotter import plot_top_stocks
from reporter import export_to_latest_csv

def main():
    print("🚀 開始執行 TWSE 資料流程")

    # 🟡 第一步：擷取資料（如已抓過可註解）
    # fetch_data_to_db(days=30)

    # 🟢 第二步：定義條件組合（每個子清單為一組 AND 條件）
    filter_groups = [
        ["多頭排列", "10MA最大交叉"],       # 同時符合這兩個條件
        ["5日5MA=10MA", "多頭排列"],
        ["10MA最大5MA=20MA"],
        ["10MA最大10MA=20MA"]
    ]

    # 🟢 第三步：執行分析並標記條件名稱
    df_list = []
    for conds in filter_groups:
        df = run_analysis(filters=conds)  # 執行 AND 分析
        if not df.empty:
            df["來源"] = " + ".join(conds)
            df_list.append(df)

    # 🔴 沒有資料就結束
    if not df_list:
        print("⚠ 沒有符合任何條件的結果")
        return

    # 🟢 第四步：彙整結果與條件標籤
    df_all = pd.concat(df_list).drop_duplicates(subset=["日期", "代號", "名稱"])
    df_grouped = df_all.groupby(["日期", "代號", "名稱"])["來源"] \
        .apply(lambda x: " + ".join(sorted(set(x)))).reset_index()

    df_unique = df_all.drop(columns=["來源"]).drop_duplicates(subset=["日期", "代號", "名稱"])
    df_result = df_unique.merge(df_grouped, on=["日期", "代號", "名稱"])
    df_result = df_result.rename(columns={"來源": "篩選"})

    # 🟢 顯示分析結果
    print("\n✅ 分析結果：")
    print(df_result)

    # 🟡 第五步：畫圖（選擇性）
    # plot_top_stocks(df_result, df_result["代號"].unique().tolist(), top_n=5)

    # 🟢 第六步：匯出報告
    print("\n📝 匯出報告中...")
    export_to_latest_csv(df_result)

if __name__ == "__main__":
    main()
