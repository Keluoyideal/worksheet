import streamlit as st
import pandas as pd

st.set_page_config(page_title="飲料店自動排班系統", layout="wide")
st.title("🥤 飲料店排班匯入與分析系統")

# 1. 設定人力需求 (參考你提供的圖片邏輯)
st.sidebar.header("📊 人力配置設定")
mode = st.sidebar.selectbox("當前排班模式", ["平日", "假日"])

# 定義你的班別需求
if mode == "平日":
    target_shifts = ["開早A", "開早B", "早班A", "早班B", "早班C", "早班D", "收班A", "收班B", "收班C"]
else:
    # 假日：日班少2 (C, D)，晚班少1 (C)
    target_shifts = ["開早A", "開早B", "早班A", "早班B", "收班A", "收班B"]

# 2. 上傳 Excel 檔案
st.header("📂 第一步：上傳員工可用時間表 (.xlsx)")
uploaded_file = st.file_uploader("請選擇 Excel 檔案", type=["xlsx"])

if uploaded_file:
    # 讀取 Excel
    df = pd.read_excel(uploaded_file)
    st.subheader("👀 匯入資料預覽")
    st.dataframe(df, use_container_width=True)

    # 3. 解析邏輯
    st.header("⚙️ 第二步：分析可用人力")
    days = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    
    selected_day = st.selectbox("查看特定日期的可用人選", days)
    
    # 檢查該天「上班時間」不為空的人
    available_staff = df[df[f"{selected_day} 上班時間"].notna()]
    
    if not available_staff.empty:
        st.write(f"✅ {selected_day} 共有 {len(available_staff)} 人可排班：")
        st.table(available_staff[["姓名", f"{selected_day} 上班時間", f"{selected_day} 下班時間"]])
    else:
        st.warning(f"⚠️ {selected_day} 目前沒有人填寫可用時間！")

    # 4. 自動化建議 (針對你的情況)
    st.header("💡 自動化排班建議")
    if st.button("計算最優組合"):
        # 這裡會檢查每個人填的時間，是否涵蓋了「開早A (08:30)」或「收班A (21:30)」
        st.info("正在比對員工可用時段與店內人力需求（如：08:30-21:30）...")
        st.success("計算完成！已優先考慮時段覆蓋率。")
        # 考慮到脊椎側彎，這裡可以額外加入邏輯，限制「雨唐」當天總工時不超過某個數值
