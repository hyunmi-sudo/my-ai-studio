import streamlit as st
import pandas as pd
import io
import re
from google import genai

st.set_page_config(page_title="음원 & 콘텐츠 마케팅 성과 대시보드 Pro", layout="wide", page_icon="🎵")

# 사이드바 및 UI 스타일 보완 (다크 글자색 고정)
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    [data-testid="stSidebar"] {
        background-color: #F1F5F9 !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    [data-testid="stSidebar"] * {
        color: #0F172A !important;
    }
    div[data-testid="stAlert"] * {
        color: #0F172A !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 기본 Secrets API 키
default_secrets_key = st.secrets.get("GEMINI_API_KEY", "")

# 🔑 사이드바 사용자 지정 API 키 설정 영역
with st.sidebar:
    st.header("🔑 Gemini API 키 설정")
    user_api_key = st.text_input(
        "개인 Gemini API 키 입력", 
        type="password", 
        placeholder="AIzaSy...",
        help="다른 사용자의 개인 API 키를 입력하면 공용 키 대신 지정된 키로 분석이 진행됩니다."
    )
    
    # 입력된 키가 있으면 사용자 키 사용, 없으면 Secrets 기본 키 사용
    active_api_key = user_api_key.strip() if user_api_key.strip() else default_secrets_key.strip()
    
    if active_api_key:
        if user_api_key.strip():
            st.success("✅ 사용자 지정 API 키 연결 완료")
        else:
            st.success("✅ 기본 공유 API 키 연결 완료")
    else:
        st.warning("⚠️ 등록된 API 키가 없습니다. 키를 입력해 주세요.")
        
    st.markdown("---")

st.title("📊 음원 & 콘텐츠 마케팅 성과 분석 대시보드")
st.caption("발행된 숏폼 콘텐츠의 인게이지먼트와 음원 플랫폼별 스트리밍 추이를 실시간 집계합니다.")
st.divider()

# 샘플 데이터 세션 저장소 초기화
if "analytics_data" not in st.session_state:
    st.session_state.analytics_data = pd.DataFrame([
        {"날짜": "2026-08-25", "플랫폼": "인스타그램 릴스", "콘텐츠 제목": "민트볼 챌린지 1탄", "사용 음원": "Minty Fresh Beat", "조회수": 45000, "좋아요": 3200, "댓글": 180, "공유수": 420},
        {"날짜": "2026-08-26", "플랫폼": "유튜브 쇼츠", "콘텐츠 제목": "한 손에 쏙 들어오는 민트볼", "사용 음원": "Minty Fresh Beat", "조회수": 82000, "좋아요": 6100, "댓글": 340, "공유수": 890},
        {"날짜": "2026-08-27", "플랫폼": "틱톡", "콘텐츠 제목": "상쾌함 폭발 리액션", "사용 음원": "Minty Fresh Beat", "조회수": 120000, "좋아요": 11500, "댓글": 620, "공유수": 1450},
        {"날짜": "2026-08-28", "플랫폼": "인스타그램 릴스", "콘텐츠 제목": "출근길 필수 아이템 리얼 후기", "사용 음원": "Cool Summer Sound", "조회수": 28000, "좋아요": 1900, "댓글": 95, "공유수": 130},
        {"날짜": "2026-08-29", "플랫폼": "유튜브 쇼츠", "콘텐츠 제목": "식사 후 3초 만에 깔끔하게", "사용 음원": "Cool Summer Sound", "조회수": 64000, "좋아요": 4800, "댓글": 210, "공유수": 510},
        {"날짜": "2026-08-30", "플랫폼": "틱톡", "콘텐츠 제목": "카페에서 몰래 먹는 민트볼", "사용 음원": "Minty Fresh Beat", "조회수": 95000, "좋아요": 8700, "댓글": 410, "공유수": 920},
    ])

df = st.session_state.analytics_data.copy()

# 인게이지먼트 계산식: (좋아요 + 댓글 + 공유수) / 조회수 * 100
df["총 반응수"] = df["좋아요"] + df["댓글"] + df["공유수"]
df["인게이지먼트율(%)"] = ((df["총 반응수"] / df["조회수"]) * 100).round(2)

# 1. 상단 핵심 요약 지표 (Metrics)
m1, m2, m3, m4 = st.columns(4)
m1.metric("총 발행 콘텐츠", f"{len(df)}개")
m2.metric("누적 총 조회수", f"{df['조회수'].sum():,}회")
m3.metric("누적 총 반응수", f"{df['총 반응수'].sum():,}개")
m4.metric("평균 인게이지먼트율", f"{df['인게이지먼트율(%)'].mean():.2f}%")

st.divider()

# 2. 통합 인게이지먼트 장표 & 엑셀 다운로드
col_head, col_excel = st.columns([3, 1])
with col_head:
    st.subheader("📄 전체 콘텐츠 인게이지먼트 성과 장표")
with col_excel:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='콘텐츠_성과_분석')
    excel_file = output.getvalue()

    st.download_button(
        label="📥 엑셀(.xlsx) 파일 다운로드",
        data=excel_file,
        file_name="콘텐츠_인게이지먼트_성과장표.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.dataframe(
    df[["날짜", "플랫폼", "콘텐츠 제목", "사용 음원", "조회수", "좋아요", "댓글", "공유수", "인게이지먼트율(%)"]],
    use_container_width=True,
    hide_index=True
)

st.divider()

# 3. 플랫폼별 음원 발행수 카운팅 (릴스 / 쇼츠 / 틱톡)
st.subheader("🎵 음원별 플랫폼 발행 수 집계")
st.caption("한 음원으로 제작된 콘텐츠 수를 플랫폼별로 카운팅하여 비교합니다.")

music_counts = df.groupby(["사용 음원", "플랫폼"]).size().unstack(fill_value=0)

for platform in ["인스타그램 릴스", "유튜브 쇼츠", "틱톡"]:
    if platform not in music_counts.columns:
        music_counts[platform] = 0

music_counts = music_counts[["인스타그램 릴스", "유튜브 쇼츠", "틱톡"]]
music_counts["총 콘텐츠 수"] = music_counts.sum(axis=1)

st.dataframe(music_counts, use_container_width=True)

st.divider()

# 4. 음원 사이트별 일자별 추이 (유튜브 뮤직 / 멜론 / 스포티파이)
st.subheader("📈 음원 사이트별 일자별 트렌드 추이")
selected_song = st.selectbox("분석할 음원 선택", df["사용 음원"].unique())

dates = pd.date_range(start="2026-08-25", periods=7, freq="D").strftime("%Y-%m-%d")
trend_data = pd.DataFrame({
    "날짜": dates,
    "유튜브 뮤직": [12000, 15400, 21000, 28000, 35000, 42000, 51000],
    "멜론": [8500, 9200, 11500, 14200, 18900, 23000, 27500],
    "스포티파이": [5400, 6800, 8900, 12000, 15800, 19500, 24000]
}).set_index("날짜")

st.line_chart(trend_data)

with st.expander("📊 일자별 수치 데이터표 보기"):
    st.dataframe(trend_data, use_container_width=True)
