import os
import io
import time
import re
import tempfile
import streamlit as st
from google import genai
import anthropic
import yt_dlp
import pandas as pd
from PIL import Image

st.set_page_config(page_title="AI 영상 제작 & 마케팅 스튜디오 Pro", layout="wide", page_icon="⚡")

default_secrets_key = st.secrets.get("GEMINI_API_KEY", "")

# 🎨 다크 모드 스타일 고정
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }
    [data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 1px solid #334155 !important;
    }
    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    h1, h2, h3, h4, h5, h6, label, p, span, div {
        color: #F8FAFC !important;
    }
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border-color: #475569 !important;
        color: #F8FAFC !important;
    }
    div[data-baseweb="input"] input {
        color: #F8FAFC !important;
    }
    div[data-testid="stDataEditor"], .stDataFrame {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stAlert"] * {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 💾 저장소 세션 초기화
default_items = {
    "prompts": [], "plans": [], "yt_diag": [], 
    "img_analysis": [], "influencer": [], "calendar": [], "copywriting": []
}

if "saved_items" not in st.session_state:
    st.session_state.saved_items = default_items
else:
    for key, val in default_items.items():
        if key not in st.session_state.saved_items:
            st.session_state.saved_items[key] = val

if "saved_prompt_result" not in st.session_state: st.session_state.saved_prompt_result = None
if "saved_plan_result" not in st.session_state: st.session_state.saved_plan_result = None
if "saved_yt_result" not in st.session_state: st.session_state.saved_yt_result = None
if "saved_img_result" not in st.session_state: st.session_state.saved_img_result = None
if "saved_inf_result" not in st.session_state: st.session_state.saved_inf_result = None
if "saved_cal_result" not in st.session_state: st.session_state.saved_cal_result = None
if "saved_copy_result" not in st.session_state: st.session_state.saved_copy_result = None

st.title("⚡ AI 영상 제작 & 올인원 마케팅 스튜디오 Pro")
st.divider()

# 🔑 사이드바 API 설정
with st.sidebar:
    st.header("🔑 Gemini API 키 설정")
    
    user_gemini_key = st.text_input(
        "개인 Gemini API 키 입력", 
        type="password", 
        placeholder="AQ...",
        help="개인 API 키를 입력하시면 공유 제한 없이 본인 전용 할당량으로 즉시 작동합니다."
    )
    
    active_gemini_key = user_gemini_key.strip() if user_gemini_key.strip() else default_secrets_key.strip()
    
    if active_gemini_key:
        if user_gemini_key.strip():
            st.success("✅ 개인 API 키 연결 완료 (우선 사용)")
        else:
            st.info("ℹ️ 기본 공유 API 키 연결 중")
    else:
        st.warning("⚠️ API 키가 입력되지 않았습니다.")
        
    claude_key = st.text_input("Anthropic Claude API Key (선택)", type="password")

    st.divider()
    st.header("📂 카테고리별 보관함")
    
    with st.expander("🎬 영상 프롬프트 보관함", expanded=False):
        if st.session_state.saved_items.get("prompts"):
            for idx, item in enumerate(st.session_state.saved_items["prompts"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_p_{idx}")
                st.markdown("---")
        else: st.caption("저장된 프롬프트가 없습니다.")

    with st.expander("📄 촬영 기획서 보관함", expanded=False):
        if st.session_state.saved_items.get("plans"):
            for idx, item in enumerate(st.session_state.saved_items["plans"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.md", key=f"dl_pl_{idx}")
                st.markdown("---")
        else: st.caption("저장된 기획서가 없습니다.")

    with st.expander("🎥 유튜브 진단 보관함", expanded=False):
        if st.session_state.saved_items.get("yt_diag"):
            for idx, item in enumerate(st.session_state.saved_items["yt_diag"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_yt_{idx}")
                st.markdown("---")
        else: st.caption("저장된 진단 리포트가 없습니다.")

    with st.expander("📸 시각적 미디어 분석 보관함", expanded=False):
        if st.session_state.saved_items.get("img_analysis"):
            for idx, item in enumerate(st.session_state.saved_items["img_analysis"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_img_{idx}")
                st.markdown("---")
        else: st.caption("저장된 분석 결과가 없습니다.")

    with st.expander("👥 인플루언서 매칭 보관함", expanded=False):
        if st.session_state.saved_items.get("influencer"):
            for idx, item in enumerate(st.session_state.saved_items["influencer"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_inf_{idx}")
                st.markdown("---")
        else: st.caption("저장된 매칭 가이드가 없습니다.")

    with st.expander("📅 30일 달력 보관함", expanded=False):
        if st.session_state.saved_items.get("calendar"):
            for idx, item in enumerate(st.session_state.saved_items["calendar"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_cal_{idx}")
                st.markdown("---")
        else: st.caption("저장된 달력이 없습니다.")

    with st.expander("✍️ 카피라이팅 보관함", expanded=False):
        if st.session_state.saved_items.get("copywriting"):
            for idx, item in enumerate(st.session_state.saved_items["copywriting"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_copy_{idx}")
                st.markdown("---")
        else: st.caption("저장된 카피가 없습니다.")

def get_gemini_client():
    if not active_gemini_key:
        st.error("⚠️ 사용할 Gemini API 키가 없습니다. 사이드바에 개인 키를 입력해 주세요.")
        return None
    try:
        return genai.Client(api_key=active_gemini_key)
    except Exception as e:
        st.error(f"Gemini 초기화 오류: {e}")
        return None

# 🛡️ 503 과부하 자동 전환 우회 핸들러
def safe_gemini_generate(client, contents_input):
    models_to_try = ['gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-2.5-flash']
    last_error = ""

    for target_model in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=target_model,
                    contents=contents_input
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = str(e)
                if "503" in last_error or "UNAVAILABLE" in last_error or "high demand" in last_error:
                    time.sleep(1.5)
                    continue
                elif "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                    st.error("⚠️ 일일 사용 한도가 초과되었습니다. 개인 API 키 상태를 확인해 주세요.")
                    return None
                else:
                    break

    st.error("⚠️ 구글 서버 트래픽이 일시적으로 높은 상태입니다. 10초 후 다시 시도해 주세요.")
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
            pass
    if gemini_client:
        return safe_gemini_generate(gemini_client, prompt)
    return None

def get_youtube_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'url': url,
                'title': info.get('title') or 'N/A',
                'views': info.get('view_count') or 0,
                'likes': info.get('like_count') or 0,
                'comments': info.get('comment_count') or 0,
                'channel': info.get('uploader') or 'N/A'
            }
    except Exception:
        return {'url': url, 'title': '정보 수집 실패', 'views': 0, 'likes': 0, 'comments': 0, 'channel': 'N/A'}

main_tab1, main_tab2, main_tab3 = st.tabs([
    "🎬 1. 영상 제작 전용 AI 프롬프트 생성기", 
    "📄 2. 영상 종합 기획서 & 촬영계획서 작성기",
    "🛠️ 3. 확장 마케팅 스튜디오"
])

# ==========================================
# 🎬 TAB 1: 영상 제작 전용 프롬프트 생성기
# ==========================================
with main_tab1:
    st.markdown("### 🎬 영상 제작용 AI 프롬프트 독립 생성")
    col_p1, col_p2 = st.columns([1, 1])
    with col_p1:
        p_topic = st.text_input("영상 주제 / 제품명", placeholder="예: 민트볼 틴케이스 숏폼 홍보 영상", key="p_topic")
        p_style = st.selectbox("영상 포맷", ["유튜브 숏폼/릴스/틱톡 (15~60초)", "유튜브 롱폼 (5~10분)", "브랜드 홍보 CF", "제품 언박싱/리뷰"], key="p_style")
    with col_p2:
        p_tone = st.text_input("원하는 톤앤매너 & 감성", placeholder="예: 트렌디함, B급 유머, 감성적인", key="p_tone")
        p_detail = st.text_area("핵심 메시지", placeholder="예: 휴대성과 상쾌함 강조", height=100, key="p_detail")

    if st.button("🚀 영상 제작용 프롬프트 생성 실행", type="primary", use_container_width=True):
        gemini_client = get_gemini_client()
        if p_topic and p_detail and gemini_client:
            with st.spinner("프롬프트 생성 중..."):
                prompt_req = f"주제: {p_topic}, 포맷: {p_style}, 톤: {p_tone}, 내용: {p_detail} 바탕으로 전문 프롬프트를 한국어로 작성하세요."
                res = generate_claude_or_gemini(prompt_req, gemini_client)
                if res:
                    st.session_state.saved_prompt_result = res

    if st.session_state.saved_prompt_result:
        st.divider()
        st.markdown("#### 📌 생성된 영상 제작용 프롬프트 결과")
        st.info(st.session_state.saved_prompt_result)
        save_p_title = st.text_input("저장할 제목 입력", value=f"{p_topic} 프롬프트", key="save_p_title")
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("💾 영상 프롬프트 보관함에 저장", use_container_width=True):
                st.session_state.saved_items["prompts"].append({
                    "title": save_p_title.strip() if save_p_title.strip() else "제목 없음",
                    "content": st.session_state.saved_prompt_result
                })
                st.success("✅ '영상 프롬프트 보관함'에 저장되었습니다!")
                st.rerun()
        with col_btn2:
            st.download_button("📥 텍스트 다운로드", data=st.session_state.saved_prompt_result, file_name="Prompt.txt", use_container_width=True)

# ==========================================
# 📄 TAB 2: 영상 기획서 & 촬영계획서 작성기
# ==========================================
with main_tab2:
    st.markdown("### 📄 영상 종합 기획서 & 촬영계획서 작성")
    col_g1, col_g2 = st.columns([1, 1])
    with col_g1:
        g_title = st.text_input("기획 프로젝트명", placeholder="예: 민트볼 틴케이스", key="g_title")
        g_target = st.text_input("타겟 시청자층", placeholder="예: 2030대", key="g_target")
    with col_g2:
        g_location = st.text_input("촬영 장소", placeholder="예: 카페, 야외 공원", key="g_location")
        g_goal = st.text_area("제작 목적 및 세부 내용", placeholder="내용 입력", height=100, key="g_goal")

    if st.button("📄 영상 기획서 & 촬영계획서 생성 실행", type="primary", use_container_width=True):
        gemini_client = get_gemini_client()
        if g_title and g_goal and gemini_client:
            with st.spinner("촬영계획서 작성 중..."):
                plan_req = f"프로젝트명: {g_title}, 타겟: {g_target}, 장소: {g_location}, 내용: {g_goal} 바탕으로 촬영계획서를 한국어로 작성하세요."
                res_pl = safe_gemini_generate(gemini_client, plan_req)
                if res_pl:
                    st.session_state.saved_plan_result = res_pl

    if st.session_state.saved_plan_result:
        st.divider()
        st.markdown("#### 📄 생성된 영상 종합 기획서 & 촬영계획서")
        st.success(st.session_state.saved_plan_result)
        save_pl_title = st.text_input("저장할 제목 입력", value=f"{g_title} 촬영기획서", key="save_pl_title")
        col_pbtn1, col_pbtn2 = st.columns([1, 1])
        with col_pbtn1:
            if st.button("💾 촬영 기획서 보관함에 저장", use_container_width=True):
                st.session_state.saved_items["plans"].append({
                    "title": save_pl_title.strip() if save_pl_title.strip() else "제목 없음",
                    "content": st.session_state.saved_plan_result
                })
                st.success("✅ '촬영 기획서 보관함'에 저장되었습니다!")
                st.rerun()
        with col_pbtn2:
            st.download_button("📥 마크다운 다운로드", data=st.session_state.saved_plan_result, file_name="Plan.md", use_container_width=True)

# ==========================================
# 🛠️ TAB 3: 확장 마케팅 스튜디오
# ==========================================
with main_tab3:
    st.markdown("### 🛠️ 확장 마케팅 스튜디오")
    tab_yt_std, tab_img, tab_inf, tab_cal, tab_copy = st.tabs([
        "🎥 내 유튜브 영상 성과 진단", 
        "📸🎥 이미지 & 동영상 AI 종합 분석기", 
        "👥 키워드 기반 인플루언서 탐색", 
        "📅 30일 콘텐츠 달력 생성기",
        "✍️ 마케팅 카피라이팅 추출기"
    ])

    with tab_yt_std:
        st.markdown("#### 🎥 유튜브 영상 URL 입력 진단")
        standalone_urls = st.text_area("유튜브 URL 목록 (한 줄에 하나씩)", height=100)
        if st.button("📊 영상 성과 진단 실행", use_container_width=True):
            gemini_client = get_gemini_client()
            if gemini_client and standalone_urls.strip():
                url_list = [u.strip() for u in standalone_urls.strip().split('\n') if u.strip()]
                with st.spinner("유튜브 데이터 분석 중..."):
                    fetched = []
                    for idx, url in enumerate(url_list, start=1):
                        try:
                            info = get_youtube_info(url)
                            info['id'] = f"영상 {idx}"
                            fetched.append(info)
                        except Exception as e: pass
                    if fetched:
                        v_summary = "".join([f"\n- [{d['id']}] 제목:{d['title']} / 조회수:{d['views']} / 좋아요:{d['likes']}" for d in fetched])
                        res_yt = safe_gemini_generate(gemini_client, f"다음 유튜브 데이터 분석 및 해법을 한국어로 작성하세요: {v_summary}")
                        if res_yt:
                            st.session_state.saved_yt_result = res_yt

        if st.session_state.saved_yt_result:
            st.divider()
            st.warning(st.session_state.saved_yt_result)
            save_yt_title = st.text_input("저장할 제목 입력", value="유튜브 성과 진단 리포트", key="save_yt_title")
            col_ybtn1, col_ybtn2 = st.columns([1, 1])
            with col_ybtn1:
                if st.button("💾 유튜브 진단 보관함에 저장", use_container_width=True):
                    st.session_state.saved_items["yt_diag"].append({
                        "title": save_yt_title.strip() if save_yt_title.strip() else "제목 없음",
                        "content": st.session_state.saved_yt_result
                    })
                    st.success("✅ '유튜브 진단 보관함'에 저장되었습니다!")
                    st.rerun()
            with col_ybtn2:
                st.download_button("📥 텍스트 다운로드", data=st.session_state.saved_yt_result, file_name="YouTube_Diagnosis.txt", use_container_width=True)

    # 📸🎥 이미지 & 동영상 멀티모달 시각 분석 통합 탭
    with tab_img:
        st.markdown("#### 📸🎥 이미지 및 제작 동영상 파일 AI 정밀 분석")
        
        media_type = st.radio("분석할 미디어 유형 선택", ["🖼️ 제품/광고 이미지", "🎬 직접 제작한 동영상 (MP4 / MOV)"], horizontal=True)
        
        col_m1, col_m2 = st.columns([1, 1])
        uploaded_media = None
        
        with col_m1:
            if "이미지" in media_type:
                uploaded_media = st.file_uploader("이미지 파일 업로드", type=["png", "jpg", "jpeg"], key="up_img_file")
                if uploaded_media:
                    st.image(Image.open(uploaded_media), caption="업로드 이미지 미리보기", width=300)
            else:
                uploaded_media = st.file_uploader("동영상 파일 업로드 (최대 100MB 권장)", type=["mp4", "mov", "avi"], key="up_vid_file")
                if uploaded_media:
                    st.video(uploaded_media)

        with col_m2:
            media_concept = st.text_area("강조할 제품 소구점 또는 의도한 연출 콘셉트 (선택사항)", placeholder="예: 첫 3초 몰입도 검토, 20대 여성 타겟 숏폼 릴스 연출", height=120)
            btn_gen_media = st.button("🚀 미디어 시각 분석 및 평가 실행", type="primary", use_container_width=True)

        if btn_gen_media:
            gemini_client = get_gemini_client()
            if gemini_client and uploaded_media:
                with st.spinner("AI가 미디어 프레임을 정밀 분석 중입니다..."):
                    if "이미지" in media_type:
                        input_img = Image.open(uploaded_media)
                        prompt = f"""
                        당신은 수석 영상/광고 마케팅 디렉터입니다. 전달된 이미지를 정밀 분석하여 한국어로 답하세요.
                        [연출 의도]: {media_concept if media_concept else '기본 연출 최적화'}

                        1. 🎨 시각적 특징 및 구도 요약
                        2. 📌 클릭률(CTR)을 높일 추천 썸네일 기획 (3가지)
                        3. 🖼️ AI 이미지 생성용 완성형 영문/한글 프롬프트
                        4. 💡 숏폼(릴스/쇼츠) 활용 마케팅 팁
                        """
                        res_media = safe_gemini_generate(gemini_client, [prompt, input_img])
                    else:
                        # 동영상 업로드 처리
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                            tmp_file.write(uploaded_media.read())
                            tmp_path = tmp_file.name

                        try:
                            video_file = gemini_client.files.upload(file=tmp_path)
                            # 동영상 처리 대기
                            while video_file.state.name == "PROCESSING":
                                time.sleep(2)
                                video_file = gemini_client.files.get(name=video_file.name)

                            vid_prompt = f"""
                            당신은 전문 영상 마케팅 디렉터입니다. 제작된 동영상의 시각적 구성, 스토리 흐름, 자막/오디오 밸런스를 분석해 주세요.
                            반드시 한국어로 자연스럽게 작성해 주세요.
                            [제작자 의도]: {media_concept if media_concept else '전반적인 완성도 피드백'}

                            1. 🎬 동영상 핵심 연출 & 스토리 흐름 분석
                            2. ⚡ 첫 3초(Hook) 시청자 이탈 방지 몰입도 평가
                            3. 👁️ 화면 자막 가독성, 색감 및 시각적 개선점 (3가지)
                            4. 📌 이 영상에 어울리는 추천 썸네일 문구 및 구도 제안
                            """
                            res_media = safe_gemini_generate(gemini_client, [vid_prompt, video_file])
                        except Exception as ex:
                            st.error(f"동영상 파일 분석 중 오류 발생: {ex}")
                            res_media = None

                    if res_media:
                        st.session_state.saved_img_result = res_media

        if st.session_state.saved_img_result:
            st.divider()
            st.markdown(st.session_state.saved_img_result)
            save_img_title = st.text_input("저장할 제목 입력", value="미디어 시각 분석 리포트", key="save_img_title")
            col_ibtn1, col_ibtn2 = st.columns([1, 1])
            with col_ibtn1:
                if st.button("💾 시각적 미디어 보관함에 저장", use_container_width=True):
                    st.session_state.saved_items["img_analysis"].append({
                        "title": save_img_title.strip() if save_img_title.strip() else "제목 없음",
                        "content": st.session_state.saved_img_result
                    })
                    st.success("✅ '시각적 미디어 보관함'에 저장되었습니다!")
                    st.rerun()
            with col_ibtn2:
                st.download_button("📥 텍스트 다운로드", data=st.session_state.saved_img_result, file_name="Media_Analysis.txt", use_container_width=True)

    with tab_inf:
        st.markdown("#### 👥 타겟 키워드 기반 인플루언서 매칭")
        col_inf1, col_inf2 = st.columns([2, 1])
        with col_inf1:
            inf_keyword = st.text_input("타겟 키워드", placeholder="예: 친환경")
        with col_inf2:
            inf_platform = st.selectbox("플랫폼", ["유튜브", "인스타그램", "틱톡", "블로그"])
        
        if st.button("👥 인플루언서 매칭 실행", use_container_width=True):
            gemini_client = get_gemini_client()
            if gemini_client and inf_keyword:
                res_inf = safe_gemini_generate(gemini_client, f"인플루언서 매칭 가이드(한국어로 작성): {inf_keyword} ({inf_platform})")
                if res_inf:
                    st.session_state.saved_inf_result = res_inf

        if st.session_state.saved_inf_result:
            st.divider()
            st.markdown(st.session_state.saved_inf_result)
            save_inf_title = st.text_input("저장할 제목 입력", value=f"{inf_keyword} 인플루언서 매칭", key="save_inf_title")
            col_infbtn1, col_infbtn2 = st.columns([1, 1])
            with col_infbtn1:
                if st.button("💾 인플루언서 매칭 보관함에 저장", use_container_width=True):
                    st.session_state.saved_items["influencer"].append({
                        "title": save_inf_title.strip() if save_inf_title.strip() else "제목 없음",
                        "content": st.session_state.saved_inf_result
                    })
                    st.success("✅ '인플루언서 매칭 보관함'에 저장되었습니다!")
                    st.rerun()
            with col_infbtn2:
                st.download_button("📥 텍스트 다운로드", data=st.session_state.saved_inf_result, file_name="Influencer_Matching.txt", use_container_width=True)

    with tab_cal:
        st.markdown("#### 📅 30일 콘텐츠 마케팅 달력 생성")
        plan_cal_topic = st.text_input("달력 제작할 브랜드/제품 및 목표", placeholder="예: 신제품 텀블러 와디즈 펀딩 30일 캠페인", key="cal_input_topic")
        if st.button("📅 30일 콘텐츠 달력 생성 실행", type="primary", use_container_width=True):
            gemini_client = get_gemini_client()
            if gemini_client and plan_cal_topic:
                with st.spinner("30일 콘텐츠 전략 및 달력 생성 중..."):
                    res_cal = safe_gemini_generate(gemini_client, f"다음 브랜드/목표에 대한 1일차부터 30일차까지의 상세 콘텐츠 마케팅 달력(주차별 목표, 일별 콘텐츠 주제 및 게시 포맷 포함, 한국어 필수)을 작성하세요: {plan_cal_topic}")
                    if res_cal:
                        st.session_state.saved_cal_result = res_cal

        if st.session_state.saved_cal_result:
            st.divider()
            st.markdown(st.session_state.saved_cal_result)
            save_cal_title = st.text_input("저장할 제목 입력", value=f"{plan_cal_topic} 30일 달력", key="save_cal_title")
            col_cbtn1, col_cbtn2 = st.columns([1, 1])
            with col_cbtn1:
                if st.button("💾 30일 달력 보관함에 저장", use_container_width=True):
                    st.session_state.saved_items["calendar"].append({
                        "title": save_cal_title.strip() if save_cal_title.strip() else "제목 없음",
                        "content": st.session_state.saved_cal_result
                    })
                    st.success("✅ '30일 달력 보관함'에 저장되었습니다!")
                    st.rerun()
            with col_cbtn2:
                st.download_button("📥 텍스트 다운로드", data=st.session_state.saved_cal_result, file_name="Content_Calendar.txt", use_container_width=True)

    with tab_copy:
        st.markdown("#### ✍️ 마케팅 카피라이팅 문구 추출")
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            copy_topic = st.text_input("카피라이팅 대상 제품/브랜드명", placeholder="예: 민트볼 틴케이스", key="copy_input_topic")
        with col_c2:
            copy_channel = st.selectbox("게시 채널", ["인스타그램 릴스/포스터", "유튜브 쇼츠/제목", "광고 헤드라인", "상세페이지 메인문구"], key="copy_input_channel")
        copy_detail = st.text_area("강조하고 싶은 소구점/혜택", placeholder="예: 한 손에 쏙 들어오는 휴대성, 강력한 상쾌함", height=100, key="copy_input_detail")
        
        if st.button("✍️ 마케팅 카피라이팅 문구 추출 실행", type="primary", use_container_width=True):
            gemini_client = get_gemini_client()
            if gemini_client and copy_topic:
                with st.spinner("카피라이팅 문구 추출 중..."):
                    copy_prompt = f"제품/브랜드: {copy_topic}, 채널: {copy_channel}, 주요혜택: {copy_detail}\n위 정보를 바탕으로 마케팅 카피라이팅 문구 10개를 한국어로 작성하세요."
                    res_copy = safe_gemini_generate(gemini_client, copy_prompt)
                    if res_copy:
                        st.session_state.saved_copy_result = res_copy

        if st.session_state.saved_copy_result:
            st.divider()
            st.markdown(st.session_state.saved_copy_result)
            save_copy_title = st.text_input("저장할 제목 입력", value=f"{copy_topic} 카피라이팅", key="save_copy_title")
            col_cpbtn1, col_cpbtn2 = st.columns([1, 1])
            with col_cpbtn1:
                if st.button("💾 카피라이팅 보관함에 저장", use_container_width=True):
                    st.session_state.saved_items["copywriting"].append({
                        "title": save_copy_title.strip() if save_copy_title.strip() else "제목 없음",
                        "content": st.session_state.saved_copy_result
                    })
                    st.success("✅ '카피라이팅 보관함'에 저장되었습니다!")
                    st.rerun()
            with col_cpbtn2:
                st.download_button("📥 텍스트 다운로드", data=st.session_state.saved_copy_result, file_name="Copywriting.txt", use_container_width=True)
