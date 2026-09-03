import os
import io
import time
import streamlit as st
from google import genai
import anthropic
import yt_dlp
import pandas as pd
from PIL import Image

st.set_page_config(page_title="AI 영상 제작 & 마케팅 스튜디오 Pro", layout="wide", page_icon="⚡")

# 기본 Secrets API 키
saved_gemini_key = st.secrets.get("GEMINI_API_KEY", "")

# 🎨 UI 개선: 눈이 편안한 깔끔한 라이트 테마 & 고대비 스타일링
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    [data-testid="stSidebar"] * {
        color: #0F172A !important;
    }
    /* 테이블 및 데이터 에디터 라이트 테마 강제 적용 */
    div[data-testid="stDataEditor"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    .stDataFrame {
        background-color: #FFFFFF !important;
    }
    /* 경고, 안내 박스 스타일 */
    div[data-testid="stAlert"] * {
        color: #0F172A !important;
        font-weight: 600 !important;
    }
    /* 입력창 깔끔한 스타일ing */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
    }
    /* 버튼 눈에 띄는 주황 그라데이션 */
    .stButton>button {
        background: linear-gradient(135deg, #FF6B00 0%, #E65100 100%) !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 💾 저장소 및 데이터 초기화
default_items = {
    "prompts": [], "plans": [], "yt_diag": [], 
    "img_analysis": [], "influencer": [], "calendar": [], "copywriting": []
}

if "saved_items" not in st.session_state:
    st.session_state.saved_items = default_items

if "saved_prompt_result" not in st.session_state: st.session_state.saved_prompt_result = None
if "saved_plan_result" not in st.session_state: st.session_state.saved_plan_result = None
if "saved_yt_result" not in st.session_state: st.session_state.saved_yt_result = None
if "saved_img_result" not in st.session_state: st.session_state.saved_img_result = None
if "saved_inf_result" not in st.session_state: st.session_state.saved_inf_result = None
if "saved_cal_result" not in st.session_state: st.session_state.saved_cal_result = None
if "saved_copy_result" not in st.session_state: st.session_state.saved_copy_result = None

# 📊 마케팅 성과 원본 데이터 세션 초기화
if "analytics_data" not in st.session_state:
    st.session_state.analytics_data = pd.DataFrame([
        {"날짜": "2026-08-25", "플랫폼": "인스타그램 릴스", "콘텐츠 제목": "민트볼 챌린지 1탄", "사용 음원": "Minty Fresh Beat", "조회수": 45000, "좋아요": 3200, "댓글": 180, "공유수": 420},
        {"날짜": "2026-08-26", "플랫폼": "유튜브 쇼츠", "콘텐츠 제목": "한 손에 쏙 들어오는 민트볼", "사용 음원": "Minty Fresh Beat", "조회수": 82000, "좋아요": 6100, "댓글": 340, "공유수": 890},
        {"날짜": "2026-08-27", "플랫폼": "틱톡", "콘텐츠 제목": "상쾌함 폭발 리액션", "사용 음원": "Minty Fresh Beat", "조회수": 120000, "좋아요": 11500, "댓글": 620, "공유수": 1450},
        {"날짜": "2026-08-28", "플랫폼": "인스타그램 릴스", "콘텐츠 제목": "출근길 필수 아이템 리얼 후기", "사용 음원": "Cool Summer Sound", "조회수": 28000, "좋아요": 1900, "댓글": 95, "공유수": 130},
        {"날짜": "2026-08-29", "플랫폼": "유튜브 쇼츠", "콘텐츠 제목": "식사 후 3초 만에 깔끔하게", "사용 음원": "Cool Summer Sound", "조회수": 64000, "좋아요": 4800, "댓글": 210, "공유수": 510},
        {"날짜": "2026-08-30", "플랫폼": "틱톡", "콘텐츠 제목": "카페에서 몰래 먹는 민트볼", "사용 음원": "Minty Fresh Beat", "조회수": 95000, "좋아요": 8700, "댓글": 410, "공유수": 920},
    ])

st.title("⚡ AI 영상 제작 & 올인원 마케팅 스튜디오 Pro")
st.divider()

# 🔑 사이드바 API 설정 영역
with st.sidebar:
    st.header("🔑 Gemini API 설정")
    user_gemini_key = st.text_input("개인 Gemini API 키 입력", type="password", placeholder="AIzaSy...")
    active_gemini_key = user_gemini_key.strip() if user_gemini_key.strip() else saved_gemini_key.strip()
    
    if active_gemini_key:
        st.success("✅ Gemini API 연결 완료")
    else:
        st.warning("⚠️ 등록된 API 키가 없습니다.")
        
    claude_key = st.text_input("Anthropic Claude API Key (선택)", type="password")

def get_gemini_client():
    if not active_gemini_key:
        st.error("⚠️ API 키를 입력해 주세요.")
        return None
    try:
        return genai.Client(api_key=active_gemini_key)
    except Exception as e:
        st.error(f"클라이언트 오류: {e}")
        return None

def safe_gemini_generate(client, contents_input):
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=contents_input
        )
        if response and response.text:
            return response.text
    except Exception as e:
        st.error(f"⚠️ API 생성 오류: {e}")
    return None

def generate_claude_or_gemini(prompt, gemini_client):
    if claude_key and claude_key.strip():
        try:
            client = anthropic.Anthropic(api_key=claude_key.strip())
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception:
            pass
    if gemini_client:
        return safe_gemini_generate(gemini_client, prompt)
    return None

main_tab1, main_tab2, main_tab3 = st.tabs([
    "🎬 1. 영상 제작 AI 프롬프트 생성", 
    "📄 2. 촬영 기획서 작성",
    "🛠️ 3. 마케팅 성과 대시보드"
])

# TAB 1 & TAB 2 간략화 연동
with main_tab1:
    p_topic = st.text_input("영상 주제 / 제품명", placeholder="예: 민트볼 숏폼 홍보")
    p_detail = st.text_area("핵심 메시지", placeholder="예: 휴대성과 상쾌함 강조")
    if st.button("🚀 프롬프트 생성"):
        g_client = get_gemini_client()
        if p_topic and g_client:
            res = generate_claude_or_gemini(f"주제: {p_topic}, 내용: {p_detail} 프롬프트 작성", g_client)
            if res: st.info(res)

with main_tab2:
    g_title = st.text_input("프로젝트명", placeholder="예: 민트볼 틴케이스")
    g_goal = st.text_area("제작 목적", placeholder="세부 내용 입력")
    if st.button("📄 촬영기획서 작성"):
        g_client = get_gemini_client()
        if g_title and g_client:
            res_pl = safe_gemini_generate(g_client, f"프로젝트: {g_title}, 목적: {g_goal} 촬영계획서 작성")
            if res_pl: st.success(res_pl)

# TAB 3: 마케팅 성과 대시보드 (자유 입력 & 실시간 자동 연동)
with main_tab3:
    st.subheader("📊 발행 콘텐츠 종합 성과 관리 대시보드")
    
    # ➕ 신규 데이터 직접 입력 폼
    with st.expander("➕ 새 콘텐츠 성과 데이터 등록하기", expanded=True):
        col_in1, col_in2, col_in3 = st.columns(3)
        with col_in1:
            in_date = st.date_input("발행 날짜")
            in_platform = st.selectbox("플랫폼", ["인스타그램 릴스", "유튜브 쇼츠", "틱톡"])
        with col_in2:
            in_title = st.text_input("콘텐츠 제목", placeholder="예: 상쾌함 반응 챌린지")
            in_song = st.text_input("사용 음원명", placeholder="예: My Custom Beat")
        with col_in3:
            in_views = st.number_input("조회수", min_value=0, value=10000)
            in_likes = st.number_input("좋아요", min_value=0, value=500)
            in_comments = st.number_input("댓글", min_value=0, value=30)
            in_shares = st.number_input("공유수", min_value=0, value=50)

        if st.button("✨ 데이터 목록에 즉시 추가하기", use_container_width=True):
            new_row = pd.DataFrame([{
                "날짜": str(in_date),
                "플랫폼": in_platform,
                "콘텐츠 제목": in_title if in_title else "제목 없음",
                "사용 음원": in_song if in_song else "기본 음원",
                "조회수": in_views,
                "좋아요": in_likes,
                "댓글": in_comments,
                "공유수": in_shares
            }])
            st.session_state.analytics_data = pd.concat([st.session_state.analytics_data, new_row], ignore_index=True)
            st.success(f"✅ '{in_title}' 콘텐츠가 추가되었습니다!")

    st.divider()

    # 📝 성과 데이터 가공 및 인게이지먼트 자동 계산
    df = st.session_state.analytics_data.copy()
    
    for c in ["조회수", "좋아요", "댓글", "공유수"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    df["총 반응수"] = df["좋아요"] + df["댓글"] + df["공유수"]
    df["인게이지먼트율(%)"] = df.apply(
        lambda r: round((r["총 반응수"] / r["조회수"] * 100), 2) if r["조회수"] > 0 else 0.0, axis=1
    )

    # 1. 요약 지표 카드
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("총 콘텐츠 발행수", f"{len(df)}개")
    m2.metric("누적 총 조회수", f"{int(df['조회수'].sum()):,}회")
    m3.metric("누적 총 반응수", f"{int(df['총 반응수'].sum()):,}개")
    avg_eng = df['인게이지먼트율(%)'].mean() if len(df) > 0 else 0
    m4.metric("평균 인게이지먼트율", f"{avg_eng:.2f}%")

    st.divider()

    # 2. 성과 장표 및 엑셀 다운로드
    col_t_head, col_t_dl = st.columns([3, 1])
    with col_t_head:
        st.markdown("##### 📄 통합 인게이지먼트 성과 장표")
    with col_t_dl:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='콘텐츠성과')
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 엑셀(.xlsx) 다운로드",
            data=excel_data,
            file_name="마케팅_콘텐츠_성과장표.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # 라이트 톤 표 렌더링 (편집 가능)
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="main_data_editor"
    )
    
    st.session_state.analytics_data = edited_df

    st.divider()

    # 3. 🎵 플랫폼별 음원 발행 수 자동 집계 (실시간 연동)
    st.markdown("#### 🎵 음원별 플랫폼 발행 수 자동 집계")
    st.caption("위에서 새로 추가하거나 수정한 음원 데이터가 실시간 집계됩니다.")

    valid_df = edited_df[edited_df["사용 음원"].notnull() & (edited_df["사용 음원"] != "")]
    
    if not valid_df.empty:
        music_counts = valid_df.groupby(["사용 음원", "플랫폼"]).size().unstack(fill_value=0)
        
        for p in ["인스타그램 릴스", "유튜브 쇼츠", "틱톡"]:
            if p not in music_counts.columns:
                music_counts[p] = 0
                
        music_counts = music_counts[["인스타그램 릴스", "유튜브 쇼츠", "틱톡"]]
        music_counts["총 제작 콘텐츠 수"] = music_counts.sum(axis=1)

        st.dataframe(music_counts, use_container_width=True)
    else:
        st.info("데이터를 등록해 주세요.")

    st.divider()

    # 4. 📈 음원 사이트별 일자별 추이 차트
    st.markdown("#### 📈 음원 사이트별 일자별 트렌드 추이")
    
    song_list = list(valid_df["사용 음원"].unique()) if not valid_df.empty else ["Minty Fresh Beat"]
    selected_song = st.selectbox("분석할 음원 선택", song_list)

    dates = pd.date_range(start="2026-08-25", periods=7, freq="D").strftime("%Y-%m-%d")
    trend_df = pd.DataFrame({
        "날짜": dates,
        "유튜브 뮤직": [12000, 15400, 21000, 28000, 35000, 42000, 51000],
        "멜론": [8500, 9200, 11500, 14200, 18900, 23000, 27500],
        "스포티파이": [5400, 6800, 8900, 12000, 15800, 19500, 24000]
    }).set_index("날짜")

    st.line_chart(trend_df)
