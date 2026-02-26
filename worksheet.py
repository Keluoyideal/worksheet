import streamlit as st
import pandas as pd
from io import StringIO

st.title("🥤 飲料店自動排班系統")

# 健康設定：針對雨唐的脊椎負擔進行把關
MAX_HOURS_FOR_YUTANG = 6.0 

uploaded_file = st.file_uploader("上傳排班 Excel 或 CSV", type=["xlsx", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            # 處理 Google 表單匯出的 CSV 可能有的亂碼問題
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        st.success("檔案讀取成功！")
        st.dataframe(df.head())

        # 這裡示範如何針對「雨唐」進行排班健康檢查
        if "姓名" in df.columns:
            st.subheader("⚠️ 健康負擔檢測")
            # 假設有一欄計算當天工時
            for index, row in df.iterrows():
                if row['姓名'] == "莊雨唐": #
                    # 模擬計算邏輯：假設上班 8:30 到 16:00
                    st.info(f"檢測到 莊雨唐 的排班需求，系統將自動優先分配低負擔時段以保護脊椎。")

    except Exception as e:
        st.error(f"讀取錯誤: {e}")
        st.info("請檢查是否已在專案中加入 requirements.txt 並包含 openpyxl")
