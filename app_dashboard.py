import os
import io
import time
import streamlit as st
from google import genai
import anthropic
import yt_dlp
import pandas as pd
from PIL import Image

st.set_page_config(page_title="AI 영상 제작 & 마케팅 스튜디오 Pro", layout="wide", page_icon="⚡")

# 백업용 서버 공유 API 키 (서브 연결)
server_backup_key = st.secrets.get("GEMINI_API_KEY", "")

# 💾 카테고리 저장소 및 세션 초기화
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

# 📊 마케팅 성과 원본 데이터 세션 초기화
if "analytics_data" not in st.session_state:
    st.session_state.analytics_data = pd.DataFrame([
        {"날짜": "2026-08-25", "플랫폼": "인스타그램 릴스", "콘텐츠 제목": "민트볼 챌린지 1탄", "사용 음원": "Minty Fresh Beat", "조회수": 45000, "좋아요": 3200, "댓글": 180, "공유수": 420},
        {"날짜": "2026-08-26", "플랫폼": "유튜브 쇼츠", "콘텐츠 제목": "한 손에 쏙 들어오는 민트볼", "사용 음원": "Minty Fresh Beat", "조회수": 82000, "좋아요": 6100, "댓글": 340, "공유수": 890},
        {"날짜": "2026-08-27", "플랫폼": "틱톡", "콘텐츠 제목": "상쾌함 폭발 리액션", "사용 음원": "Minty Fresh Beat", "조회수": 120000, "좋아요": 11500, "댓글": 620, "공유수": 1450},
        {"날짜": "2026-08-28", "플랫폼": "인스타그램 릴스", "콘텐츠 제목": "출근길 필수 아이템 리얼 후기", "사용 음원": "Cool Summer Sound", "조회수": 28000, "좋아요": 1900, "댓글": 95, "공유수": 130},
        {"날짜": "2026-08-29", "플랫폼": "유튜브 쇼츠", "콘텐츠 제목": "식사 후 3초 만에 깔끔하게", "사용 음원": "Cool Summer Sound", "조회수": 64000, "좋아요": 4800, "댓글": 210, "공유수": 510},
        {"날짜": "2026-08-30", "플랫폼": "틱톡", "콘텐츠 제목": "카페에서 몰래 먹는 민트볼", "사용 음원": "Minty Fresh Beat", "조회수": 95000, "좋아요": 8700, "댓글": 410, "공유수": 920},
    ])

st.title("⚡ AI 영상 제작 & 올인원 마케팅 스튜디오 Pro")
st.caption("개인 API 키 우선 연결 모드: 사용자 키를 최우선 적용하며, 미입력 시 시스템 백업 키로 자동 작동합니다.")
st.divider()

# 🔑 사이드바: 개인 API 우선 사용 & 보관함
with st.sidebar:
    st.header("🔑 메인 API 연결")
    user_gemini_key = st.text_input("개인 Gemini API Key (우선 적용)", type="password", placeholder="AIzaSy...")
    
    # 개인 API 키 존재 시 1순위 사용, 없을 시 시스템 백업 키를 2순위로 사용
    if user_gemini_key.strip():
        active_gemini_key = user_gemini_key.strip()
        st.success("👑 [메인] 개인 Gemini API 키 적용 중")
    elif server_backup_key.strip():
        active_gemini_key = server_backup_key.strip()
        st.info("🛡️ [서브] 시스템 백업 API 키 적용 중")
    else:
        active_gemini_key = ""
        st.warning("⚠️ 사용 가능한 API 키가 없습니다.")
        
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

    with st.expander("📸 이미지 분석 보관함", expanded=False):
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
        st.error("⚠️ API 키가 설정되지 않았습니다. 개인 Gemini API 키를 입력해 주세요.")
        return None
    try:
        return genai.Client(api_key=active_gemini_key)
    except Exception as e:
        st.error(f"Gemini 초기화 오류: {e}")
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
        st.error(f"⚠️ API 요청 실패: {e}")
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

main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
    "🎬 1. 영상 제작 전용 AI 프롬프트 생성기", 
    "📄 2. 영상 종합 기획서 & 촬영계획서 작성기",
    "🛠️ 3. 확장 마케팅 스튜디오",
    "📊 4. 마케팅 성과 & 음원 분석 대시보드"
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
            with st.spinner("개인 API로 프롬프트 생성 중..."):
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
                        res_yt = safe_gemini_generate(gemini_client, f"다음 유튜브 데이터 분석 및 해법을 작성하세요: {v_summary}")
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
            with col_ybtn2:
                st.download_button("📥 텍스트 다운로드", data=st.session_state.saved_yt_result, file_name="YouTube_Diagnosis.txt", use_container_width=True)

    with tab_img:
        st.markdown("#### 📸 제품 이미지 시각 특징 분석")
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
            col_ibtn1, col_ibtn2 = st.columns([1, 1])
            with col_ibtn1:
                if st.button("💾 이미지 분석 보관함에 저장", use_container_width=True):
                    st.session_state.saved_items["img_analysis"].append({
                        "title": save_img_title.strip() if save_img_title.strip() else "제목 없음",
                        "content": st.session_state.saved_img_result
                    })
                    st.success("✅ '이미지 분석 보관함'에 저장되었습니다!")
            with col_ibtn2:
                st.download_button("📥 텍스트 다운로드", data=st.session_state.saved_img_result, file_name="Image_Analysis.txt", use_container_width=True)

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
                res_inf = safe_gemini_generate(gemini_client, f"인플루언서 매칭 가이드: {inf_keyword} ({inf_platform})")
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
            with col_infbtn2:
                st.download_button("📥 텍스트 다운로드", data=st.session_state.saved_inf_result, file_name="Influencer_Matching.txt", use_container_width=True)

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
            col_cbtn1, col_cbtn2 = st.columns([1, 1])
            with col_cbtn1:
                if st.button("💾 30일 달력 보관함에 저장", use_container_width=True):
                    st.session_state.saved_items["calendar"].append({
                        "title": save_cal_title.strip() if save_cal_title.strip() else "제목 없음",
                        "content": st.session_state.saved_cal_result
                    })
                    st.success("✅ '30일 달력 보관함'에 저장되었습니다!")
            with col_cbtn2:
                st.download_button("📥 텍스트 다운로드", data=st.session_state.saved_cal_result, file_name="Content_Calendar.txt", use_container_width=True)

    with tab_copy:
        st.markdown("#### ✍️ 마케팅 카피라이팅 문구 추출")
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            copy_topic = st.text_input("카피라이팅 대상 제품/브랜드명", placeholder="예: 민트볼 틴케이스", key="copy_input_topic")
        with col_c2:
            copy_channel = st.selectbox("게시 채널", ["인스타그램 릴스/포스터", "유튜브 숏폼/제목", "광고 헤드라인", "상세페이지 메인문구"], key="copy_input_channel")
        
        copy_detail = st.text_area("강조하고 싶은 소구점/혜택", placeholder="예: 한 손에 쏙 들어오는 휴대성, 강력한 상쾌함", height=100, key="copy_input_detail")
        
        if st.button("✍️ 마케팅 카피라이팅 문구 추출 실행", type="primary", use_container_width=True):
            gemini_client = get_gemini_client()
            if gemini_client and copy_topic:
                with st.spinner("카피라이팅 문구 추출 중..."):
                    copy_prompt = f"제품/브랜드: {copy_topic}, 채널: {copy_channel}, 주요혜택: {copy_detail}\n위 정보를 바탕으로 마케팅 카피라이팅 문구 10개를 작성하세요."
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
            with col_cpbtn2:
                st.download_button("📥 텍스트 다운로드", data=st.session_state.saved_copy_result, file_name="Copywriting.txt", use_container_width=True)

# ==========================================
# 📊 TAB 4: 마케팅 성과 & 음원 분석 대시보드 (서브 분리 및 대제목 4번)
# ==========================================
with main_tab4:
    st.markdown("### 📊 4. 마케팅 성과 & 음원 분석 대시보드")
    st.caption("독립 대시보드 영역: 등록, 수정, 삭제 데이터를 하단 집계 및 추이 차트로 실시간 연동합니다.")
    
    sub_dash1, sub_dash2, sub_dash3 = st.tabs([
        "📄 4-1. 인게이지먼트 성과 장표 관리",
        "🎵 4-2. 음원별 플랫폼 발행 수 카운팅",
        "📈 4-3. 음원 사이트별 일자별 추이"
    ])

    # 서브 탭 4-1: 장표 관리 및 추가/삭제
    with sub_dash1:
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            with st.expander("➕ 새 콘텐츠 성과 데이터 등록하기", expanded=True):
                col_in1, col_in2, col_in3 = st.columns(3)
                with col_in1:
                    in_date = st.date_input("발행 날짜")
                    in_platform = st.selectbox("플랫폼", ["인스타그램 릴스", "유튜브 쇼츠", "틱톡"])
                with col_in2:
                    in_title = st.text_input("콘텐츠 제목", placeholder="예: 상쾌함 반응 챌린지")
                    in_song = st.text_input("사용 음원명", placeholder="예: My Custom Beat")
                with col_in3:
                    in_views = st.number_input("조회수", min_value=0, value=10000)
                    in_likes = st.number_input("좋아요", min_value=0, value=500)
                    in_comments = st.number_input("댓글", min_value=0, value=30)
                    in_shares = st.number_input("공유수", min_value=0, value=50)

                if st.button("✨ 데이터 목록에 즉시 추가하기", use_container_width=True, type="primary"):
                    new_row = pd.DataFrame([{
                        "날짜": str(in_date),
                        "플랫폼": in_platform,
                        "콘텐츠 제목": in_title if in_title else "제목 없음",
                        "사용 음원": in_song if in_song else "기본 음원",
                        "조회수": in_views,
                        "좋아요": in_likes,
                        "댓글": in_comments,
                        "공유수": in_shares
                    }])
                    st.session_state.analytics_data = pd.concat([st.session_state.analytics_data, new_row], ignore_index=True)
                    st.success(f"✅ '{in_title}' 콘텐츠가 추가되었습니다!")

        with col_f2:
            st.markdown("##### 🗑️ 항목 관리")
            if not st.session_state.analytics_data.empty:
                del_target = st.selectbox("삭제할 콘텐츠 선택", st.session_state.analytics_data["콘텐츠 제목"].tolist())
                if st.button("🗑️ 선택 항목 삭제하기", use_container_width=True):
                    st.session_state.analytics_data = st.session_state.analytics_data[
                        st.session_state.analytics_data["콘텐츠 제목"] != del_target
                    ].reset_index(drop=True)
                    st.warning(f"🗑️ '{del_target}' 항목이 삭제되었습니다.")
                    st.rerun()

        st.divider()

        df = st.session_state.analytics_data.copy()
        for c in ["조회수", "좋아요", "댓글", "공유수"]:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        df["총 반응수"] = df["좋아요"] + df["댓글"] + df["공유수"]
        df["인게이지먼트율(%)"] = df.apply(
            lambda r: round((r["총 반응수"] / r["조회수"] * 100), 2) if r["조회수"] > 0 else 0.0, axis=1
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 콘텐츠 발행수", f"{len(df)}개")
        m2.metric("누적 총 조회수", f"{int(df['조회수'].sum()):,}회")
        m3.metric("누적 총 반응수", f"{int(df['총 반응수'].sum()):,}개")
        avg_eng = df['인게이지먼트율(%)'].mean() if len(df) > 0 else 0
        m4.metric("평균 인게이지먼트율", f"{avg_eng:.2f}%")

        st.divider()

        col_t_head, col_t_dl = st.columns([3, 1])
        with col_t_head:
            st.markdown("##### 📄 전체 콘텐츠 성과 장표")
        with col_t_dl:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='콘텐츠성과')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 엑셀(.xlsx) 다운로드",
                data=excel_data,
                file_name="마케팅_콘텐츠_성과장표.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            key="main_dashboard_editor"
        )
        st.session_state.analytics_data = edited_df

    # 서브 탭 4-2: 플랫폼별 음원 카운팅
    with sub_dash2:
        st.markdown("#### 🎵 음원별 플랫폼 발행 수 자동 집계")
        valid_df = st.session_state.analytics_data[
            st.session_state.analytics_data["사용 음원"].notnull() & (st.session_state.analytics_data["사용 음원"] != "")
        ]
        if not valid_df.empty:
            music_counts = valid_df.groupby(["사용 음원", "플랫폼"]).size().unstack(fill_value=0)
            for p in ["인스타그램 릴스", "유튜브 쇼츠", "틱톡"]:
                if p not in music_counts.columns:
                    music_counts[p] = 0
            music_counts = music_counts[["인스타그램 릴스", "유튜브 쇼츠", "틱톡"]]
            music_counts["총 제작 콘텐츠 수"] = music_counts.sum(axis=1)
            st.dataframe(music_counts, use_container_width=True)
        else:
            st.info("등록된 데이터가 없습니다.")

    # 서브 탭 4-3: 음원 사이트 추이
    with sub_dash3:
        st.markdown("#### 📈 음원 사이트별 일자별 트렌드 추이")
        valid_df = st.session_state.analytics_data[
            st.session_state.analytics_data["사용 음원"].notnull() & (st.session_state.analytics_data["사용 음원"] != "")
        ]
        song_list = list(valid_df["사용 음원"].unique()) if not valid_df.empty else ["Minty Fresh Beat"]
        selected_song = st.selectbox("분석할 음원 선택", song_list)

        dates = pd.date_range(start="2026-08-25", periods=7, freq="D").strftime("%Y-%m-%d")
        trend_df = pd.DataFrame({
            "날짜": dates,
            "유튜브 뮤직": [12000, 15400, 21000, 28000, 35000, 42000, 51000],
            "멜론": [8500, 9200, 11500, 14200, 18900, 23000, 27500],
            "스포티파이": [5400, 6800, 8900, 12000, 15800, 19500, 24000]
        }).set_index("날짜")
        st.line_chart(trend_df)
