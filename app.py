import os
import streamlit as st
from google import genai
from google.genai import types
import anthropic
import yt_dlp
import pandas as pd
from PIL import Image

st.set_page_config(page_title="AI 영상 제작 & 올인원 마케팅 스튜디오 Pro", layout="wide")

# Secrets에서 API 키 자동 로드
saved_gemini_key = st.secrets.get("GEMINI_API_KEY", "")

# 💾 그룹별(카테고리) 저장소 초기화
if "saved_items" not in st.session_state:
    st.session_state.saved_items = {
        "prompts": [],   # 프롬프트 그룹
        "plans": [],     # 기획서/촬영계획서 그룹
        "marketing": []  # 마케팅 스튜디오 그룹
    }

if "curr_prompt" not in st.session_state: st.session_state.curr_prompt = None
if "curr_plan" not in st.session_state: st.session_state.curr_plan = None
if "curr_topic" not in st.session_state: st.session_state.curr_topic = ""

st.title("⚡ AI 영상 제작 & 올인원 마케팅 스튜디오 Pro")
st.caption("결과물을 확인한 뒤 원하는 내용만 그룹별로 선택하여 저장소에 보관할 수 있습니다.")
st.divider()

# 사이드바 API 설정 & 그룹별 보관함
with st.sidebar:
    st.header("🔑 API 설정")
    gemini_key = st.text_input("1️⃣ Google Gemini API Key", value=saved_gemini_key, type="password")
    st.caption("[Google AI Studio](https://aistudio.google.com/) 무료 발급")
    st.divider()
    claude_key = st.text_input("2️⃣ Anthropic Claude API Key (선택)", type="password")
    
    st.divider()
    st.header("📂 그룹별 보관함")
    
    # 카테고리 1: 프롬프트
    with st.expander("🎬 영상 프롬프트 그룹", expanded=False):
        if st.session_state.saved_items["prompts"]:
            for idx, item in enumerate(st.session_state.saved_items["prompts"], 1):
                st.markdown(f"**{idx}. {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"Prompt_{idx}.txt", key=f"dl_p_{idx}")
        else: st.caption("저장된 프롬프트가 없습니다.")

    # 카테고리 2: 기획서
    with st.expander("📄 촬영 기획서 그룹", expanded=False):
        if st.session_state.saved_items["plans"]:
            for idx, item in enumerate(st.session_state.saved_items["plans"], 1):
                st.markdown(f"**{idx}. {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"Plan_{idx}.md", key=f"dl_pl_{idx}")
        else: st.caption("저장된 기획서가 없습니다.")

    # 카테고리 3: 마케팅
    with st.expander("🛠️ 마케팅 분석 리포트 그룹", expanded=False):
        if st.session_state.saved_items["marketing"]:
            for idx, item in enumerate(st.session_state.saved_items["marketing"], 1):
                st.markdown(f"**{idx}. {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"Marketing_{idx}.txt", key=f"dl_m_{idx}")
        else: st.caption("저장된 마케팅 리포트가 없습니다.")

def get_gemini_client():
    key_to_use = gemini_key.strip() if gemini_key else ""
    if not key_to_use:
        st.warning("왼쪽 사이드바에 Google Gemini API Key를 입력해 주세요.")
        return None
    try:
        return genai.Client(api_key=key_to_use)
    except Exception as e:
        st.error(f"Gemini 클라이언트 초기화 실패: {e}")
        return None

def safe_gemini_generate(client, contents_input):
    try:
        # 올바른 모델명인 gemini-1.5-flash로 수정
        response = client.models.generate_content(
            model='gemini-1.5-flash',
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
            st.info("Claude 연결 제외로 Gemini로 전환하여 처리합니다.")
    if gemini_client:
        return safe_gemini_generate(gemini_client, prompt)
    return None

main_tab1, main_tab2, main_tab3 = st.tabs([
    "🎬 1. 영상 제작 전용 AI 프롬프트 생성기", 
    "📄 2. 영상 종합 기획서 & 촬영계획서 작성기",
    "🛠️ 3. 확장 마케팅 스튜디오"
])

# 🎬 TAB 1: 프롬프트
with main_tab1:
    st.markdown("### 🎬 영상 제작용 AI 프롬프트 독립 생성")
    col_p1, col_p2 = st.columns([1, 1])
    with col_p1:
        p_topic = st.text_input("영상 주제 / 제품명", placeholder="예: 민트볼 틴케이스", key="p_topic")
        p_style = st.selectbox("영상 포맷", ["유튜브 숏폼/릴스/틱톡", "유튜브 롱폼", "브랜드 홍보 CF"], key="p_style")
    with col_p2:
        p_tone = st.text_input("원하는 톤앤매너", placeholder="예: 트렌디함, 감성적인", key="p_tone")
        p_detail = st.text_area("핵심 메시지", placeholder="내용을 입력하세요", height=100, key="p_detail")

    if st.button("🚀 영상 제작용 프롬프트 생성 실행", type="primary", use_container_width=True):
        gemini_client = get_gemini_client()
        if p_topic and p_detail and gemini_client:
            with st.spinner("프롬프트 생성 중..."):
                prompt_req = f"주제: {p_topic}, 포맷: {p_style}, 톤: {p_tone}, 내용: {p_detail} 바탕으로 영상 제작 프롬프트 및 마스터 템플릿을 만드세요."
                res = generate_claude_or_gemini(prompt_req, gemini_client)
                if res:
                    st.session_state.curr_prompt = res
                    st.session_state.curr_topic = p_topic

    if st.session_state.curr_prompt:
        st.divider()
        st.markdown("#### 📌 생성된 영상 제작용 프롬프트")
        st.info(st.session_state.curr_prompt)
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("💾 이 프롬프트 [영상 프롬프트 그룹]에 저장하기", use_container_width=True):
                st.session_state.saved_items["prompts"].append({
                    "title": st.session_state.curr_topic,
                    "content": st.session_state.curr_prompt
                })
                st.success("✅ '영상 프롬프트 그룹' 보관함에 저장되었습니다!")
        with col_btn2:
            st.download_button("📥 텍스트 다운로드", data=st.session_state.curr_prompt, file_name="Prompt.txt", use_container_width=True)

# 📄 TAB 2: 기획서 & 촬영계획서
with main_tab2:
    st.markdown("### 📄 영상 종합 기획서 & 촬영계획서 작성")
    col_g1, col_g2 = st.columns([1, 1])
    with col_g1:
        g_title = st.text_input("기획 프로젝트명", placeholder="예: 민트볼 틴케이스", key="g_title")
        g_target = st.text_input("타겟 시청자층", placeholder="예: 2030대", key="g_target")
    with col_g2:
        g_location = st.text_input("촬영 장소", placeholder="예: 사무실, 카페", key="g_location")
        g_goal = st.text_area("제작 목적 및 세부 내용", placeholder="세부 내용 입력", height=100, key="g_goal")

    if st.button("📄 영상 기획서 & 촬영계획서 생성 실행", type="primary", use_container_width=True):
        gemini_client = get_gemini_client()
        if g_title and g_goal and gemini_client:
            with st.spinner("기획서 및 씬별 촬영계획서 작성 중..."):
                plan_req = f"프로젝트명: {g_title}, 타겟: {g_target}, 장소: {g_location}, 내용: {g_goal} 바탕으로 영상 종합 기획서, 씬별 촬영계획서(표), 체크리스트를 작성하세요."
                res_pl = safe_gemini_generate(gemini_client, plan_req)
                if res_pl:
                    st.session_state.curr_plan = res_pl
                    st.session_state.curr_topic = g_title

    if st.session_state.curr_plan:
        st.divider()
        st.markdown("#### 📄 생성된 영상 종합 기획서 & 촬영계획서")
        st.success(st.session_state.curr_plan)
        
        col_pbtn1, col_pbtn2 = st.columns([1, 1])
        with col_pbtn1:
            if st.button("💾 이 기획서 [촬영 기획서 그룹]에 저장하기", use_container_width=True):
                st.session_state.saved_items["plans"].append({
                    "title": st.session_state.curr_topic,
                    "content": st.session_state.curr_plan
                })
                st.success("✅ '촬영 기획서 그룹' 보관함에 저장되었습니다!")
        with col_pbtn2:
            st.download_button("📥 마크다운 다운로드", data=st.session_state.curr_plan, file_name="Plan.md", use_container_width=True)

# 🛠️ TAB 3: 마케팅 스튜디오
with main_tab3:
    st.markdown("### 🛠️ 확장 마케팅 스튜디오")
    st.info("지표 수집, 이미지 분석, 인플루언서 탐색 등 마케팅 관련 보조 기능을 사용하는 공간입니다.")
    
    b_name = st.text_input("브랜드/제품명", placeholder="예: 루미아 에스테틱", key="m_bname")
    m_target = st.text_input("타겟 고객층", placeholder="예: 2030 직장인 여성", key="m_target")
    m_goal = st.selectbox("마케팅 분석 목적", ["SWOT 분석", "경쟁사 비교 분석", "SNS 마케팅 전략", "카피라이팅 문구 추출"], key="m_goal")
    
    if st.button("🛠️ 마케팅 리포트 생성 실행", type="primary", use_container_width=True):
        gemini_client = get_gemini_client()
        if b_name and gemini_client:
            with st.spinner("마케팅 분석 리포트를 작성 중입니다..."):
                m_prompt = f"브랜드명: {b_name}\n타겟: {m_target}\n목적: {m_goal}\n위 정보를 바탕으로 전문적인 마케팅 분석 리포트를 상세히 작성해줘."
                res_m = safe_gemini_generate(gemini_client, m_prompt)
                if res_m:
                    st.session_state.curr_m_res = res_m
                    st.session_state.curr_m_topic = b_name

    if "curr_m_res" in st.session_state and st.session_state.curr_m_res:
        st.divider()
        st.markdown("#### 🛠️ 생성된 마케팅 리포트")
        st.markdown(st.session_state.curr_m_res)
        
        col_mbtn1, col_mbtn2 = st.columns([1, 1])
        with col_mbtn1:
            if st.button("💾 이 리포트 [마케팅 분석 리포트 그룹]에 저장하기", use_container_width=True):
                st.session_state.saved_items["marketing"].append({
                    "title": st.session_state.curr_m_topic,
                    "content": st.session_state.curr_m_res
                })
                st.success("✅ '마케팅 분석 리포트 그룹' 보관함에 저장되었습니다!")
        with col_mbtn2:
            st.download_button("📥 텍스트 다운로드", data=st.session_state.curr_m_res, file_name="Marketing_Report.txt", use_container_width=True)
