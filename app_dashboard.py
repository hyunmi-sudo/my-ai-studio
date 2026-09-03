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
default_secrets_key = st.secrets.get("GEMINI_API_KEY", "")

# 🎨 사이드바 & 라벨 가독성 고대비 CSS
st.markdown("""
    <style>
    [data-testid="stSidebar"] h2 { font-size: 1.35rem !important; font-weight: 800 !important; color: #0F172A !important; }
    [data-testid="stSidebar"] label { font-weight: 700 !important; color: #0F172A !important; }
    div[data-testid="stAlert"] * { font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

# 💾 카테고리 저장소 및 세션 초기화
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
    ])

st.title("⚡ AI 영상 제작 & 올인원 마케팅 스튜디오 Pro")
st.divider()

# 🔑 사이드바 API 설정
with st.sidebar:
    st.header("🔑 Gemini API 키 설정")
    user_gemini_key = st.text_input("개인 Gemini API 키 입력", type="password", placeholder="AIzaSy...")
    active_gemini_key = user_gemini_key.strip() if user_gemini_key.strip() else default_secrets_key.strip()
    
    if active_gemini_key:
        if user_gemini_key.strip():
            st.success("✅ 사용자 지정 API 키 연결 완료")
        else:
            st.success("✅ 기본 공유 API 키 연결 완료")
    else:
        st.warning("⚠️ API 키가 입력되지 않았습니다.")
        
    claude_key = st.text_input("Anthropic Claude API Key (선택)", type="password")

    st.divider()
    st.header("📂 카테고리별 보관함")
    # (보관함 UI 생략 - 기존 동일)

def get_gemini_client():
    if not active_gemini_key:
        st.error("⚠️ 사용할 Gemini API 키가 없습니다.")
        return None
    try:
        return genai.Client(api_key=active_gemini_key)
    except Exception as e:
        st.error(f"Gemini 초기화 오류: {e}")
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
        st.error(f"⚠️ API 요청 실패: {e}")
    return None

# 유튜브 상세 자동 파싱 함수
def extract_auto_yt_data(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "날짜": time.strftime("%Y-%m-%d"),
            "플랫폼": "유튜브 쇼츠",
            "콘텐츠 제목": info.get('title', 'N/A'),
            "사용 음원": info.get('track') or info.get('artist') or '유튜브 오리지널 음원',
            "조회수": info.get('view_count', 0),
            "좋아요": info.get('like_count', 0),
            "댓글": info.get('comment_count', 0),
            "공유수": 0
        }

main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
    "🎬 1. 영상 제작 AI 프롬프트 생성기", 
    "📄 2. 영상 종합 기획서 & 촬영계획서 작성기",
    "🛠️ 3. 확장 마케팅 스튜디오",
    "📊 4. 마케팅 성과 & 음원 분석 대시보드"
])

# (탭 1~3 기존 동일)

# ==========================================
# 📊 TAB 4: URL 자동 수집 기능이 통합된 대시보드
# ==========================================
with main_tab4:
    st.markdown("### 📊 4. 마케팅 성과 & 음원 분석 대시보드")
    
    sub_dash1, sub_dash2, sub_dash3 = st.tabs([
        "📄 4-1. 인게이지먼트 성과 장표 관리",
        "🎵 4-2. 음원별 플랫폼 발행 수 카운팅",
        "📈 4-3. 음원 사이트별 일자별 추이"
    ])

    with sub_dash1:
        # 🔗 URL 자동 수집 섹션 추가
        with st.expander("🔗 유튜브 영상 링크(URL) 넣고 성과 데이터 자동 수집하기", expanded=True):
            col_u1, col_u2 = st.columns([3, 1])
            with col_u1:
                auto_yt_url = st.text_input("유튜브 Shorts 또는 일반 영상 URL 입력", placeholder="https://www.youtube.com/shorts/...")
            with col_u2:
                st.write("") # 간격 맞춤용
                st.write("")
                btn_auto_fetch = st.button("🚀 URL 자동 등록", use_container_width=True, type="primary")

            if btn_auto_fetch:
                if auto_yt_url.strip():
                    with st.spinner("유튜브에서 조회수, 좋아요, 음원 정보를 수집 중입니다..."):
                        try:
                            auto_data = extract_auto_yt_data(auto_yt_url.strip())
                            new_df = pd.DataFrame([auto_data])
                            st.session_state.analytics_data = pd.concat([st.session_state.analytics_data, new_df], ignore_index=True)
                            st.success(f"✅ '{auto_data['콘텐츠 제목']}' 데이터 수집 및 등록 완료!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"⚠️ URL 수집 실패: {e}")

        # 수동 추가 & 삭제 섹션
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            with st.expander("➕ 수동 데이터 등록하기", expanded=False):
                col_in1, col_in2, col_in3 = st.columns(3)
                with col_in1:
                    in_date = st.date_input("발행 날짜")
                    in_platform = st.selectbox("플랫폼", ["인스타그램 릴스", "유튜브 쇼츠", "틱톡"])
                with col_in2:
                    in_title = st.text_input("콘텐츠 제목")
                    in_song = st.text_input("사용 음원명")
                with col_in3:
                    in_views = st.number_input("조회수", min_value=0, value=10000)
                    in_likes = st.number_input("좋아요", min_value=0, value=500)
                    in_comments = st.number_input("댓글", min_value=0, value=30)
                    in_shares = st.number_input("공유수", min_value=0, value=50)

                if st.button("✨ 수동 데이터 추가", use_container_width=True):
                    new_row = pd.DataFrame([{
                        "날짜": str(in_date), "플랫폼": in_platform,
                        "콘텐츠 제목": in_title if in_title else "제목 없음",
                        "사용 음원": in_song if in_song else "기본 음원",
                        "조회수": in_views, "좋아요": in_likes, "댓글": in_comments, "공유수": in_shares
                    }])
                    st.session_state.analytics_data = pd.concat([st.session_state.analytics_data, new_row], ignore_index=True)
                    st.success("✅ 직접 입력한 데이터가 추가되었습니다!")
                    st.rerun()

        with col_f2:
            st.markdown("##### 🗑️ 항목 관리")
            if not st.session_state.analytics_data.empty:
                del_target = st.selectbox("삭제할 콘텐츠 선택", st.session_state.analytics_data["콘텐츠 제목"].tolist())
                if st.button("🗑️ 선택 항목 삭제하기", use_container_width=True):
                    st.session_state.analytics_data = st.session_state.analytics_data[
                        st.session_state.analytics_data["콘텐츠 제목"] != del_target
                    ].reset_index(drop=True)
                    st.warning(f"🗑️ '{del_target}' 항목이 삭제되었습니다.")
                    st.rerun()

        st.divider()

        df = st.session_state.analytics_data.copy()
        for c in ["조회수", "좋아요", "댓글", "공유수"]:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        df["총 반응수"] = df["좋아요"] + df["댓글"] + df["공유수"]
        df["인게이지먼트율(%)"] = df.apply(
            lambda r: round((r["총 반응수"] / r["조회수"] * 100), 2) if r["조회수"] > 0 else 0.0, axis=1
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 콘텐츠 발행수", f"{len(df)}개")
        m2.metric("누적 총 조회수", f"{int(df['조회수'].sum()):,}회")
        m3.metric("누적 총 반응수", f"{int(df['총 반응수'].sum()):,}개")
        avg_eng = df['인게이지먼트율(%)'].mean() if len(df) > 0 else 0
        m4.metric("평균 인게이지먼트율", f"{avg_eng:.2f}%")

        st.divider()

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            key="main_dashboard_editor"
        )
        st.session_state.analytics_data = edited_df

    # (서브 탭 4-2, 4-3 기존 동일)
