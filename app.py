import streamlit as st
import pandas as pd

st.set_page_config(page_title="Everest 재고관리 시스템", layout="wide")

# ---------- 초기 세션 상태 ----------
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(
        columns=["지점", "품목명", "카테고리", "단위", "현재수량", "최소수량", "비고"]
    )

branches = ["동대문", "굿모닝시티", "양재", "수원영통", "동탄", "영등포", "룸비니"]
categories = ["육류", "야채", "해산물", "향신료", "소스", "곡류/면", "음료", "포장재", "기타"]

st.title("📦 EVEREST 재고관리 시스템 (베타)")

tab_input, tab_view = st.tabs(["재고 입력/수정", "재고 현황 보기"])

# ---------- 탭 1: 재고 입력/수정 ----------
with tab_input:
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
            df = st.session_state.inventory
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
                st.session_state.inventory.loc[mask, :] = list(new_row.values())
                st.success("기존 품목 정보가 업데이트되었습니다.")
            else:
                st.session_state.inventory = pd.concat(
                    [df, pd.DataFrame([new_row])],
                    ignore_index=True
                )
                st.success("새 재고 품목이 등록되었습니다.")

    # 삭제
    if del_btn:
        df = st.session_state.inventory
        mask = (df["지점"] == branch) & (df["품목명"] == name)
        if mask.any():
            st.session_state.inventory = df[~mask].reset_index(drop=True)
            st.success(f"{branch} / {name} 품목이 삭제되었습니다.")
        else:
            st.warning("해당 지점/품목 조합이 존재하지 않습니다.")

    st.markdown("---")
    st.caption("※ 지금 버전은 메모리(session_state)에만 저장됨. 앱을 재시작하면 초기화됨. 나중에 원하면 엑셀/구글시트/DB 연동 버전으로 업그레이드 가능.")

# ---------- 탭 2: 재고 현황 ----------
with tab_view:
    st.subheader("재고 현황 조회")

    df = st.session_state.inventory.copy()

    # 필터 영역
    f1, f2, f3 = st.columns(3)
    with f1:
        f_branches = st.multiselect("지점 필터", branches, default=branches)
    with f2:
        f_category = st.multiselect("카테고리 필터", categories)
    with f3:
        only_low = st.checkbox("최소수량 이하인 품목만 보기 (발주 필요)")

    if not df.empty:
        # 필터 적용
        df = df[df["지점"].isin(f_branches)]
        if f_category:
            df = df[df["카테고리"].isin(f_category)]
        if only_low:
            df = df[df["현재수량"] <= df["최소수량"]]

        st.dataframe(df, use_container_width=True)

        # 다운로드 버튼
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇ 현재 조회 결과를 CSV로 다운로드",
            data=csv,
            file_name="everest_inventory.csv",
            mime="text/csv",
        )
    else:
        st.info("등록된 재고 데이터가 없습니다. 먼저 '재고 입력/수정' 탭에서 데이터를 추가하세요.")
