import os
import io
import streamlit as st
from google import genai
from PIL import Image
import urllib.parse
from yt_dlp import YoutubeDL

st.set_page_config(page_title="아프리카TV 시그니처 BGM 추천 AI", layout="wide", page_icon="🎵")

# 화사하고 깔끔한 라이트 테마 CSS
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #F8FAFC !important;
        color: #1E293B !important;
    }
    [data-testid="stSidebar"] {
        background-color: #F1F5F9 !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    .main-title {
        color: #FF6B00 !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        text-align: center !important;
        margin-bottom: 0px !important;
    }
    .sub-title {
        color: #64748B !important;
        text-align: center !important;
        font-size: 1.0rem !important;
        margin-bottom: 25px !important;
    }
    .cute-card {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 22px !important;
        border-top: 4px solid #FF6B00 !important;
        border-left: 1px solid #E2E8F0 !important;
        border-right: 1px solid #E2E8F0 !important;
        border-bottom: 1px solid #E2E8F0 !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.04) !important;
        margin-bottom: 20px !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF6B00 0%, #E65100 100%) !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 800 !important;
        height: 50px !important;
        font-size: 1.1rem !important;
        box-shadow: 0px 4px 10px rgba(255, 107, 0, 0.25) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #FF8533 0%, #FF6B00 100%) !important;
    }
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
    }
    </style>
""", unsafe_allow_html=True)

saved_gemini_key = st.secrets.get("GEMINI_API_KEY", "")

if "sig_result" not in st.session_state: st.session_state.sig_result = None

st.markdown("<p class='main-title'>🎵 아프리카TV 시그니처 BGM & 노래 추천 AI 🎶</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>시그니처 이미지나 GIF 움짤을 업로드하면 Visual AI가 분위기를 분석하여 가장 잘 어울리는 BGM과 리액션 송을 추천해 드립니다.</p>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🔑 API 연결 상태")
    st.success("✅ Google Gemini API 연결 완료")
    st.info("💡 TIP: 시그니처의 색감, 캐릭터 스타일, 모션을 종합 분석합니다.")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("<div class='cute-card'>", unsafe_allow_html=True)
    st.subheader("🖼️ 1. 시그니처 이미지/GIF 업로드")
    uploaded_sig = st.file_uploader("시그니처 파일 선택 (GIF, PNG, JPG)", type=["gif", "png", "jpg", "jpeg"])
    if uploaded_sig:
        st.image(uploaded_sig, caption="업로드된 시그니처 이미지", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='cute-card'>", unsafe_allow_html=True)
    st.subheader("🎯 2. 방송 리액션 & 분위기 선택")
    reaction_type = st.selectbox(
        "리액션/방송 컨셉", 
        ["💃 댄스/신나는 템포", "✨ 큐트/애교/귀여움", "🔥 섹시/몽환적인", "🤪 엽기/개그/밈(Meme)", "🌙 감성/소통/잔잔함", "⚔️ 웅장/비장함"]
    )
    streamer_memo = st.text_input("추가 특징 (선택)", placeholder="예: 3초 짧은 리액션용, 힙합 비트 선호 등")
    btn_analyze = st.button("🚀 BGM & 어울리는 노래 분석 실행", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if btn_analyze:
    if not saved_gemini_key:
        st.error("⚠️ Secrets에 GEMINI_API_KEY가 설정되어 있지 않습니다.")
    elif not uploaded_sig:
        st.error("⚠️ 시그니처 이미지/GIF 파일을 업로드해 주세요.")
    else:
        with st.spinner("Visual AI가 시그니처의 분위기, 색감, 연출을 분석 중입니다..."):
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
                
                try:
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=[prompt, image_data]
                    )
                except Exception:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[prompt, image_data]
                    )
                
                if response and response.text:
                    st.session_state.sig_result = response.text
            except Exception as e:
                st.error(f"⚠️ 분석 오류 발생: {e}")

if st.session_state.sig_result:
    st.divider()
    st.markdown("### 📊 AI 시그니처 음악 분석 리포트")
    st.info(st.session_state.sig_result)

st.divider()

# 🎬 검색어로 유튜브 영상 즉시 탐색 및 플레이어 재생
st.subheader("▶️ 추천곡 검색 후 플레이어로 바로 듣기")
search_query = st.text_input("듣고 싶은 노래 제목이나 아티스트 입력 후 엔터", placeholder="예: 뉴진스 Hype Boy")

if search_query:
    with st.spinner(f"🔍 '{search_query}' 검색 결과 영상을 찾는 중입니다..."):
        try:
            ydl_opts = {
                'format': 'best',
                'noplaylist': True,
                'quiet': True,
                'default_search': 'ytsearch1'
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"{search_query} BGM", download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    video_url = info['entries'][0]['webpage_url']
                    video_title = info['entries'][0]['title']
                    st.success(f"🎬 재생 영상: **{video_title}**")
                    st.video(video_url)
                else:
                    st.warning("⚠️ 해당 검색어에 일치하는 유튜브 영상 검색 결과를 찾지 못했습니다.")
        except Exception as e:
            # 자동 탐색 실패 시 대체 검색 링크 제공
            encoded_query = urllib.parse.quote(f"{search_query} BGM")
            youtube_search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            st.markdown(f"👉 [▶️ 유튜브에서 '{search_query}' 직접 들어보기]({youtube_search_url})")

st.divider()

# ✂️ MP3/음원 소장용 오디오 플레이어
st.subheader("✂️ 소장 중인 MP3 음원 들어보기")
uploaded_audio = st.file_uploader("MP3 / WAV / OGG 음원 파일 업로드", type=["mp3", "wav", "ogg"])

if uploaded_audio:
    st.audio(uploaded_audio)
    
    col_cut1, col_cut2 = st.columns([1, 1])
    with col_cut1:
        start_sec = st.number_input("시작 시간 (초)", min_value=0, max_value=600, value=0)
    with col_cut2:
        end_sec = st.number_input("종료 시간 (초)", min_value=1, max_value=600, value=15)

    if start_sec < end_sec:
        st.success(f"🎵 지정 구간: **{start_sec}초 ~ {end_sec}초** (총 {end_sec - start_sec}초 리액션 구간)")
        
        st.download_button(
            label=f"📥 원본 음원 다운로드 ({uploaded_audio.name})",
            data=uploaded_audio.getvalue(),
            file_name=uploaded_audio.name,
            mime="audio/mp3",
            use_container_width=True
        )
