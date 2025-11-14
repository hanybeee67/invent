import streamlit as st
import pandas as pd
import os

# ---------------- 기본 설정 ----------------
st.set_page_config(
    page_title="Everest 재고관리 시스템",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- 글로벌 스타일 (CSS) ----------------
CUSTOM_CSS = """
<style>
/* 전체 앱 배경 */
.stApp {
    background: radial-gradient(circle at top left, #1f2937 0, #020617 45%, #020617 100%);
    color: #e5e7eb;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
}

/* 메인 컨테이너 */
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 2.5rem;
    max-width: 1200px;
}

/* 제목 스타일 */
h1, h2, h3, h4 {
    color: #e5e7eb;
    letter-spacing: 0.02em;
}

/* 설명 텍스트 */
p, .stMarkdown {
    color: #cbd5f5;
}

/* 카드 공통 */
.card {
    background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(15,23,42,0.9));
    padding: 1.6rem 1.8rem;
    border-radius: 18px;
    border: 1px solid rgba(148,163,184,0.4);
    box-shadow: 0 22px 55px rgba(15,23,42,0.95);
    margin-bottom: 1.8rem;
}

/* 상단 인포 카드 (메트릭 느낌) */
.metric-card {
    background: radial-gradient(circle at top left, rgba(30,64,175,0.35), rgba(15,23,42,0.98));
    padding: 1.0rem 1.2rem;
    border-radius: 14px;
    border: 1px solid rgba(129,140,248,0.6);
    box-shadow: 0 16px 40px rgba(15,23,42,0.9);
}

/* 탭 스타일 살짝 보정 */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.2rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #020617);
    border-right: 1px solid rgba(30,64,175,0.7);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* 위젯 라벨 */
label, .stSelectbox, .stTextInput, .stNumberInput {
    font-size: 0.9rem;
}

/* 데이터프레임 배경 톤다운 */
[data-testid="stDataFrame"] {
    background-color: rgba(15,23,42,0.9);
    border-radius: 14px;
    border: 1px solid rgba(148,163,184,0.35);
}

/* 체크박스 라벨 색 */
.stCheckbox label {
    color: #e5e7eb;
}

/* 다운로드 버튼 커스텀 느낌 */
.stDownloadButton button, .stButton button {
    border-radius: 999px;
    padding: 0.45rem 1.0rem;
    border: 1px solid rgba(148,163,184,0.7);
    background: radial-gradient(circle at top left, #1d4ed8, #1e293b);
    color: #e5e7eb;
    font-weight: 500;
}
.stDownloadButton button:hover, .stButton button:hover {
    border-color: #a5b4fc;
    box-shadow: 0 0 0 1px rgba(129,140,248,0.9);
}

/* 경고/정보 박스 살짝 투명하게 */
div[data-testid="stAlert"] {
    background-color: rgba(15,23,42,0.85);
    border-radius: 12px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------- 설정 ----------------
DATA_FILE = "inventory_data.csv"  # 재고 데이터 저장 파일 이름

branches = ["동대문", "굿모닝시티", "양재", "수원영통", "동탄", "영등포", "룸비니"]
categories = ["육류", "야채", "해산물", "향신료", "소스", "곡류/면", "음료", "포장재", "기타"]

# ---------------- 데이터 로드/저장 함수 ----------------
def load_inventory():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            expected_cols = ["지점", "품목명", "카테고리", "단위", "현재수량", "최소수량", "비고"]
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = ""
            df = df[expected_cols]
            return df
        except Exception:
            return pd.DataFrame(columns=["지점", "품목명", "카테고리", "단위", "현재수량", "최소수량", "비고"])
    else:
        return pd.DataFrame(columns=["지점", "품목명", "카테고리", "단위", "현재수량", "최소수량", "비고"])


def save_inventory(df: pd.DataFrame):
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


# ---------------- 세션 초기화 ----------------
if "inventory" not in st.session_state:
    st.session_state.inventory = load_inventory()

# ---------------- 상단 헤더 ----------------
st.markdown(
    """
<div class="card" style="margin-bottom: 1.2rem;">
  <div style="display:flex; align-items:center; justify-content:space-between; gap:1rem;">
    <div>
      <h1 style="margin-bottom:0.2rem;">📦 EVEREST 재고관리 시스템</h1>
      <p style="margin-top:0.2rem; color:#9ca3af;">
        지점별·품목별 재고를 한눈에 관리하고, 부족 재고를 빠르게 확인할 수 있는 내부용 대시보드입니다.
      </p>
    </div>
    <div class="metric-card">
      <div style="font-size:0.85rem; color:#9ca3af;">현재 저장된 품목 수</div>
      <div style="font-size:1.4rem; font-weight:600; color:#e5e7eb; margin-top:0.1rem;">
        {count} 개
      </div>
    </div>
  </div>
</div>
""".format(count=len(st.session_state.inventory)),
    unsafe_allow_html=True,
)

tab_input, tab_view = st.tabs(["✏ 재고 입력/수정", "📊 재고 현황 보기"])

# =========================================================
# 🔹 탭 1: 재고 입력 / 수정
# =========================================================
with tab_input:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("재고 등록 / 수정")

    col1, col2, col3 = st.columns(3)

    with col1:
        branch = st.selectbox("지점 선택", branches, key="inv_branch")
        name = st.text_input("품목명", key="inv_name")
        category = st.selectbox("카테고리", categories, key="inv_cat")

    with col2:
        unit = st.text_input("단위 (예: kg, 개, 박스)", key="inv_unit")
        qty = st.number_input("현재 수량", min_value=0.0, step=1.0, key="inv_qty")
        min_qty = st.number_input("최소 필요 수량", min_value=0.0, step=1.0, key="inv_min")

    with col3:
        note = st.text_input("비고", key="inv_note")
        save_btn = st.button("💾 재고 등록 / 업데이트")
        del_btn = st.button("🗑 선택 품목 삭제 (지점+품목 기준)")

    # 저장 / 업데이트
    if save_btn:
        if name.strip() == "":
            st.warning("품목명을 입력하세요.")
        else:
            df = st.session_state.inventory.copy()
            mask = (df["지점"] == branch) & (df["품목명"] == name)

            new_row = {
                "지점": branch,
                "품목명": name,
                "카테고리": category,
                "단위": unit,
                "현재수량": qty,
                "최소수량": min_qty,
                "비고": note,
            }

            if mask.any():
                df.loc[mask, :] = list(new_row.values())
                st.success("기존 품목 정보가 업데이트되었습니다.")
            else:
                df = pd.concat(
                    [df, pd.DataFrame([new_row])],
                    ignore_index=True
                )
                st.success("새 재고 품목이 등록되었습니다.")

            st.session_state.inventory = df
            save_inventory(df)

    # 삭제
    if del_btn:
        df = st.session_state.inventory.copy()
        mask = (df["지점"] == branch) & (df["품목명"] == name)
        if mask.any():
            df = df[~mask].reset_index(drop=True)
            st.session_state.inventory = df
            save_inventory(df)
            st.success(f"{branch} / {name} 품목이 삭제되었습니다.")
        else:
            st.warning("해당 지점/품목 조합이 존재하지 않습니다.")

    st.markdown("---")
    st.caption("※ inventory_data.csv 파일에 저장되며, 앱을 다시 열어도 데이터가 유지됩니다.")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 🔹 탭 2: 재고 현황 보기 (지점 → 카테고리 → 품목 Top-Down)
# =========================================================
with tab_view:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("재고 현황 조회 (지점 → 카테고리 → 품목 Top-Down)")

    df = st.session_state.inventory.copy()

    if df.empty:
        st.info("등록된 재고 데이터가 없습니다. 먼저 '재고 입력/수정' 탭에서 데이터를 추가하세요.")
    else:
        # 숫자형 변환
        for col in ["현재수량", "최소수량"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # 1단계: 지점 선택
        branch_options = ["전체"] + sorted(df["지점"].dropna().unique().tolist())
        selected_branch = st.selectbox("1단계: 지점 선택", branch_options)

        filtered = df.copy()
        if selected_branch != "전체":
            filtered = filtered[filtered["지점"] == selected_branch]

        # 2단계: 카테고리 선택
        available_categories = sorted(filtered["카테고리"].dropna().unique().tolist())
        cat_options = ["전체"] + available_categories
        selected_category = st.selectbox("2단계: 카테고리 선택", cat_options)

        if selected_category != "전체":
            filtered = filtered[filtered["카테고리"] == selected_category]

        # 3단계: 품목 선택
        available_items = sorted(filtered["품목명"].dropna().unique().tolist())
        item_options = ["전체"] + available_items
        selected_item = st.selectbox("3단계: 품목 선택", item_options)

        if selected_item != "전체":
            filtered = filtered[filtered["품목명"] == selected_item]

        # 추가 필터: 최소수량 이하만 보기
        only_low = st.checkbox("최소수량 이하 품목만 보기 (발주 필요)", value=False)

        if only_low:
            filtered = filtered[filtered["현재수량"] <= filtered["최소수량"]]

        st.markdown("#### 재고 목록")

        if filtered.empty:
            st.info("선택한 조건에 해당하는 재고가 없습니다.")
        else:
            # 부족 재고에 색 강조
            def highlight_low(row):
                if row["현재수량"] <= row["최소수량"]:
                    return [
                        'background-color: #7f1d1d; color: #fee2e2; font-weight: 500;'
                    ] * len(row)
                else:
                    return [''] * len(row)

            styled = filtered.style.apply(highlight_low, axis=1)
            st.dataframe(styled, use_container_width=True)

            # 다운로드 버튼
            csv = filtered.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="⬇ 현재 조회 결과를 CSV로 다운로드",
                data=csv,
                file_name="everest_inventory_filtered.csv",
                mime="text/csv",
            )

    st.markdown('</div>', unsafe_allow_html=True)

