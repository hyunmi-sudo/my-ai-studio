import os
import io
import time
import streamlit as st
from google import genai
from PIL import Image
import urllib.parse
import re

st.set_page_config(page_title="아프리카TV 시그니처 BGM 추천 AI", layout="wide", page_icon="🎵")

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
if "songs_list" not in st.session_state: st.session_state.songs_list = []

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

                2. 🎧 **추천 BGM 및 리액션 송 (총 5곡)**
                   (구간이나 타임라인 설명은 쓰지 말고, 곡명과 추천 이유만 간단히 적으세요)
                   ① 가수이름 - 노래제목
                   - 추천 이유 & 매칭 포인트: 설명
                   
                   ② 가수이름 - 노래제목
                   - 추천 이유 & 매칭 포인트: 설명

                   (5번 곡까지 동일 형식)
                """
                
                response = None
                # 503 과부하 대비 1차(2.5-flash), 2차(1.5-flash) 자동 분기 시도
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[prompt, image_data]
                    )
                except Exception as first_e:
                    if "503" in str(first_e) or "UNAVAILABLE" in str(first_e):
                        time.sleep(2)
                        response = client.models.generate_content(
                            model='gemini-1.5-flash',
                            contents=[prompt, image_data]
                        )
                    else:
                        raise first_e
                
                if response and response.text:
                    st.session_state.sig_result = response.text
                    
                    extracted_songs = re.findall(r'[①②③④⑤12345][.\s\)]*([^\n\r-]+-[^\n\r]+)', response.text)
                    if not extracted_songs:
                        extracted_songs = re.findall(r'(\w+[\s\w]*\s*-\s*[\w\s♡%()]+)', response.text)
                    st.session_state.songs_list = [s.strip('* ') for s in extracted_songs][:5]

            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    st.warning("⚡ 현재 구글 AI 서버에 순간 트래픽이 폭주하고 있습니다. 약 5초 후 아래 버튼을 눌러 다시 시도해주세요!")
                elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    st.warning("⏳ 트래픽 사용량이 일시 도달했습니다. 10초 후 다시 시도해 주세요!")
                else:
                    st.error(f"⚠️ 분석 오류 발생: {e}")

# 리포트 및 유튜브 플레이어 연동
if st.session_state.sig_result:
    st.divider()
    st.markdown("### 📊 AI 시그니처 음악 분석 리포트")
    st.markdown(st.session_state.sig_result)
    
    st.divider()
    st.subheader("🎬 추천곡 유튜브 현장 플레이어")
    
    if st.session_state.songs_list:
        for idx, song_title in enumerate(st.session_state.songs_list):
            st.markdown(f"#### 🎵 {idx+1}. {song_title}")
            encoded_query = urllib.parse.quote(f"{song_title} Official Audio")
            
            html_player = f"""
            <iframe width="100%" height="280" 
                src="https://www.youtube-nocookie.com/embed?listType=search&list={encoded_query}" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
            </iframe>
            """
            st.components.v1.html(html_player, height=290)
            st.divider()

st.divider()

# ✂️ MP3/음원 자르기 플레이어
st.subheader("✂️ 소장 중인 MP3 음원 자르기 & 들어보기")
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
