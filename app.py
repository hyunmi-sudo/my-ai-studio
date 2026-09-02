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

# 💾 그룹별(카테고리 & 세부 그룹) 저장소 초기화
if "saved_groups" not in st.session_state:
    st.session_state.saved_groups = {
        "prompts": {},    # { "그룹명/제목": [내용1, 내용2] }
        "plans": {},      # { "그룹명/제목": [내용1, 내용2] }
        "marketing": {}  # { "그룹명/제목": [내용1, 내용2] }
    }

if "curr_prompt" not in st.session_state: st.session_state.curr_prompt = None
if "curr_plan" not in st.session_state: st.session_state.curr_plan = None
if "curr_topic" not in st.session_state: st.session_state.curr_topic = ""

st.title("⚡ AI 영상 제작 & 올인원 마케팅 스튜디오 Pro")
st.caption("결과물을 확인한 뒤 원하는 그룹명(제목)을 설정하여 보관함에 체계적으로 저장할 수 있습니다.")
st.divider()

# 사이드바 API 설정 & 세부 그룹별 보관함
with st.sidebar:
    st.header("🔑 API 설정")
    gemini_key = st.text_input("1️⃣ Google Gemini API Key", value=saved_gemini_key, type="password")
    st.caption("[Google AI Studio](https://aistudio.google.com/) 무료 발급")
    st.divider()
    claude_key = st.text_input("2️⃣ Anthropic Claude API Key (선택)", type="password")
    
    st.divider()
    st.header("📂 그룹별 보관함")
    
    # 🎬 카테고리 1: 프롬프트
    with st.expander("🎬 영상 프롬프트 보관함", expanded=False):
        if st.session_state.saved_groups["prompts"]:
            for group_name, items in st.session_state.saved_groups["prompts"].items():
                st.markdown(f"**📁 {group_name}**")
                for idx, content in enumerate(items, 1):
                    st.code(content, language="markdown")
                    st.download_button(f"💾 {group_name}_{idx} 다운로드", content, file_name=f"{group_name}_{idx}.txt", key=f"dl_p_{group_name}_{idx}")
                st.markdown("---")
        else:
            st.caption("저장된 프롬프트가 없습니다.")

    # 📄 카테고리 2: 기획서
    with st.expander("📄 촬영 기획서 보관함", expanded=False):
        if st.session_state.saved_groups["plans"]:
            for group_name, items in st.session_state.saved_groups["plans"].items():
                st.markdown(f"**📁 {group_name}**")
                for idx, content in enumerate(items, 1):
                    st.code(content, language="markdown")
                    st.download_button(f"💾 {group_name}_{idx} 다운로드", content, file_name=f"{group_name}_{idx}.md", key=f"dl_pl_{group_name}_{idx}")
                st.markdown("---")
        else:
            st.caption("저장된 기획서가 없습니다.")

    # 🛠️ 카테고리 3: 마케팅 스튜디오
    with st.expander("🛠️ 마케팅 리포트 보관함", expanded=False):
        if st.session_state.saved_groups["marketing"]:
            for group_name, items in st.session_state.saved_groups["marketing"].items():
                st.markdown(f"**📁 {group_name}**")
                for idx, content in enumerate(items, 1):
                    st.code(content, language="markdown")
                    st.download_button(f"💾 {group_name}_{idx} 다운로드", content, file_name=f"{group_name}_{idx}.txt", key=f"dl_m_{group_name}_{idx}")
                st.markdown("---")
        else:
            st.caption("저장된 마케팅 리포트가 없습니다.")

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
        
        # 저장 레이아웃: 원하는 그룹명(제목) 지정 입력창
        save_col1, save_col2 = st.columns([2, 1])
        with save_col1:
            p_group_title = st.text_input("저장할 그룹명/제목을 입력하세요", value=st.session_state.curr_topic, key="p_group_title")
        with save_col2:
            st.write("") # 간격 맞춤
            st.write("")
            if st.button("💾 프롬프트 보관함에 저장", use_container_width=True):
                target_title = p_group_title.strip() if p_group_title.strip() else "기본 프롬프트 그룹"
                if target_title not in st.session_state.saved_groups["prompts"]:
                    st.session_state.saved_groups["prompts"][target_title] = []
                st.session_state.saved_groups["prompts"][target_title].append(st.session_state.curr_prompt)
                st.success(f"✅ '프롬프트 보관함 → [{target_title}]' 그룹에 저장되었습니다!")

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
        
        save_pl_col1, save_pl_col2 = st.columns([2, 1])
        with save_pl_col1:
            pl_group_title = st.text_input("저장할 그룹명/제목을 입력하세요", value=st.session_state.curr_topic, key="pl_group_title")
        with save_pl_col2:
            st.write("")
            st.write("")
            if st.button("💾 기획서 보관함에 저장", use_container_width=True):
                target_title = pl_group_title.strip() if pl_group_title.strip() else "기본 기획서 그룹"
                if target_title not in st.session_state.saved_groups["plans"]:
                    st.session_state.saved_groups["plans"][target_title] = []
                st.session_state.saved_groups["plans"][target_title].append(st.session_state.curr_plan)
                st.success(f"✅ '촬영 기획서 보관함 → [{target_title}]' 그룹에 저장되었습니다!")

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
        
        save_m_col1, save_m_col2 = st.columns([2, 1])
        with save_m_col1:
            m_group_title = st.text_input("저장할 그룹명/제목을 입력하세요", value=st.session_state.curr_m_topic, key="m_group_title")
        with save_m_col2:
            st.write("")
            st.write("")
            if st.button("💾 마케팅 리포트 보관함에 저장", use_container_width=True):
                target_title = m_group_title.strip() if m_group_title.strip() else "기본 마케팅 그룹"
                if target_title not in st.session_state.saved_groups["marketing"]:
                    st.session_state.saved_groups["marketing"][target_title] = []
                st.session_state.saved_groups["marketing"][target_title].append(st.session_state.curr_m_res)
                st.success(f"✅ '마케팅 리포트 보관함 → [{target_title}]' 그룹에 저장되었습니다!")
