# main.py

from reader import fetch_data_to_db
from analyzer import run_analysis
from plotter import plot_top_stocks
from reporter import export_to_csv, export_to_latest_csv

def main():
    print("🚀 開始執行 TWSE 資料流程")

    # 第一步：抓取並儲存資料
    #fetch_data_to_db(days=30)

    # 第二步：執行分析
    結果 = run_analysis(filters=[
        "10MA最大交叉",
    ])

    # 顯示結果
    print("\n✅ 分析結果：")
    print(結果)

    # 第三步：畫出前 5 名個股圖表
    #print("\n📊 繪製圖表中...")
    #plot_top_stocks(結果, 結果["代號"].unique().tolist(), top_n=5)

    # 第四步：輸出 CSV 報告
    print("\n📝 匯出報告中...")
    export_to_latest_csv(結果)

if __name__ == "__main__":
    main()
