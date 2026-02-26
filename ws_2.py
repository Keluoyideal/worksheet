import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time

# --- 1. 人力需求配置 (平日/假日獨立) ---
WEEKDAY_TARGETS = {"08:30": 1, "09:00": 2, "09:30": 2, "10:00": 4, "10:30": 5, "11:00": 6, "11:30": 6, "12:00": 6, "12:30": 6, "13:00": 6, "13:30": 6, "14:00": 6, "14:30": 6, "15:00": 5, "15:30": 6, "16:00": 5, "16:30": 4, "17:00": 4, "17:30": 4, "18:00": 4, "18:30": 4, "19:00": 3, "19:30": 3, "20:00": 3, "20:30": 3, "21:00": 2}
HOLIDAY_TARGETS = {"08:30": 1, "09:00": 2, "09:30": 2, "10:00": 3, "10:30": 3, "11:00": 4, "11:30": 4, "12:00": 4, "12:30": 4, "13:00": 4, "13:30": 4, "14:00": 4, "14:30": 4, "15:00": 4, "15:30": 4, "16:00": 4, "16:30": 4, "17:00": 4, "17:30": 3, "18:00": 3, "18:30": 3, "19:00": 3, "19:30": 3, "20:00": 2, "20:30": 2, "21:00": 2}

TIME_SLOTS = sorted(WEEKDAY_TARGETS.keys())
FULL_TIME_STAFF = ["鄭力瑜", "康珮庭"]
DAYS = [("週一", "w1"), ("週二", "w2"), ("週三", "w3"), ("週四", "w4"), ("週五", "w5"), ("週六", "w6"), ("週日", "w7")]

st.set_page_config(page_title="專業排班管理系統", layout="wide")

# --- 2. 輔助運算函式 ---
def to_time_obj(val):
    if pd.isna(val) or str(val).strip() in ["休", ""]: return None
    try:
        t_str = str(val).strip()
        if "-" in t_str: t_str = t_str.split('-')[0].strip()
        if ":" in t_str: return datetime.strptime(t_str, "%H:%M").time()
        t_float = float(val)
        h, m = int(t_float * 24), int(round((t_float * 24 - int(t_float * 24)) * 60))
        if m == 60: h, m = h + 1, 0
        return time(min(h, 23), m)
    except: return None

def calc_net_hours(shift):
    if shift == "休" or not shift or "-" not in str(shift): return 0
    try:
        s, e = shift.split('-')
        fmt = "%H:%M"
        start, end = datetime.strptime(s.strip(), fmt), datetime.strptime(e.strip(), fmt)
        dur = (end - start).total_seconds() / 3600
        return max(0, dur - 1.0) if dur >= 8.0 else (max(0, dur - 0.5) if dur >= 4.0 else dur)
    except: return 0

# --- 3. 初始排班演算與初始化 ---
st.title("青山南京三民排班系統")
uploaded_file = st.file_uploader("請上傳同仁回覆.CSV檔", type="csv")

if uploaded_file:
    orig_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    all_names = orig_df['你的名字'].unique().tolist()

    # 初始化 session_state
    if 'main_schedule' not in st.session_state:
        rost_dict = {name: {d[0]: "休" for d in DAYS} for name in all_names}
        consecutive = {name: 0 for name in all_names}

        for d_label, d_key in DAYS:
            is_we = d_label in ["週六", "週日"]
            targets = HOLIDAY_TARGETS if is_we else WEEKDAY_TARGETS
            curr_c = {slot: 0 for slot in TIME_SLOTS}
            assigned = set()

            # A. 正職優先 (避連六)
            for boss in FULL_TIME_STAFF:
                if boss in all_names and consecutive[boss] < 5:
                    row = orig_df[orig_df['你的名字'] == boss].iloc[0]
                    s_s, s_e = to_time_obj(row[f"{d_key} [上班]"]), to_time_obj(row[f"{d_key} [下班]"])
                    if s_s and s_e:
                        rost_dict[boss][d_label] = f"{s_s.strftime('%H:%M')}-{s_e.strftime('%H:%M')}"
                        assigned.add(boss); consecutive[boss] += 1
                        for slot in TIME_SLOTS:
                            if s_s <= datetime.strptime(slot, "%H:%M").time() < s_e: curr_c[slot] += 1

            # B. 兼職填坑
            potential = orig_df[~orig_df['你的名字'].isin(assigned)].copy()
            while True:
                best_pick, max_score = None, 0
                for idx, row in potential.iterrows():
                    name = row['你的名字']
                    if consecutive[name] >= 5: continue
                    s_s, s_e = to_time_obj(row[f"{d_key} [上班]"]), to_time_obj(row[f"{d_key} [下班]"])
                    if not s_s or not s_e: continue
                    score = sum(1 for slot in TIME_SLOTS if s_s <= datetime.strptime(slot, "%H:%M").time() < s_e and curr_c[slot] < targets[slot])
                    if score > max_score: max_score, best_pick = score, (idx, name, s_s, s_e)
                
                if best_pick and max_score > 0:
                    idx, name, s_s, s_e = best_pick
                    rost_dict[name][d_label] = f"{s_s.strftime('%H:%M')}-{s_e.strftime('%H:%M')}"
                    assigned.add(name); consecutive[name] += 1
                    for slot in TIME_SLOTS:
                        if s_s <= datetime.strptime(slot, "%H:%M").time() < s_e: curr_c[slot] += 1
                    potential = potential.drop(idx)
                else: break
            for n in all_names:
                if n not in assigned: consecutive[n] = 0

        st.session_state.main_schedule = pd.DataFrame.from_dict(rost_dict, orient='index').reset_index().rename(columns={'index': '姓名'})

    # --- 4. 功能分頁 ---
    tab_edit, tab_view, tab_chart = st.tabs(["✍️ 手動調整", "🎨 配色預覽", "📊 覆蓋率分析圖"])

    with tab_edit:
        edited_df = st.data_editor(st.session_state.main_schedule, use_container_width=True, height=450, key="editor_vfinal")
        st.session_state.main_schedule = edited_df

    with tab_view:
        view_df = edited_df.copy()
        view_df['總時數'] = view_df.apply(lambda r: sum(calc_net_hours(r[d[0]]) for d in DAYS), axis=1)
        
        def apply_colors(row):
            name, styles = row['姓名'], ['background-color: #f1f5f9; font-weight: bold']
            for d_label, d_key in DAYS:
                val = row[d_label]
                orig_row = orig_df[orig_df['你的名字'] == name]
                orig_start = orig_row[f"{d_key} [上班]"].values[0] if not orig_row.empty else "休"
                if val != "休":
                    try:
                        e_t = datetime.strptime(val.split('-')[1].strip(), "%H:%M").time()
                        # 晚綠 / 早橘
                        bg = "#d4edda" if e_t >= time(21, 0) else "#ffe5d9"
                    except: bg = "#ffffff"
                elif str(orig_start) == "休" or pd.isna(orig_start): bg = "#f8d7da" # 預約休紅
                else: bg = "#fff3cd" # 有班改休黃
                styles.append(f'background-color: {bg}; border: 1px solid #eee')
            styles.append('background-color: #eee')
            return styles
        st.dataframe(view_df.style.apply(apply_colors, axis=1), use_container_width=True, height=500)

    with tab_chart:
        sel_day = st.selectbox("選擇查看日期", [d[0] for d in DAYS])
        is_we = sel_day in ["週六", "週日"]
        targets = HOLIDAY_TARGETS if is_we else WEEKDAY_TARGETS
        
        actual = {slot: 0 for slot in TIME_SLOTS}
        for v in edited_df[sel_day]:
            if v != "休" and "-" in str(v):
                try:
                    s_t = datetime.strptime(v.split('-')[0].strip(), "%H:%M").time()
                    e_t = datetime.strptime(v.split('-')[1].strip(), "%H:%M").time()
                    for slot in TIME_SLOTS:
                        if s_t <= datetime.strptime(slot, "%H:%M").time() < e_t: actual[slot] += 1
                except: pass

        # Plotly 疊加圖：目標為深色框，實際為填滿色
        fig = go.Figure()
        # 目標框 (Outline)
        fig.add_trace(go.Bar(
            x=TIME_SLOTS, y=[targets[s] for s in TIME_SLOTS],
            name='目標人數',
            marker_color='rgba(0,0,0,0)', # 透明填滿
            marker_line_color='#2d3436', # 深色框
            marker_line_width=2,
            offsetgroup=0
        ))
        # 實際填滿 (Infill)
        fig.add_trace(go.Bar(
            x=TIME_SLOTS, y=[actual[s] for s in TIME_SLOTS],
            name='實際排班',
            marker_color='rgba(9, 132, 227, 0.6)', # 藍色填滿
            offsetgroup=0
        ))

        fig.update_layout(
            barmode='overlay', # 關鍵疊加
            title=f"{sel_day} 人力時段覆蓋率分析",
            xaxis_title="時段", yaxis_title="人數",
            plot_bgcolor='white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
