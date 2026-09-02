import os
import streamlit as st
from google import genai
from PIL import Image
import urllib.parse

st.set_page_config(page_title="🎖️ 시그니처 BGM 작전본부 🎖️", layout="wide", page_icon="💥")

# 서든어택 밀리터리 FPS 다크/카키/오렌지 스타일링 CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #121417;
        color: #E2E8F0;
    }
    .main-title {
        color: #FF6B00;
        font-weight: 900;
        font-size: 2.3rem;
        text-align: center;
        letter-spacing: 2px;
        text-shadow: 0px 0px 10px rgba(255, 107, 0, 0.5);
        margin-bottom: 0px;
    }
    .sub-title {
        color: #8B9B90;
        text-align: center;
        font-size: 1.0rem;
        font-weight: bold;
        margin-bottom: 25px;
    }
    .sudden-card {
        background-color: #1C2026;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #FF6B00;
        border-top: 1px solid #2D3748;
        border-right: 1px solid #2D3748;
        border-bottom: 1px solid #2D3748;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF6B00 0%, #CC5200 100%) !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        border: 1px solid #FF8533 !important;
        font-weight: 900 !important;
        height: 52px !important;
        font-size: 1.1rem !important;
        letter-spacing: 1px !important;
        box-shadow: 0px 4px 12px rgba(255, 107, 0, 0.4) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #FF8533 0%, #FF6B00 100%) !important;
        border-color: #FFA366 !important;
    }
    </style>
""", unsafe_allow_html=True)

saved_gemini_key = st.secrets.get("GEMINI_API_KEY", "")

if "sig_result" not in st.session_state: st.session_state.sig_result = None

st.markdown("<p class='main-title'>🎖️ SUDDEN SIGNATURE BGM TACTICS 💥</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>[ 작전명 : 시그니처 비주얼 타겟팅 & 최적 리액션 BGM 제압 ]</p>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🔫 작전 통신망 상태")
    st.success("🎯 HQ 메인 레이더 연결 완료")
    st.info("💡 MISSION: 타겟 타임라인, 비주얼 컬러, 전투 템포를 타겟팅합니다.")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("<div class='sudden-card'>", unsafe_allow_html=True)
    st.subheader("📸 1. 타겟 시그니처 파일 장전")
    uploaded_sig = st.file_uploader("시그니처 이미지/GIF 움짤 투입 (GIF, PNG, JPG)", type=["gif", "png", "jpg", "jpeg"])
    if uploaded_sig:
        st.image(uploaded_sig, caption="💥 장전 완료된 타겟 시그니처", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='sudden-card'>", unsafe_allow_html=True)
    st.subheader("💣 2. 교전 리액션 & 전술 모드 선택")
    reaction_type = st.selectbox(
        "전투 및 리액션 장르", 
        ["💃 댄스/돌격 모드 (신나는 템포)", "✨ 큐트/위장 모드 (귀여움/애교)", "🔥 섹시/클로즈업 모드 (몽환적)", "🤪 개그/밈(Meme) 모드 (엽기/폭소)", "🌙 감성/소통 모드 (잔잔함)", "⚔️ 웅장/승리 모드 (비장함)"]
    )
    streamer_memo = st.text_input("추가 전술 커스텀 (선택)", placeholder="예: 3초 킬링포인트용, 힙합 비트 선호")
    btn_analyze = st.button("🔥 BGM 분석 & 작전 수행 개시!", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if btn_analyze:
    if not saved_gemini_key:
        st.error("⚠️ Secrets에 GEMINI_API_KEY 통신 키가 장전되지 않았습니다.")
    elif not uploaded_sig:
        st.error("⚠️ 타겟 시그니처 파일이 장전되지 않았습니다.")
    else:
        with st.spinner("🎯 Visual AI 타겟팅 레이더 가동 중..."):
            try:
                client = genai.Client(api_key=saved_gemini_key.strip())
                image_data = Image.open(uploaded_sig)
                
                prompt = f"""
                당신은 아프리카TV BJ 전문 방송 연출 감독이자 최고급 음악 사운드 디렉터입니다.
                업로드된 시그니처 이미지/움짤을 정밀 분석하고, 사용자가 선택한 전투 모드([{reaction_type}])와 추가 전술 커스텀([{streamer_memo}])에 가장 잘 어울리는 BGM 및 리액션 송을 추천하세요.

                [출력 형식]:
                1. 🎨 **시그니처 비주얼 & 타겟팅 분석**
                   - 메인 메인 컬러감 및 분위기
                   - 연출 파괴력 및 프레임 특징
                   - 추천 킬링 타임라인 (예: 0초~5초 하이라이트 파트)

                2. 💣 **최적 추천 BGM & 리액션 송 (총 5곡)**
                   - 곡명 / 아티스트
                   - 추천 타임라인 구간 (예: 15초~30초 하이라이트)
                   - 추천 사유 및 타격감 매칭 포인트

                3. 🎼 **AI 사운드 제작용 영문 프롬프트 (Suno / Udio 용)**
                   - Style of Music 영문 프롬프트
                """
                
                try:
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=[prompt, image_data]
                    )
                except Exception:
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=[prompt, image_data]
                    )
                
                if response and response.text:
                    st.session_state.sig_result = response.text
            except Exception as e:
                st.error(f"⚠️ 분석 오류 발생: {e}")

if st.session_state.sig_result:
    st.divider()
    st.markdown("### 📜 AI 시그니처 BGM 작전 지침서")
    st.info(st.session_state.sig_result)
    
    st.divider()
    st.subheader("✂️ 리액션 타임라인 구간 지정 지침서 다운로드")
    
    col_cut1, col_cut2, col_cut3 = st.columns([1, 1, 2])
    with col_cut1:
        start_sec = st.number_input("시작 타임라인 (초)", min_value=0, max_value=300, value=0)
    with col_cut2:
        end_sec = st.number_input("종료 타임라인 (초)", min_value=1, max_value=300, value=5)
    
    with col_cut3:
        st.write("")
        st.write("")
        custom_note = f"""[ 🎖️ 서든 시그니처 BGM 리액션 작전 가이드 ]
■ 지정 사용 구간: {start_sec}초 ~ {end_sec}초 (총 {end_sec - start_sec}초간 교전)

[ AI 음악 추천 작전지침서 전문 ]
{st.session_state.sig_result}
"""
        st.download_button(
            label=f"💾 [{start_sec}초 ~ {end_sec}초] 작전 지침서 메모장 다운로드",
            data=custom_note,
            file_name=f"Sudden_BGM_{start_sec}s_to_{end_sec}s.txt",
            use_container_width=True
        )

    st.divider()
    st.subheader("🔍 유튜브 추천 음원 정찰 바로가기")
    search_keyword = st.text_input("정찰할 음원 제목이나 아티스트 입력", placeholder="예: 서든어택 BGM")
    if search_keyword:
        encoded_query = urllib.parse.quote(f"{search_keyword} BGM")
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        st.markdown(f"👉 [▶️ 유튜브에서 '{search_keyword}' 정찰하기]({youtube_url})")
