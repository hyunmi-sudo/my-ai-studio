def extract_auto_yt_data(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'extractor_args': {'youtube': {'player_client': ['android', 'web', 'tv']}}
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_title = info.get('title', 'N/A')
        
        # 1. 쇼츠 공식 음악 라이브러리 태그 우선 탐색 (캡처에 나오는 부분)
        track = info.get('track')
        artist = info.get('artist')
        album = info.get('album')
        
        if track and artist:
            final_song = f"{track} - {artist}"
        elif track:
            final_song = track
        elif artist:
            final_song = artist
        else:
            # 2. 설명란(description)이나 음원 태그 세부 검색
            description = info.get('description', '')
            music_match = re.search(r'Song\s*-\s*(.*?)\n|Artist\s*-\s*(.*?)\n', description)
            
            if music_match:
                final_song = music_match.group(0).replace('\n', '').strip()
            else:
                # 3. 제목 내 '가수 - 곡명' 패턴 파싱
                match = re.search(r'([가-힣\w\s]+)\s*-\s*([가-힣\w\s]+)', video_title)
                if match:
                    final_song = match.group(0).strip()
                else:
                    # 4. 채널명 및 클린 제목 활용
                    uploader = info.get('uploader') or info.get('channel') or ''
                    clean_title = re.sub(r'[\[\(].*?[\]\)]|#\w+', '', video_title).strip()
                    if uploader and clean_title:
                        final_song = f"{uploader} ({clean_title[:12]}...)"
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
