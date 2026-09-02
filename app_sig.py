import os
import streamlit as st
from google import genai
from PIL import Image
import urllib.parse

# 귀여운 아기자기한 스타일 및 색상 테마 CSS 적용
st.set_page_config(page_title="🎀 아프리카TV 시그 BGM 추천소 🎀", layout="wide", page_icon="🎀")

st.markdown("""
    <style>
    /* 전체 배경 및 폰트 감성 스타일링 */
    .stApp {
        background-color: #FAF5FF;
    }
    .main-title {
        color: #FF6B8B;
        font-weight: 800;
        font-size: 2.2rem;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #8862B5;
        text-align: center;
        font-size: 1.0rem;
        margin-bottom: 25px;
    }
    .cute-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0px 8px 20px rgba(255, 182, 193, 0.3);
        border: 2px solid #FFE4E1;
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF8EAE 0%, #FF6B8B 100%) !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        font-weight: bold !important;
        height: 50px !important;
        font-size: 1.1rem !important;
        box-shadow: 0px 4px 10px rgba(255, 107, 139, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Secrets에서 API 키 자동 로드
saved_gemini_key = st.secrets.get("GEMINI_API_KEY", "")

# 세션 보관함 초기화
if "sig_result" not in st.session_state: st.session_state.sig_result = None

st.markdown("<p class='main-title'>🎀 아프리카TV 시그니처 BGM 추천소 🎶</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>✨ 시그니처 움짤/이미지를 업로드하면 어울리는 리액션 BGM과 노래를 추천해 드려요! ✨</p>", unsafe_allow_html=True)

# 사이드바 API 설정
with st.sidebar:
    st.header("🔑 API 연결 상태")
    st.success("💖 Google Gemini API 연결 완료!")
    st.info("💡 TIP: 시그니처의 색감, 캐릭터 스타일, 템포를 종합 분석합니다.")

# 메인 UI 카드 분리
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("<div class='cute-card'>", unsafe_allow_html=True)
    st.subheader("🖼️ 1. 시그니처 이미지/GIF 업로드")
    uploaded_sig = st.file_uploader("파일을 끌어다 놓으세요 (GIF, PNG, JPG)", type=["gif", "png", "jpg", "jpeg"])
    
    if uploaded_sig:
        st.image(uploaded_sig, caption="✨ 업로드된 예쁜 시그니처 ✨", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='cute-card'>", unsafe_allow_html=True)
    st.subheader("🎯 2. 방송 리액션 & 분위기 선택")
    reaction_type = st.selectbox(
        "어떤 리액션인가요?", 
        ["💃 댄스/신나는 템포", "✨ 큐트/애교/귀여움", "🔥 섹시/몽환적인", "🤪 엽기/개그/밈(Meme)", "🌙 감성/소통/잔잔함", "⚔️ 웅장/비장함"]
    )
    
    streamer_memo = st.text_input("추가 특징 (선택)", placeholder="예: 3초 짜리 짧은 리액션, 힙합 느낌 선호")
    
    btn_analyze = st.button("💖 BGM & 어울리는 노래 분석 시작하기!", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# AI 분석 실행
if btn_analyze:
    if not saved_gemini_key:
        st.error("⚠️ Secrets에 GEMINI_API_KEY가 설정되어 있지 않습니다.")
    elif not uploaded_sig:
        st.error("⚠️ 시그니처 이미지/GIF 파일을 업로드해 주세요.")
    else:
        with st.spinner("🎀 Visual AI가 시그니처의 분위기와 매력을 분석 중입니다..."):
            try:
                client = genai.Client(api_key=saved_gemini_key.strip())
                image_data = Image.open(uploaded_sig)
                
                prompt = f"""
                당신은 아프리카TV BJ 전문 방송 연출 감독이자 음악 디렉터입니다.
                업로드된 시그니처 이미지/움짤을 시각적으로 정밀 분석하고, 사용자가 선택한 컨셉([{reaction_type}])과 추가 특징([{streamer_memo}])에 가장 잘 어울리는 BGM 및 노래를 추천하세요.

                [출력 형식]:
                1. 🎨 **시그니처 시각적 분위기 분석**
                   - 주요 색감 및 톤앤매너
                   - 캐릭터/움직임의 연출 특징
                   - 추천 리액션 구간 (예: 0초~5초 하이라이트)

                2. 🎧 **추천 BGM 및 리액션 송 (총 5곡)**
                   - 곡명 / 아티스트
                   - 추천 구간 (예: 15초~30초 하이라이트 파트)
                   - 추천 이유 및 매칭 포인트

                3. 🎼 **AI 음악 생성용 영문 프롬프트 (Suno / Udio 용)**
                   - Style of Music 영문 프롬프트
                """
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=[prompt, image_data]
                )
                
                if response and response.text:
                    st.session_state.sig_result = response.text
            except Exception as e:
                st.error(f"⚠️ 분석 오류 발생: {e}")

# 분석 결과 및 구간별 자르기 다운로드
if st.session_state.sig_result:
    st.divider()
    st.markdown("### 📊 AI 시그니처 음악 분석 리포트")
    st.info(st.session_state.sig_result)
    
    st.divider()
    
    # ✂️ 리액션 초 단위 구간 지정 및 다운로드 기능
    st.subheader("✂️ 시그니처 BGM 구간 지정 메모장 다운로드")
    st.caption("시그니처 리액션에 사용할 특정 초(Second) 구간을 지정해서 메모장(.txt) 파일로 다운로드하세요!")
    
    col_cut1, col_cut2, col_cut3 = st.columns([1, 1, 2])
    with col_cut1:
        start_sec = st.number_input("시작 시간 (초)", min_value=0, max_value=300, value=0)
    with col_cut2:
        end_sec = st.number_input("종료 시간 (초)", min_value=1, max_value=300, value=5)
    
    with col_cut3:
        st.write("") # 간격 조정
        st.write("")
        custom_note = f"""[ 🎀 아프리카TV 시그니처 BGM 리액션 가이드 ]
■ 지정 사용 구간: {start_sec}초 ~ {end_sec}초 (총 {end_sec - start_sec}초간 재생)

[ AI 음악 추천 리포트 전문 ]
{st.session_state.sig_result}
"""
        st.download_button(
            label=f"💾 [{start_sec}초 ~ {end_sec}초 구간] 맞춤 메모장 다운로드",
            data=custom_note,
            file_name=f"Signature_BGM_{start_sec}s_to_{end_sec}s.txt",
            use_container_width=True
        )

    st.divider()
    st.subheader("🔍 유튜브에서 추천곡 들어보기")
    search_keyword = st.text_input("검색할 노래 제목이나 아티스트 입력", placeholder="예: 뉴진스 Hype Boy")
    if search_keyword:
        encoded_query = urllib.parse.quote(f"{search_keyword} BGM")
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        st.markdown(f"👉 [▶️ 유튜브에서 '{search_keyword}' 검색해서 들어보기]({youtube_url})")
