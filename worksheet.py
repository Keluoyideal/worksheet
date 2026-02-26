import streamlit as st
import pandas as pd

st.set_page_config(page_title="飲料店自動排班系統", layout="wide")
st.title("🥤 飲料店自動排班系統 (Excel 匯入版)")

# 1. 定義店內需求 (參考你提供的圖片)
# 格式: (班別名稱, 開始時間, 結束時間)
SHIFTS_DEMAND = {
    "開早A": ("08:30", "16:00"),
    "早班A": ("10:00", "19:00"),
    "收班A": ("16:00", "21:30")
}

# 2. 上傳你剛剛上傳的那份 CSV/XLSX
uploaded_file = st.file_uploader("上傳「表單回覆」檔案", type=["csv", "xlsx"])

if uploaded_file:
    # 讀取資料
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("🗓️ 原始排班資料預覽")
    st.dataframe(df.head(), use_container_width=True)

    # 3. 選擇要處理的日期
    days = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    target_day = st.selectbox("請選擇要產生的日期", days)

    # 4. 核心演算法：時段比對
    st.subheader(f"🔍 {target_day} 人力分配分析")
    
    # 假設 Excel 欄位名稱是 "姓名", "週一 上班時間", "週一 下班時間"
    start_col = f"{target_day} 上班時間"
    end_col = f"{target_day} 下班時間"

    if start_col in df.columns:
        # 過濾出當天有空的人
        available = df[df[start_col].notna()].copy()
        
        # 建立分配清單
        assignments = []
        for shift_name, (s_time, e_time) in SHIFTS_DEMAND.items():
            # 找出誰的時間能涵蓋這個班別 (簡單邏輯：上班 <= 班別開始 且 下班 >= 班別結束)
            match = available[
                (available[start_col] <= s_time) & 
                (available[end_col] >= e_time)
            ]
            
            if not match.empty:
                # 這裡可以加入權重，例如你(雨唐)若這週時數已多，就排別人
                chosen_one = match.iloc[0]["姓名"]
                assignments.append({"班別": shift_name, "時段": f"{s_time}-{e_time}", "安排人員": chosen_one})
                # 已經排的人就從當天可用名單移除，避免重疊
                available = available[available["姓名"] != chosen_one]
            else:
                assignments.append({"班別": shift_name, "時段": f"{s_time}-{e_time}", "安排人員": "❌ 缺人！"})

        st.table(pd.DataFrame(assignments))
    else:
        st.error(f"找不到 {target_day} 的欄位，請檢查 Excel 標題是否正確。")
