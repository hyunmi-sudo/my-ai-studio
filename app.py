import os
import streamlit as st
from google import genai
from PIL import Image

# 1. 페이지 기본 설정 및 레이아웃
st.set_page_config(page_title="AI 영상 제작 & 올인원 마케팅 스튜디오 Pro", layout="wide")

# 2. Secrets 또는 사이드바에서 API 키 로드
saved_gemini_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.header("🔑 API 설정")
    gemini_key = st.text_input("Google Gemini API Key", value=saved_gemini_key, type="password")
    st.caption("[Google AI Studio](https://aistudio.google.com/)에서 무료 발급")

st.title("⚡ AI 영상 제작 & 올인원 마케팅 스튜디오 Pro")
st.caption("생성된 결과물을 브랜드/제품별 폴더로 분류하여 보관함에 저장할 수 있습니다.")
st.divider()

# API 키 검증
if not gemini_key:
    st.warning("⚠️ 좌측 사이드바에 Gemini API Key를 입력해 주세요.")
    st.stop()

# GenAI 클라이언트 초기화
client = genai.Client(api_key=gemini_key)

# 3. 메인 탭 구성
tab1, tab2, tab3 = st.tabs([
    "🎬 1. 영상 제작 전용 AI 프롬프트 생성기",
    "📄 2. 영상 종합 기획서 & 촬영계획서 작성기",
    "🛠️ 3. 확장 마케팅 스튜디오"
])

with tab1:
    st.subheader("🎬 AI 영상 프롬프트 생성기")
    topic1 = st.text_input("영상 주제나 컨셉을 입력하세요", placeholder="예: 30대 직장인을 위한 스트레칭 홈트레이닝")
    if st.button("프롬프트 생성", key="btn1"):
        with st.spinner("AI가 프롬프트를 생성 중입니다..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"다음 주제에 대한 숏폼 영상 제작용 상세 프롬프트를 작성해줘: {topic1}"
            )
            st.markdown(response.text)

with tab2:
    st.subheader("📄 영상 종합 기획서 작성기")
    topic2 = st.text_input("기획할 영상의 목적이나 제품을 입력하세요", placeholder="예: 신제품 친환경 텀블러 와디즈 펀딩 홍보 영상")
    if st.button("기획서 작성", key="btn2"):
        with st.spinner("AI가 영상 기획서를 작성 중입니다..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"다음 주제에 대한 상세한 영상 촬영 기획서 및 씬별 콘티를 작성해줘: {topic2}"
            )
            st.markdown(response.text)

with tab3:
    st.subheader("🛠️ 확장 마케팅 스튜디오")
    st.info("다양한 브랜드/제품별 마케팅 보조 분석을 수행하고 마케팅 분석 리포트를 생성해보세요.")
    
    brand_name = st.text_input("브랜드/제품명", placeholder="예: 루미아 에스테틱")
    target_audience = st.text_input("타겟 고객층", placeholder="예: 2030 직장인 여성")
    marketing_goal = st.selectbox("마케팅 분석 목적", ["SWOT 분석", "경쟁사 비교 분석", "SNS 마케팅 전략", "카피라이팅 문구 추출"])
    
    if st.button("마케팅 리포트 생성", key="btn3"):
        with st.spinner("마케팅 분석 리포트를 작성 중입니다..."):
            prompt = f"브랜드명: {brand_name}\n타겟: {target_audience}\n목적: {marketing_goal}\n위 정보를 바탕으로 전문적인 마케팅 분석 리포트를 상세히 작성해줘."
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            st.markdown(response.text)
