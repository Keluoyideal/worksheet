import streamlit as st
import pandas as pd

st.title("🥤 飲料店自動排班系統")

# 設定人力需求（參考你的圖片）
st.sidebar.header("設定人力配置")
mode = st.sidebar.radio("排班模式", ["平日", "假日"])

# 平日與假日的邏輯切換
if mode == "平日":
    shifts = {
        "班別": ["開早A", "開早B", "早班A", "早班B", "早班C", "早班D", "收班A", "收班B", "收班C"],
        "人數": [1, 1, 1, 1, 1, 1, 1, 1, 1]
    }
else:
    # 假日：日班少2人，晚班少1人
    shifts = {
        "班別": ["開早A", "開早B", "早班A", "早班B", "收班A", "收班B"],
        "人數": [1, 1, 1, 1, 1, 1]
    }

st.write(f"### 當前為：{mode} 需求表")
st.table(pd.DataFrame(shifts))

# 讓店長（你）手動輸入本週有誰
staff_input = st.text_area("請輸入本週員工名單（以逗號分開）", "雨唐, 小明, 小華, 阿美, 老王")
staff_list = [s.strip() for s in staff_input.split(",")]

if st.button("生成排班"):
    st.balloons()
    st.success("排班已根據人力配置自動計算完成！")
    # 這裡未來可以放入更複雜的分配演算法
    st.write("📌 這只是預覽介面，之後我們可以串接 Google Sheets API 來自動抓取資料。")
    