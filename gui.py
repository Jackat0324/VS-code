import tkinter as tk
from tkinter import messagebox
from analyzer import run_analysis, run_analysis_or
from reader import fetch_data_to_db
from reporter import export_to_latest_csv

def run_fetch():
    fetch_data_to_db(days=30)
    messagebox.showinfo("完成", "資料擷取並儲存完成！")

def run_analyze():
    filters = []
    if var1.get(): filters.append("多頭排列")
    if var2.get(): filters.append("5日5MA=10MA")
    if var3.get(): filters.append("10MA最大交叉")
    if var4.get(): filters.append("10MA最大5MA=20MA")
    if var5.get(): filters.append("10MA最大10MA=20MA")

    if not filters:
        messagebox.showwarning("請選擇", "請至少選擇一個篩選條件")
        return

    global last_result
    last_result = run_analysis_or(filters)
    messagebox.showinfo("分析完成", f"共 {len(last_result)} 筆結果")

def export_csv():
    global last_result
    if last_result is not None and not last_result.empty:
        export_to_latest_csv(last_result)
        messagebox.showinfo("匯出完成", "已匯出最新報告")
    else:
        messagebox.showwarning("沒有資料", "請先執行分析")

app = tk.Tk()
app.title("TWSE 分析工具")
app.geometry("360x450")
app.option_add("*Font", "Helvetica 14")

tk.Button(app, text="📥 擷取資料", command=run_fetch, width=20, height=2).pack(pady=10)

tk.Label(app, text="📊 篩選條件", font=("Helvetica", 16, "bold")).pack(pady=5)
var1 = tk.BooleanVar()
var2 = tk.BooleanVar()
var3 = tk.BooleanVar()
var4 = tk.BooleanVar()
var5 = tk.BooleanVar()
tk.Checkbutton(app, text="多頭排列", variable=var1).pack(anchor='w', padx=40)
tk.Checkbutton(app, text="5日5MA=10MA", variable=var2).pack(anchor='w', padx=40)
tk.Checkbutton(app, text="10MA最大交叉", variable=var3).pack(anchor='w', padx=40)
tk.Checkbutton(app, text="10MA最大5MA=20MA", variable=var4).pack(anchor='w', padx=40)
tk.Checkbutton(app, text="10MA最大10MA=20MA", variable=var5).pack(anchor='w', padx=40)

tk.Button(app, text="🚀 執行分析", command=run_analyze, width=20, height=2).pack(pady=15)
tk.Button(app, text="💾 匯出 CSV", command=export_csv, width=20, height=2).pack()

last_result = None
app.mainloop()
