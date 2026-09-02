import os
import streamlit as st
from google import genai
from google.genai import types
import anthropic
import yt_dlp
import pandas as pd
from PIL import Image

st.set_page_config(page_title="AI 영상 제작 & 마케팅 스튜디오 Pro", layout="wide")

# Secrets에서 Gemini API 키 백그라운드 자동 로드
saved_gemini_key = st.secrets.get("GEMINI_API_KEY", "")

# 💾 전 카테고리 저장소 초기화
if "saved_items" not in st.session_state:
    st.session_state.saved_items = {
        "prompts": [],     # 🎬 영상 프롬프트
        "plans": [],       # 📄 촬영 기획서
        "yt_diag": [],     # 🎥 유튜브 성과 진단
        "img_analysis": [],# 📸 이미지 시각 분석
        "influencer": [],  # 👥 인플루언서 매칭
        "calendar": [],    # 📅 30일 콘텐츠 달력
        "copywriting": []  # ✍️ 카피라이팅 문구
    }

# 생성 결과 세션 보관
if "saved_prompt_result" not in st.session_state: st.session_state.saved_prompt_result = None
if "saved_plan_result" not in st.session_state: st.session_state.saved_plan_result = None
if "saved_yt_result" not in st.session_state: st.session_state.saved_yt_result = None
if "saved_img_result" not in st.session_state: st.session_state.saved_img_result = None
if "saved_inf_result" not in st.session_state: st.session_state.saved_inf_result = None
if "saved_cal_result" not in st.session_state: st.session_state.saved_cal_result = None
if "saved_copy_result" not in st.session_state: st.session_state.saved_copy_result = None

st.title("⚡ AI 영상 제작 & 올인원 마케팅 스튜디오 Pro")
st.caption("결과물 확인 후 원하는 제목을 지정하여 카테고리별 저장소에 보관할 수 있습니다.")
st.divider()

# 사이드바 API 설정 & 카테고리별 보관함
with st.sidebar:
    st.header("🔑 API 설정")
    st.success("✅ Google Gemini API 연결 완료")
    
    claude_key = st.text_input("Anthropic Claude API Key (선택)", type="password")
    
    st.divider()
    st.header("📂 카테고리별 보관함")
    
    # 1. 프롬프트 보관함
    with st.expander("🎬 영상 프롬프트 보관함", expanded=False):
        if st.session_state.saved_items["prompts"]:
            for idx, item in enumerate(st.session_state.saved_items["prompts"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_p_{idx}")
                st.markdown("---")
        else: st.caption("저장된 프롬프트가 없습니다.")

    # 2. 기획서 보관함
    with st.expander("📄 촬영 기획서 보관함", expanded=False):
        if st.session_state.saved_items["plans"]:
            for idx, item in enumerate(st.session_state.saved_items["plans"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.md", key=f"dl_pl_{idx}")
                st.markdown("---")
        else: st.caption("저장된 기획서가 없습니다.")

    # 3. 유튜브 성과 진단 보관함
    with st.expander("🎥 유튜브 진단 보관함", expanded=False):
        if st.session_state.saved_items["yt_diag"]:
            for idx, item in enumerate(st.session_state.saved_items["yt_diag"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_yt_{idx}")
                st.markdown("---")
        else: st.caption("저장된 진단 리포트가 없습니다.")

    # 4. 이미지 분석 보관함
    with st.expander("📸 이미지 분석 보관함", expanded=False):
        if st.session_state.saved_items["img_analysis"]:
            for idx, item in enumerate(st.session_state.saved_items["img_analysis"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_img_{idx}")
                st.markdown("---")
        else: st.caption("저장된 분석 결과가 없습니다.")

    # 5. 인플루언서 매칭 보관함
    with st.expander("👥 인플루언서 매칭 보관함", expanded=False):
        if st.session_state.saved_items["influencer"]:
            for idx, item in enumerate(st.session_state.saved_items["influencer"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_inf_{idx}")
                st.markdown("---")
        else: st.caption("저장된 매칭 가이드가 없습니다.")

    # 6. 콘텐츠 달력 보관함
    with st.expander("📅 30일 달력 보관함", expanded=False):
        if st.session_state.saved_items["calendar"]:
            for idx, item in enumerate(st.session_state.saved_items["calendar"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_cal_{idx}")
                st.markdown("---")
        else: st.caption("저장된 달력이 없습니다.")

    # 7. 카피라이팅 보관함
    with st.expander("✍️ 카피라이팅 보관함", expanded=False):
        if st.session_state.saved_items["copywriting"]:
            for idx, item in enumerate(st.session_state.saved_items["copywriting"], 1):
                st.markdown(f"**📌 {item['title']}**")
                st.code(item['content'], language="markdown")
                st.download_button("💾 다운로드", item['content'], file_name=f"{item['title']}.txt", key=f"dl_copy_{idx}")
                st.markdown("---")
        else: st.caption("저장된 카피가 없습니다.")

def get_gemini_client():
    if not saved_gemini_key:
        st.error("⚠️ Streamlit Secrets에 GEMINI_API_KEY가 설정되어 있지 않습니다.")
        return None
    try:
        return genai.Client(api_key=saved_gemini_key.strip())
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
                prompt_req = f"주제: {p_topic}, 포맷: {p_style}, 톤: {p_tone}, 내용: {p_detail} 바탕으로 전문 프롬프트를 작성하세요."
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
                plan_req = f"프로젝트명: {g_title}, 타겟: {g_target}, 장소: {g_location}, 내용: {g_goal} 바탕으로 촬영계획서를 작성하세요."
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
        with col_pbtn2:
            st.download_button("📥 마크다운 다운로드", data=st.session_state.saved_plan_result, file_name="Plan.md", use_container_width=True)

# ==========================================
# 🛠️ TAB 3: 확장 마케팅 스튜디오
# ==========================================
with main_tab3:
    st.markdown("### 🛠️ 확장 마케팅 스튜디오")
    tab_yt_std, tab_img, tab_inf, tab_cal, tab_copy = st.tabs([
        "🎥 내 유튜브 영상 성과 진단", 
        "📸 제품 사진 기반 AI 이미지 분석", 
        "👥 키워드 기반 인플루언서 탐색", 
        "📅 30일 콘텐츠 달력 생성기",
        "✍️ 마케팅 카피라이팅 추출기"
    ])

    # 1. 유튜브 성과 진단
    with tab_yt_std:
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
                        res_yt = safe_gemini_generate(gemini_client, f"다음 유튜브 데이터 분석 및 해법을 작성하세요: {v_summary}")
                        if res_yt:
                            st.session_state.saved_yt_result = res_yt

        if st.session_state.saved_yt_result:
            st.divider()
            st.warning(st.session_state.saved_yt_result)
            save_yt_title = st.text_input("저장할 제목 입력", value="유튜브 성과 진단 리포트", key="save_yt_title")
            if st.button("💾 유튜브 진단 보관함에 저장", use_container_width=True):
                st.session_state.saved_items["yt_diag"].append({
                    "title": save_yt_title.strip() if save_yt_title.strip() else "제목 없음",
                    "content": st.session_state.saved_yt_result
                })
                st.success("✅ '유튜브 진단 보관함'에 저장되었습니다!")

    # 2. 이미지 분석
    with tab_img:
        col_img1, col_img2 = st.columns([1, 1])
        with col_img1:
            uploaded_file = st.file_uploader("제품 사진 업로드", type=["png", "jpg", "jpeg"])
            if uploaded_file:
                input_image = Image.open(uploaded_file)
                st.image(input_image, caption="업로드 원본", width=250)
        with col_img2:
            img_style_prompt = st.text_area("연출 분위기 작성", height=100)
            btn_gen_img = st.button("🖼️ 연출 이미지 특징 분석", use_container_width=True)

        if btn_gen_img:
            gemini_client = get_gemini_client()
            if gemini_client and uploaded_file:
                with st.spinner("이미지 특성 분석 중..."):
                    res_img = safe_gemini_generate(gemini_client, ["Describe key visual characteristics of this product image.", input_image])
                    if res_img:
                        st.session_state.saved_img_result = res_img

        if st.session_state.saved_img_result:
            st.divider()
            st.info(st.session_state.saved_img_result)
            save_img_title = st.text_input("저장할 제목 입력", value="제품 이미지 시각 분석", key="save_img_title")
            if st.button("💾 이미지 분석 보관함에 저장", use_container_width=True):
                st.session_state.saved_items["img_analysis"].append({
                    "title": save_img_title.strip() if save_img_title.strip() else "제목 없음",
                    "content": st.session_state.saved_img_result
                })
                st.success("✅ '이미지 분석 보관함'에 저장되었습니다!")

    # 3. 인플루언서 탐색
    with tab_inf:
        col_inf1, col_inf2 = st.columns([2, 1])
        with col_inf1:
            inf_keyword = st.text_input("타겟 키워드", placeholder="예: 친환경")
        with col_inf2:
            inf_platform = st.selectbox("플랫폼", ["유튜브", "인스타그램", "틱톡", "블로그"])
        
        if st.button("👥 인플루언서 매칭 실행", use_container_width=True):
            gemini_client = get_gemini_client()
            if gemini_client and inf_keyword:
                res_inf = safe_gemini_generate(gemini_client, f"인플루언서 매칭 가이드: {inf_keyword} ({inf_platform})")
                if res_inf:
                    st.session_state.saved_inf_result = res_inf

        if st.session_state.saved_inf_result:
            st.divider()
            st.markdown(st.session_state.saved_inf_result)
            save_inf_title = st.text_input("저장할 제목 입력", value=f"{inf_keyword} 인플루언서 매칭", key="save_inf_title")
            if st.button("💾 인플루언서 매칭 보관함에 저장", use_container_width=True):
                st.session_state.saved_items["influencer"].append({
                    "title": save_inf_title.strip() if save_inf_title.strip() else "제목 없음",
                    "content": st.session_state.saved_inf_result
                })
                st.success("✅ '인플루언서 매칭 보관함'에 저장되었습니다!")

    # 4. 독립된 30일 콘텐츠 달력 생성기
    with tab_cal:
        st.markdown("#### 📅 30일 콘텐츠 마케팅 달력 생성")
        plan_cal_topic = st.text_input("달력 제작할 브랜드/제품 및 목표", placeholder="예: 신제품 텀블러 와디즈 펀딩 30일 캠페인", key="cal_input_topic")
        
        if st.button("📅 30일 콘텐츠 달력 생성 실행", type="primary", use_container_width=True):
            gemini_client = get_gemini_client()
            if gemini_client and plan_cal_topic:
                with st.spinner("30일 콘텐츠 전략 및 달력 생성 중..."):
                    res_cal = safe_gemini_generate(gemini_client, f"다음 브랜드/목표에 대한 1일차부터 30일차까지의 상세 콘텐츠 마케팅 달력(주차별 목표, 일별 콘텐츠 주제 및 게시 포맷 포함)을 작성하세요: {plan_cal_topic}")
                    if res_cal:
                        st.session_state.saved_cal_result = res_cal

        if st.session_state.saved_cal_result:
            st.divider()
            st.markdown(st.session_state.saved_cal_result)
            save_cal_title = st.text_input("저장할 제목 입력", value=f"{plan_cal_topic} 30일 달력", key="save_cal_title")
            if st.button("💾 30일 달력 보관함에 저장", use_container_width=True):
                st.session_state.saved_items["calendar"].append({
                    "title": save_cal_title.strip() if save_cal_title.strip() else "제목 없음",
                    "content": st.session_state.saved_cal_result
                })
                st.success("✅ '30일 달력 보관함'에 저장되었습니다!")

    # 5. 독립된 마케팅 카피라이팅 추출기
    with tab_copy:
        st.markdown("#### ✍️ 마케팅 카피라이팅 문구 추출")
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            copy_topic = st.text_input("카피라이팅 대상 제품/브랜드명", placeholder="예: 민트볼 틴케이스", key="copy_input_topic")
        with col_c2:
            copy_channel = st.selectbox("게시 채널", ["인스타그램 릴스/포스터", "유튜브 숏폼/제목", "광고 헤드라인", "상세페이지 메인문구"], key="copy_input_channel")
        
        copy_detail = st.text_area("강조하고 싶은 소구점/혜택", placeholder="예: 한 손에 쏙 들어오는 휴대성, 입안 가득 퍼지는 강력한 상쾌함", height=100, key="copy_input_detail")
        
        if st.button("✍️ 마케팅 카피라이팅 문구 추출 실행", type="primary", use_container_width=True):
            gemini_client = get_gemini_client()
            if gemini_client and copy_topic:
                with st.spinner("카피라이팅 문구 추출 중..."):
                    copy_prompt = f"제품/브랜드: {copy_topic}, 채널: {copy_channel}, 주요혜택: {copy_detail}\n위 정보를 바탕으로 시선을 사로잡는 마케팅 카피라이팅 문구 10개를 톤앤매너별로 추출하세요."
                    res_copy = safe_gemini_generate(gemini_client, copy_prompt)
                    if res_copy:
                        st.session_state.saved_copy_result = res_copy

        if st.session_state.saved_copy_result:
            st.divider()
            st.markdown(st.session_state.saved_copy_result)
            save_copy_title = st.text_input("저장할 제목 입력", value=f"{copy_topic} 카피라이팅", key="save_copy_title")
            if st.button("💾 카피라이팅 보관함에 저장", use_container_width=True):
                st.session_state.saved_items["copywriting"].append({
                    "title": save_copy_title.strip() if save_copy_title.strip() else "제목 없음",
                    "content": st.session_state.saved_copy_result
                })
                st.success("✅ '카피라이팅 보관함'에 저장되었습니다!")
