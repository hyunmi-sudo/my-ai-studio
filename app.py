import streamlit as st
from google import genai
from google.genai import types
import anthropic
import yt_dlp
import pandas as pd
from PIL import Image

# Streamlit 페이지 설정
st.set_page_config(page_title="AI 영상 제작 & 마케팅 스튜디오 Pro", layout="wide")

# 세션 상태(이전 기록 보관함) 초기화
if "master_prompts" not in st.session_state:
    st.session_state.master_prompts = []
if "saved_prompt_result" not in st.session_state:
    st.session_state.saved_prompt_result = None
if "saved_plan_result" not in st.session_state:
    st.session_state.saved_plan_result = None

st.title("⚡ AI 영상 제작 & 올인원 마케팅 스튜디오 Pro")
st.caption("영상 제작용 AI 프롬프트 생성과 상세 영상 촬영계획서 작성을 독립된 구획에서 따로 진행할 수 있습니다.")
st.divider()

# 사이드바 API 설정 & 마스터 프롬프트 보관함
with st.sidebar:
    st.header("🔑 API 설정")
    gemini_key = st.text_input("1️⃣ Google Gemini API Key", type="password")
    st.caption("[Google AI Studio](https://aistudio.google.com/) 무료 발급")
    st.divider()
    claude_key = st.text_input("2️⃣ Anthropic Claude API Key (선택)", type="password")
    
    st.divider()
    st.header("📂 마스터 프롬프트 보관함")
    if st.session_state.master_prompts:
        for idx, item in enumerate(st.session_state.master_prompts, start=1):
            with st.expander(f"📌 [{item['title']}] 템플릿"):
                st.code(item['prompt'], language="markdown")
                st.download_button("💾 텍스트 다운로드", item['prompt'], file_name=f"Prompt_{idx}.txt", key=f"dl_{idx}")
    else:
        st.info("저장된 프롬프트가 없습니다.")

def get_gemini_client():
    if not gemini_key or not gemini_key.strip():
        st.warning("왼쪽 사이드바에 Google Gemini API Key를 입력해 주세요.")
        return None
    try:
        return genai.Client(api_key=gemini_key.strip())
    except Exception as e:
        st.error(f"Gemini 클라이언트 초기화 실패: {e}")
        return None

def safe_gemini_generate(client, contents_input):
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=contents_input
        )
        if response and response.text:
            return response.text
    except Exception as e:
        err_msg = str(e)
        if "INVALID_ARGUMENT" in err_msg or "API_KEY_INVALID" in err_msg:
            st.error("❌ 입력하신 Gemini API Key가 유효하지 않습니다. 키를 다시 확인해 주세요.")
        else:
            st.error(f"⚠️ API 생성 오류: {err_msg}")
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

def get_youtube_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
    }
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

# 메인 작업 탭 분리
main_tab1, main_tab2, main_tab3 = st.tabs([
    "🎬 1. 영상 제작 전용 AI 프롬프트 생성기", 
    "📄 2. 영상 종합 기획서 & 촬영계획서 작성기",
    "🛠️ 3. 확장 마케팅 스튜디오 (성과진단 / 이미지 / 인플루언서 / 달력)"
])

# ==========================================
# 🎬 TAB 1: 영상 제작 전용 프롬프트 생성기
# ==========================================
with main_tab1:
    st.markdown("### 🎬 영상 제작용 AI 프롬프트 독립 생성")
    st.caption("AI 대본 작성기나 영상 생성 AI(Sora, Runway 등)에 입력할 최적의 프롬프트를 만듭니다.")
    
    col_p1, col_p2 = st.columns([1, 1])
    with col_p1:
        p_topic = st.text_input("영상 주제 / 제품명", placeholder="예: 민트볼 틴케이스 숏폼 홍보 영상", key="p_topic")
        p_style = st.selectbox("영상 포맷", ["유튜브 숏폼/릴스/틱톡 (15~60초)", "유튜브 롱폼 (5~10분)", "브랜드 홍보 CF", "제품 언박싱/리뷰"], key="p_style")
    with col_p2:
        p_tone = st.text_input("원하는 톤앤매너 & 감성", placeholder="예: 트렌디함, B급 유머, 감성적인, 미니멀한", key="p_tone")
        p_detail = st.text_area("프롬프트에 꼭 포함할 핵심 메시지", placeholder="예: 휴대성이 좋다는 점과 민트의 상쾌함을 강조해줘", height=100, key="p_detail")

    btn_gen_prompt = st.button("🚀 영상 제작용 프롬프트 생성 실행", type="primary", use_container_width=True)

    if btn_gen_prompt:
        gemini_client = get_gemini_client()
        if not p_topic or not p_detail:
            st.error("주제와 핵심 메시지를 입력해 주세요.")
        elif gemini_client:
            with st.spinner("영상 제작용 맞춤 & 마스터 프롬프트 생성 중..."):
                prompt_req = f"""
                당신은 수석 영상 프롬프트 엔지니어입니다. 아래 조건을 바탕으로 영상 제작에 쓸 2가지 프롬프트를 작성하세요.

                [입력 조건]
                - 주제/제품: {p_topic}
                - 포맷: {p_style}
                - 톤앤매너: {p_tone}
                - 핵심 메시지: {p_detail}

                [출력 양식]:
                1. 🎬 **영상 생성 & 대본 작성용 [맞춤 실행 프롬프트]**
                   - 역할 부여(Role)
                   - 상세 지시사항(Task)
                   - 톤앤매너 및 연출 가이드라인
                   - 완성된 대본/콘티 요청 마스터 명령문

                2. 👑 **다른 영상 제작 시 재사용 가능한 [마스터 프롬프트 템플릿]**
                   - [제품명], [포맷], [톤앤매너] 슬롯만 바꾸면 바로 재사용 가능한 범용 프레임워크
                """
                res_prompt = generate_claude_or_gemini(prompt_req, gemini_client)
                if res_prompt:
                    st.session_state.saved_prompt_result = res_prompt
                    st.session_state.master_prompts.append({"title": f"{p_topic[:12]} 프롬프트", "prompt": res_prompt})

    if st.session_state.saved_prompt_result:
        st.divider()
        st.markdown("#### 📌 생성된 영상 제작용 프롬프트 결과")
        st.info(st.session_state.saved_prompt_result)
        st.download_button("💾 프롬프트 텍스트 파일 다운로드", data=st.session_state.saved_prompt_result, file_name="Video_Prompt.txt")

# ==========================================
# 📄 TAB 2: 영상 기획서 & 촬영계획서 작성기
# ==========================================
with main_tab2:
    st.markdown("### 📄 영상 종합 기획서 & 촬영계획서 작성")
    st.caption("실제 현장 촬영 및 현장 감독용 상세 촬영계획서와 타임라인 콘티를 생성합니다.")

    col_g1, col_g2 = st.columns([1, 1])
    with col_g1:
        g_title = st.text_input("기획 프로젝트명", placeholder="예: 민트볼 틴케이스 와디즈 펀딩 영상", key="g_title")
        g_target = st.text_input("타겟 시청자층", placeholder="예: 2030 직장인 및 자취생", key="g_target")
    with col_g2:
        g_location = st.text_input("촬영 장소 / 로케이션 구상", placeholder="예: 채광 좋은 미니멀 카페, 야외 공원, 자취방", key="g_location")
        g_goal = st.text_area("영상 제작 목적 및 세부 내용", placeholder="예: 제품 펀딩 전환율 상승, 브랜드 인지도 확보", height=100, key="g_goal")

    btn_gen_plan = st.button("📄 영상 기획서 & 촬영계획서 생성 실행", type="primary", use_container_width=True)

    if btn_gen_plan:
        gemini_client = get_gemini_client()
        if not g_title or not g_goal:
            st.error("프로젝트명과 세부 내용을 입력해 주세요.")
        elif gemini_client:
            with st.spinner("영상 기획서 및 씬별 촬영계획서 작성 중..."):
                plan_req = f"""
                당신은 전문 영상 감독 및 마케팅 디렉터입니다. 아래 내용을 바탕으로 전문적인 영상 종합 기획서 및 촬영계획서를 작성하세요.

                [기획 정보]
                - 프로젝트명: {g_title}
                - 타겟: {g_target}
                - 촬영 로케이션: {g_location}
                - 제작 목적/내용: {g_goal}

                [출력 목차]:
                1. 🎯 **영상 핵심 기획안**
                   - 기획 의도 및 핵심 메시지 (Hook point)
                   - 톤앤매너 & 비주얼 컨셉

                2. 🎬 **씬(Scene)별 상세 촬영계획서 (타임라인 콘티)**
                   - 표 포맷 (Scene 번호 | 연출 내용/화면 구도 | 오디오/대사 | 촬영 구도 및 카메라 워크 | 비고)

                3. 🛠️ **촬영 현장 체크리스트**
                   - 준비물 / 소품 리스트
                   - 추천 장비 (조명, 프레임, 렌즈 감성)
                   - 편집 및 BGM/사운드 연출 방향
                """
                res_plan = safe_gemini_generate(gemini_client, plan_req)
                if res_plan:
                    st.session_state.saved_plan_result = res_plan

    if st.session_state.saved_plan_result:
        st.divider()
        st.markdown("#### 📄 생성된 영상 종합 기획서 & 촬영계획서")
        st.success(st.session_state.saved_plan_result)
        st.download_button("📥 촬영계획서 마크다운(.md) 다운로드", data=st.session_state.saved_plan_result, file_name="Shooting_Plan.md", use_container_width=True)

# ==========================================
# 🛠️ TAB 3: 확장 마케팅 스튜디오
# ==========================================
with main_tab3:
    st.markdown("### 🛠️ 확장 마케팅 스튜디오")
    tab_yt_standalone, tab_img, tab_inf, tab_plan = st.tabs([
        "🎥 내 유튜브 영상 성과 진단 (단독)", "📸 제품 사진 기반 AI 이미지 분석", "👥 키워드 기반 인플루언서 탐색", "📅 30일 콘텐츠 달력"
    ])

    with tab_yt_standalone:
        st.write("유튜브 영상 URL을 입력하시면 지표 수집 및 AI 진단 리포트를 생성해 드립니다.")
        standalone_urls = st.text_area("유튜브 URL 목록 (한 줄에 하나씩)", height=100)
        if st.button("📊 영상 성과 진단 실행", use_container_width=True):
            gemini_client = get_gemini_client()
            if gemini_client and standalone_urls.strip():
                url_list_std = [u.strip() for u in standalone_urls.strip().split('\n') if u.strip()]
                with st.spinner(f"총 {len(url_list_std)}개 영상 데이터 분석 중..."):
                    fetched_std = []
                    for idx, url in enumerate(url_list_std, start=1):
                        try:
                            info = get_youtube_info(url)
                            info['id'] = f"영상 {idx}"
                            fetched_std.append(info)
                        except Exception as e:
                            st.warning(f"URL 수집 불가 ({url}): {e}")
                    
                    if fetched_std:
                        card_cols_std = st.columns(len(fetched_std))
                        for i, data in enumerate(fetched_std):
                            with card_cols_std[i]:
                                st.metric(label=f"[{data['id']}] {data['title'][:12]}...", value=f"{data['views']:,} 회", delta=f"👍 {data['likes']:,} | 💬 {data['comments']:,}")
                        st.dataframe(pd.DataFrame(fetched_std)[['id', 'title', 'views', 'likes', 'comments', 'channel']], use_container_width=True)
                        v_summary = "".join([f"\n- [{d['id']}] 제목:{d['title']} / 조회수:{d['views']} / 좋아요:{d['likes']} / 댓글:{d['comments']}" for d in fetched_std])
                        res_std_text = safe_gemini_generate(gemini_client, f"유튜브 데이터 분석가로서 다음 데이터 분석 및 해법을 제시하세요: {v_summary}")
                        if res_std_text:
                            st.warning(res_std_text)

    with tab_img:
        col_img1, col_img2 = st.columns([1, 1])
        with col_img1:
            uploaded_file = st.file_uploader("1. 제품 사진 업로드", type=["png", "jpg", "jpeg"])
            if uploaded_file:
                input_image = Image.open(uploaded_file)
                st.image(input_image, caption="업로드한 제품 원본", width=250)
        with col_img2:
            img_style_prompt = st.text_area("2. 연출 분위기 작성", height=100)
            btn_gen_img = st.button("🖼️ 연출 이미지 특징 분석", use_container_width=True)

        if btn_gen_img:
            gemini_client = get_gemini_client()
            if gemini_client and uploaded_file:
                with st.spinner("이미지 시각적 특성 분석 중..."):
                    product_features = safe_gemini_generate(gemini_client, ["Describe key visual characteristics of this product image in detail.", input_image])
                    if product_features:
                        st.info(f"**제품 시각적 특징 분석 완료:**\n{product_features}")

    with tab_inf:
        col_inf1, col_inf2, col_inf3 = st.columns([2, 1, 1])
        with col_inf1:
            inf_keyword = st.text_input("타겟 키워드", placeholder="예: 친환경")
        with col_inf2:
            inf_platform = st.selectbox("플랫폼", ["유튜브 (YouTube)", "인스타그램 (Instagram)", "틱톡 (TikTok)", "블로그"])
        with col_inf3:
            st.write("")
            btn_gen_inf = st.button("👥 인플루언서 매칭", use_container_width=True)

        if btn_gen_inf:
            gemini_client = get_gemini_client()
            if gemini_client and inf_keyword:
                res = safe_gemini_generate(gemini_client, f"인플루언서 매칭 가이드: {inf_keyword} ({inf_platform})")
                if res: st.markdown(res)

    with tab_plan:
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            plan_cal_topic = st.text_input("실행 주제 및 목표", placeholder="예: 신제품 펀딩")
        with col_p2:
            st.write("")
            btn_gen_plan = st.button("📅 30일 달력 & 카피 추출", use_container_width=True)

        if btn_gen_plan:
            gemini_client = get_gemini_client()
            if gemini_client and plan_cal_topic:
                res = safe_gemini_generate(gemini_client, f"30일 콘텐츠 달력 및 카피 작성: {plan_cal_topic}")
                if res: st.markdown(res)
