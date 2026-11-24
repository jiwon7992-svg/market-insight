"""Market Insight - 1단계: 기본 구조와 메인 화면
실행: streamlit run app.py
"""
from datetime import date

import pandas as pd
import streamlit as st

from core.config import CATEGORIES
from core.db import get_conn, init_db
from core.events import add_event, parse_tickers, tickers_of, visible_events
from core.seed import seed_if_empty

st.set_page_config(page_title="Market Insight", page_icon="📈", layout="wide")


@st.cache_resource
def get_db():
    conn = get_conn()
    init_db(conn)
    seed_if_empty(conn)
    return conn


conn = get_db()

# ---------------- 사이드바 ----------------
with st.sidebar:
    st.header("보기 설정")
    mode = st.radio(
        "기준 시점",
        ["현재 (모든 정보)", "과거 시점 (미래 정보 차단)"],
        help="과거 시점을 고르면 그 날짜까지 공개된 사건만 보입니다. 블라인드 분석 모드의 기반입니다.",
    )
    as_of = None
    if mode.startswith("과거"):
        as_of = st.date_input("이 날짜까지 공개된 정보만 보기", value=date(2022, 3, 1)).isoformat()
        st.warning(f"{as_of} 이후에 공개된 사건은 숨겨집니다.")

    category = st.selectbox("사건 종류", ["전체"] + CATEGORIES)
    category = None if category == "전체" else category

    st.divider()
    with st.expander("➕ 사건 직접 추가"):
        with st.form("add_event_form", clear_on_submit=True):
            title = st.text_input("사건 제목")
            cat = st.selectbox("종류", CATEGORIES, key="new_cat")
            occurred = st.date_input("발생일", value=date.today(), key="new_occ")
            published = st.date_input("공개일", value=date.today(), key="new_pub",
                                      help="뉴스나 공식 발표로 처음 알려진 날짜")
            summary = st.text_area("내용")
            tickers_text = st.text_input("관련 종목/지수 (쉼표로 구분)", placeholder="NVDA, SPY")
            if st.form_submit_button("저장"):
                try:
                    add_event(conn, title, cat, occurred.isoformat(), published.isoformat(),
                              summary=summary, tickers=parse_tickers(tickers_text))
                    st.success("저장했습니다.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

# ---------------- 본문 ----------------
st.title("📈 Market Insight")
st.caption("AI가 주가를 예측하거나 종목을 추천하지 않습니다. 사건과 시장 반응을 직접 관찰하고, 스스로 판단하는 연습을 위한 도구입니다.")

st.subheader("주요 시장 지표")
st.info("아직 연결되지 않았습니다. 2단계(주가 데이터)와 3단계(FRED 경제지표)에서 구현합니다.")

keyword = st.text_input("🔍 사건 검색 (제목, 내용, 종목 코드)")
events = visible_events(conn, as_of=as_of, category=category, keyword=keyword or None)


def render_event(ev):
    label = f"**{ev['published_at']}** · {ev['title']}  \n`{ev['category']}`"
    with st.expander(label.replace("\n", " ")):
        st.write(ev["summary"] or "내용 없음")
        if ev["background"]:
            st.markdown(f"**배경/원인**: {ev['background']}")
        if ev["transmission"]:
            st.markdown(f"**시장 영향 경로 (가능성)**: {ev['transmission']}")
        tks = tickers_of(conn, ev["id"])
        if tks:
            st.markdown("**관련 종목/지수**: " + ", ".join(f"{t} ({r})" for t, r in tks))
        meta = f"발생일 {ev['occurred_at']} · 공개일 {ev['published_at']}"
        if ev["data_origin"] == "seed":
            meta += " · 샘플 데이터(출처 미연결)"
        elif ev["data_origin"] == "user":
            meta += " · 사용자 입력"
        st.caption(meta)


tab_recent, tab_archive = st.tabs(["최근 사건", "과거 사건 아카이브"])
with tab_recent:
    if not events:
        st.write("조건에 맞는 사건이 없습니다.")
    for ev in events[:5]:
        render_event(ev)

with tab_archive:
    st.caption(f"총 {len(events)}건 · 분석 화면은 4~6단계에서 연결됩니다.")
    if events:
        df = pd.DataFrame(
            [{"공개일": e["published_at"], "발생일": e["occurred_at"],
              "사건": e["title"], "종류": e["category"],
              "관련": ", ".join(t for t, _ in tickers_of(conn, e["id"]))} for e in events]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
