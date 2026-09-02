import os
import streamlit as st
from google import genai
from PIL import Image
import urllib.parse

st.set_page_config(page_title="아프리카TV 시그니처 BGM 추천 AI", layout="wide", page_icon="🎵")

# Secrets에서 API 키 자동 로드
saved_gemini_key = st.secrets.get("GEMINI_API_KEY", "")

# 세션 보관함 초기화
if "sig_result" not in st.session_state: st.session_state.sig_result = None

st.title("🎵 아프리카TV 시그니처 이미지 BGM & 노래 추천 AI")
st.caption("시그니처 이미지나 GIF 움짤을 업로드하면 Visual AI가 분위기를 분석하여 가장 잘 어울리는 BGM과 리액션 송을 추천해 드립니다.")
st.divider()

# 사이드바 API 설정
with st.sidebar:
    st.header("🔑 API 연결 상태")
    st.success("✅ Google Gemini API 연결 완료")
    st.info("💡 TIP: 시그니처의 색감, 캐릭터 스타일, 모션을 종합 분석합니다.")

# 메인 UI 구성
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("🖼️ 1. 시그니처 이미지/움짤 업로드")
    uploaded_sig = st.file_uploader("시그니처 파일 선택 (GIF, PNG, JPG)", type=["gif", "png", "jpg", "jpeg"])
    
    if uploaded_sig:
        st.image(uploaded_sig, caption="업로드된 시그니처", use_container_width=True)

with col_right:
    st.subheader("🎯 2. 방송 리액션 & 분위기 설정")
    reaction_type = st.selectbox(
        "리액션/방송 컨셉", 
        ["💃 댄스/신나는 템포", "✨ 큐트/애교/귀여움", "🔥 섹시/몽환적인", "🤪 엽기/개그/밈(Meme)", "🌙 감성/소통/잔잔함", "⚔️ 웅장/비장함"]
    )
    
    streamer_memo = st.text_input("추가 특징 (선택)", placeholder="예: 3초 짧은 리액션용, 힙합 느낌 선호 등")
    
    btn_analyze = st.button("🚀 BGM & 어울리는 노래 분석 실행", type="primary", use_container_width=True)

# AI 분석 실행
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
                   - 어울리는 음악 장르 및 추천 BPM

                2. 🎧 **추천 BGM 및 리액션 송 (총 5곡)**
                   - 곡명 / 아티스트
                   - 추천 이유 및 시그니처와 매칭되는 시점(하이라이트/킬링포인트)
                   - 분위기 태그

                3. 🎼 **AI 음악 생성용 영문 프롬프트 (Suno / Udio 용)**
                   - 이 시그니처 전용 BGM을 AI로 직접 만들 때 입력할 Style of Music 영문 프롬프트
                """
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=[prompt, image_data]
                )
                
                if response and response.text:
                    st.session_state.sig_result = response.text
            except Exception as e:
                st.error(f"⚠️ 분석 오류 발생: {e}")

# 결과 출력
if st.session_state.sig_result:
    st.divider()
    st.markdown("### 📊 AI 시그니처 음악 분석 리포트")
    st.markdown(st.session_state.sig_result)
    
    st.divider()
    st.subheader("🔍 유튜브에서 추천곡 검색 바로가기")
    search_keyword = st.text_input("검색할 노래 제목이나 아티스트 입력", placeholder="예: 뉴진스 Hype Boy")
    if search_keyword:
        encoded_query = urllib.parse.quote(f"{search_keyword} BGM")
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        st.markdown(f"👉 [▶️ 유튜브에서 '{search_keyword}' 검색해서 들어보기]({youtube_url})")
