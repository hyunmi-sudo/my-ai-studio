import re

def extract_auto_yt_data(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_title = info.get('title', 'N/A')
        uploader = info.get('uploader') or info.get('channel') or ''
        
        # 1차: 공식 메타데이터 확인 (track / artist)
        song_name = info.get('track')
        artist_name = info.get('artist')
        
        if song_name and artist_name:
            final_song = f"{artist_name} - {song_name}"
        elif song_name:
            final_song = song_name
        else:
            # 2차: 영상 제목에서 '가수 - 노래제목' 패턴 추출
            match = re.search(r'([가-힣\w\s]+)\s*-\s*([가-힣\w\s]+)', video_title)
            if match:
                final_song = match.group(0).strip()
            else:
                # 3차: 채널명 및 제목 일부 활용
                clean_title = re.sub(r'[\[\(].*?[\]\)]|#\w+', '', video_title).strip()
                if uploader:
                    final_song = f"{uploader} ({clean_title[:15]}...)"
                else:
                    final_song = clean_title if clean_title else "자유 입력 음원"

        return {
            "날짜": time.strftime("%Y-%m-%d"),
            "플랫폼": "유튜브 쇼츠" if "shorts" in url.lower() else "유튜브",
            "콘텐츠 제목": video_title,
            "사용 음원": final_song,
            "조회수": info.get('view_count', 0),
            "좋아요": info.get('like_count', 0),
            "댓글": info.get('comment_count', 0),
            "공유수": 0
        }
