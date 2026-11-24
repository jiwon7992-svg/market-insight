"""MVP용 샘플 사건 (미국 시장, 과거 사건 8건).

주의
- 요약은 '사건 당시 알 수 있는 사실'만 중립적으로 적었다. 사건 이후의 주가 반응이나 평가는 쓰지 않았다 (블라인드 모드 데이터 누출 방지).
- 출처(sources)와 전문가 분석(analyses)은 아직 연결하지 않았다. 3~5단계에서 공식 자료로 채운다.
  출처가 없는 항목을 있는 것처럼 보이지 않도록, 이 데이터는 data_origin='seed'로 표시한다.
- published_at은 날짜 단위다. 장 마감 후 발표된 사건(예: 실적 발표)은 4단계에서 시각 정보를 추가해 다룰 예정이다.
- 날짜와 사실관계는 반드시 공식 자료로 재확인하라.
"""
from .events import add_event

SEED_EVENTS = [
    dict(
        title="리먼 브라더스 파산보호(챕터 11) 신청",
        category="금융위기", occurred_at="2008-09-15", published_at="2008-09-15",
        summary="미국 대형 투자은행 리먼 브라더스가 파산보호를 신청했다.",
        background="서브프라임 모기지 관련 자산 손실과 자금조달 어려움이 누적된 상태였다.",
        transmission="금융기관 간 신뢰 저하 → 신용경색과 자금조달 비용 상승 가능성 → 위험자산 회피 심리.",
        tickers=[("SPY", "index"), ("XLF", "industry")],
    ),
    dict(
        title="Fed 긴급 금리 인하(0~0.25%)와 자산매입 재개",
        category="금리", occurred_at="2020-03-15", published_at="2020-03-15",
        summary="연준이 연방기금금리 목표 범위를 0~0.25%로 낮추고 국채 등 자산매입 재개를 발표했다.",
        background="코로나19 확산으로 경제활동 둔화와 금융시장 변동성 확대에 대한 우려가 커진 상황이었다.",
        transmission="할인율 하락, 유동성 공급 기대 ↔ 경기 침체 우려가 더 심각하다는 신호로 해석될 가능성.",
        tickers=[("SPY", "index")],
    ),
    dict(
        title="WTI 원유 선물 가격 마이너스 마감",
        category="원자재", occurred_at="2020-04-20", published_at="2020-04-20",
        summary="WTI 근월물 원유 선물 가격이 사상 처음으로 0달러 아래에서 마감했다.",
        background="코로나19로 수요가 급감한 가운데 저장 공간 부족 우려가 커졌다.",
        transmission="에너지 기업 실적과 자금조달 우려, 산업 전반의 수요 위축 신호 가능성.",
        tickers=[("USO", "industry"), ("XLE", "industry"), ("SPY", "index")],
    ),
    dict(
        title="러시아의 우크라이나 침공",
        category="전쟁/국제정세", occurred_at="2022-02-24", published_at="2022-02-24",
        summary="러시아가 우크라이나에 대한 군사 공격을 개시했다.",
        background="침공 이전부터 러시아군 집결과 외교적 긴장이 이어지고 있었다.",
        transmission="에너지·곡물 가격과 인플레이션 우려, 안전자산 선호, 제재에 따른 공급망 영향 가능성.",
        tickers=[("SPY", "index"), ("XLE", "industry")],
    ),
    dict(
        title="Fed, 2018년 이후 첫 기준금리 인상(25bp)",
        category="금리", occurred_at="2022-03-16", published_at="2022-03-16",
        summary="연준이 기준금리를 0.25%p 인상해 0.25~0.50%로 올렸다.",
        background="물가 상승률이 높은 수준을 이어가고 있었고, 통화정책 정상화가 예고되어 있었다.",
        transmission="할인율 상승이 성장주 가치평가에 미치는 영향, 시장의 기대(이미 반영된 정도)와의 차이가 핵심 변수.",
        tickers=[("SPY", "index"), ("QQQ", "index")],
    ),
    dict(
        title="OpenAI, ChatGPT 공개",
        category="신기술/산업 변화", occurred_at="2022-11-30", published_at="2022-11-30",
        summary="OpenAI가 대화형 AI 서비스 ChatGPT를 공개했다.",
        background="대형 언어모델 연구가 이어지던 가운데 일반 이용자용 서비스로 공개되었다.",
        transmission="생성형 AI 수요 기대가 클라우드·반도체 기업 전망에 미칠 가능성. 즉각적 실적 영향은 불확실.",
        tickers=[("MSFT", "company"), ("NVDA", "company")],
    ),
    dict(
        title="실리콘밸리은행(SVB) 폐쇄, FDIC가 관리 개시",
        category="금융위기", occurred_at="2023-03-10", published_at="2023-03-10",
        summary="캘리포니아 금융당국이 실리콘밸리은행을 폐쇄하고 FDIC를 관리인으로 지정했다.",
        background="금리 상승으로 보유 채권 평가손실이 커진 가운데 예금 인출 압력이 급증했다.",
        transmission="지역은행 전반의 예금 이탈 우려, 금융 안정성과 향후 통화정책 경로에 대한 기대 변화 가능성.",
        tickers=[("KRE", "industry"), ("SPY", "index")],
    ),
    dict(
        title="NVIDIA 2024 회계연도 1분기 실적 발표 및 2분기 가이던스",
        category="기업 실적", occurred_at="2023-05-24", published_at="2023-05-24",
        summary="NVIDIA가 1분기 실적을 발표하고 2분기 매출 가이던스를 제시했다 (미국 증시 장 마감 후 발표).",
        background="데이터센터용 GPU 수요와 AI 투자 확대 여부가 시장의 주요 관심사였다.",
        transmission="가이던스와 시장 기대치의 차이, AI 관련 반도체·서버 업종 전반의 투자심리에 미치는 영향.",
        tickers=[("NVDA", "company"), ("SOXX", "industry"), ("SPY", "index")],
    ),
]


def seed_if_empty(conn) -> int:
    """events 테이블이 비어 있을 때만 샘플을 넣는다. 추가한 건수를 반환."""
    if conn.execute("SELECT COUNT(*) FROM events").fetchone()[0] > 0:
        return 0
    for ev in SEED_EVENTS:
        add_event(conn, data_origin="seed", **ev)
    return len(SEED_EVENTS)
