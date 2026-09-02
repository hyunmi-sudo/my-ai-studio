import streamlit as st
from google import genai
import anthropic
import yt_dlp
import pandas as pd
from PIL import Image

# 🔑 secrets.toml에서 최신 API 키 자동 로드
saved_gemini_key = st.secrets.get("GEMINI_API_KEY", "")

st.set_page_config(page_title="AI 영상 제작 & 올인원 마케팅 스튜디오 Pro", layout="wide")

# 💾 2단계 계층 구조(그룹 -> 브랜드/제품) 저장소 초기화
if "saved_groups" not in st.session_state:
    st.session_state.saved_groups = {
        "prompts": {},   # 영상 프롬프트 그룹
        "plans": {},     # 촬영 기획서 그룹
        "marketing": {} # 마케팅 분석 리포트 그룹
    }

if "curr_prompt" not in st.session_state: st.session_state.curr_prompt = None
if "curr_plan" not in st.session_state: st.session_state.curr_plan = None

st.title("⚡ AI 영상 제작 & 올인원 마케팅 스튜디오 Pro")
st.caption("생성된 결과물을 브랜드/제품별 폴더로 분류하여 그룹 보관함에 정밀 저장할 수 있습니다.")
st.divider()

# 사이드바 API 설정 (secrets 자동 입력)
with st.sidebar:
    st.header("🔑 API 설정")
    gemini_key = st.text_input("1️⃣ Google Gemini API Key", value=saved_gemini_key, type="password")
    st.caption("[Google AI Studio](https://aistudio.google.com/) 무료 발급")
    st.divider()
    claude_key = st.text_input("2️⃣ Anthropic Claude API Key (선택)", type="password")
    
    st.divider()
    st.header("📂 그룹 & 브랜드별 보관함")
    
    # 카테고리 1: 영상 프롬프트 그룹
    with st.expander("🎬 영상 프롬프트 그룹", expanded=True):
        prompts_dict = st.session_state.saved_groups["prompts"]
        if prompts_dict:
            for b_name, items in prompts_dict.items():
                st.markdown(f"📁 **[{b_name}]**")
                for idx, item in enumerate(items, 1):
                    with st.popover(f"└ 📄 {idx}. {item['title']}"):
                        st.code(item['content'], language="markdown")
                        st.download_button("💾 다운로드", item['content'], file_name=f"{b_name}_Prompt_{idx}.txt", key=f"dl_p_{b_name}_{idx}")
        else: st.caption("저장된 프롬프트가 없습니다.")

    # 카테고리 2: 촬영 기획서 그룹
    with st.expander("📄 촬영 기획서 그룹", expanded=False):
        plans_dict = st.session_state.saved_groups["plans"]
        if plans_dict:
            for b_name, items in plans_dict.items():
                st.markdown(f"📁 **[{b_name}]**")
                for idx, item in enumerate(items, 1):
                    with st.popover(f"└ 📄 {idx}. {item['title']}"):
                        st.code(item['content'], language="markdown")
                        st.download_button("💾 다운로드", item['content'], file_name=f"{b_name}_Plan_{idx}.md", key=f"dl_pl_{b_name}_{idx}")
        else: st.caption("저장된 기획서가 없습니다.")

    # 카테고리 3: 마케팅 분석 리포트 그룹
    with st.expander("🛠️ 마케팅 분석 리포트 그룹", expanded=False):
        mkt_dict = st.session_state.saved_groups["marketing"]
        if mkt_dict:
            for b_name, items in mkt_dict.items():
                st.markdown(f"📁 **[{b_name}]**")
                for idx, item in enumerate(items, 1):
                    with st.popover(f"└ 📄 {idx}. {item['title']}"):
                        st.code(item['content'], language="markdown")
                        st.download_button("💾 다운로드", item['content'], file_name=f"{b_name}_Mkt_{idx}.txt", key=f"dl_m_{b_name}_{idx}")
        else: st.caption("저장된 마케팅 리포트가 없습니다.")

def get_gemini_client():
    if not gemini_key or not gemini_key.strip():
        st.warning("왼쪽 사이드바에 Google Gemini API Key를 입력해 주세요.")
        return None
    try:
        # 최신 SDK 규격 적용
        return genai.Client(api_key=gemini_key.strip())
    except Exception as e:
        st.error(f"Gemini 클라이언트 초기화 실패: {e}")
        return None

def safe_gemini_generate(client, contents_input):
    try:
        # 구글 최신 권장 모델 gemini-3.6-flash 지정
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
            st.info("Claude 연결 제외로 Gemini로 전환하여 처리합니다.")
    if gemini_client:
        return safe_gemini_generate(gemini_client, prompt)
    return None

main_tab1, main_tab2, main_tab3 = st.tabs([
    "🎬 1. 영상 제작 전용 AI 프롬프트 생성기", 
    "📄 2. 영상 종합 기획서 & 촬영계획서 작성기",
    "🛠️ 3. 확장 마케팅 스튜디오"
])

# 🎬 TAB 1: 프롬프트 생성기
with main_tab1:
    st.markdown("### 🎬 영상 제작용 AI 프롬프트 독립 생성")
    col_p1, col_p2 = st.columns([1, 1])
    with col_p1:
        brand_p = st.text_input("🏷️ 브랜드 / 제품명 (보관함 폴더명으로 활용)", placeholder="예: 민트볼 틴케이스", key="brand_p")
        p_style = st.selectbox("영상 포맷", ["유튜브 숏폼/릴스/틱톡", "유튜브 롱폼", "브랜드 홍보 CF"], key="p_style")
    with col_p2:
        p_tone = st.text_input("원하는 톤앤매너", placeholder="예: 트렌디함, 감성적인", key="p_tone")
        p_detail = st.text_area("핵심 메시지 및 요구사항", placeholder="프롬프트에 담을 내용을 입력하세요", height=100, key="p_detail")

    if st.button("🚀 영상 제작용 프롬프트 생성 실행", type="primary", use_container_width=True):
        gemini_client = get_gemini_client()
        if brand_p and p_detail and gemini_client:
            with st.spinner("프롬프트 생성 중..."):
                prompt_req = f"브랜드/제품: {brand_p}, 포맷: {p_style}, 톤: {p_tone}, 내용: {p_detail} 바탕으로 영상 제작 프롬프트 및 마스터 템플릿을 작성하세요."
                res = generate_claude_or_gemini(prompt_req, gemini_client)
                if res:
                    st.session_state.curr_prompt = res

    if st.session_state.curr_prompt:
        st.divider()
        st.markdown(f"#### 📌 생성된 프롬프트 결과 (`브랜드: {brand_p}`)")
        st.info(st.session_state.curr_prompt)
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button(f"💾 이 결과를 [영상 프롬프트 그룹 ➡️ {brand_p}] 폴더에 저장", use_container_width=True):
                target_folder = brand_p.strip() if brand_p.strip() else "공통 브랜드"
                if target_folder not in st.session_state.saved_groups["prompts"]:
                    st.session_state.saved_groups["prompts"][target_folder] = []
                
                st.session_state.saved_groups["prompts"][target_folder].append({
                    "title": f"{p_style} 프롬프트",
                    "content": st.session_state.curr_prompt
                })
                st.success(f"✅ '🎬 영상 프롬프트 그룹 ➡️ [{target_folder}]' 폴더에 저장되었습니다!")
        with col_btn2:
            st.download_button("📥 텍스트 다운로드", data=st.session_state.curr_prompt, file_name=f"{brand_p}_Prompt.txt", use_container_width=True)

# 📄 TAB 2: 기획서 & 촬영계획서
with main_tab2:
    st.markdown("### 📄 영상 종합 기획서 & 촬영계획서 작성")
    col_g1, col_g2 = st.columns([1, 1])
    with col_g1:
        brand_g = st.text_input("🏷️ 브랜드 / 제품명 (보관함 폴더명으로 활용)", placeholder="예: 민트볼 틴케이스", key="brand_g")
        g_target = st.text_input("타겟 시청자층", placeholder="예: 2030대", key="g_target")
    with col_g2:
        g_location = st.text_input("촬영 장소", placeholder="예: 사무실, 카페", key="g_location")
        g_goal = st.text_area("제작 목적 및 세부 내용", placeholder="기획 내용을 입력하세요", height=100, key="g_goal")

    if st.button("📄 영상 기획서 & 촬영계획서 생성 실행", type="primary", use_container_width=True):
        gemini_client = get_gemini_client()
        if brand_g and g_goal and gemini_client:
            with st.spinner("기획서 및 씬별 촬영계획서 작성 중..."):
                plan_req = f"브랜드/제품: {brand_g}, 타겟: {g_target}, 장소: {g_location}, 내용: {g_goal} 바탕으로 영상 종합 기획서, 씬별 촬영계획서(표), 체크리스트를 작성하세요."
                res_pl = safe_gemini_generate(gemini_client, plan_req)
                if res_pl:
                    st.session_state.curr_plan = res_pl

    if st.session_state.curr_plan:
        st.divider()
        st.markdown(f"#### 📄 생성된 영상 기획서 & 촬영계획서 (`브랜드: {brand_g}`)")
        st.success(st.session_state.curr_plan)
        
        col_pbtn1, col_pbtn2 = st.columns([1, 1])
        with col_pbtn1:
            if st.button(f"💾 이 결과를 [촬영 기획서 그룹 ➡️ {brand_g}] 폴더에 저장", use_container_width=True):
                target_folder = brand_g.strip() if brand_g.strip() else "공통 브랜드"
                if target_folder not in st.session_state.saved_groups["plans"]:
                    st.session_state.saved_groups["plans"][target_folder] = []
                
                st.session_state.saved_groups["plans"][target_folder].append({
                    "title": f"촬영 기획서 및 콘티",
                    "content": st.session_state.curr_plan
                })
                st.success(f"✅ '📄 촬영 기획서 그룹 ➡️ [{target_folder}]' 폴더에 저장되었습니다!")
        with col_pbtn2:
            st.download_button("📥 마크다운 다운로드", data=st.session_state.curr_plan, file_name=f"{brand_g}_Plan.md", use_container_width=True)

# 🛠️ TAB 3: 마케팅 스튜디오
with main_tab3:
    st.markdown("### 🛠️ 확장 마케팅 스튜디오")
    st.info("다양한 브랜드/제품별 마케팅 보조 분석을 수행하고 마케팅 분석 리포트 그룹에 저장해보세요.")
