import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import random
import string
import time

# 環境変数の読み込み
load_dotenv()

# ページ設定
st.set_page_config(page_title="Spotify Random Tracks", page_icon="🎵", layout="wide")

# CSSでスタイリング
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #1DB954;
        color: white;
        border: none;
        border-radius: 20px;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #1ed760;
        color: white;
        border-color: #1ed760;
    }
    div[data-testid="stImage"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    div[data-testid="stImage"]:hover {
        transform: scale(1.02);
    }
    .track-title {
        font-weight: bold;
        font-size: 1rem;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .track-artist {
        color: #b3b3b3;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
</style>
""", unsafe_allow_html=True)

def init_spotify():
    """Spotifyクライアントを初期化する"""
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        st.error("⚠️ Spotify APIの認証情報が設定されていません。.envファイルを確認してください。")
        return None
        
    try:
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp
    except Exception as e:
        st.error(f"認証エラーが発生しました: {e}")
        return None

def get_random_tracks(sp, limit=12):
    """ランダムに複数の楽曲を取得する"""
    tracks = []
    attempts = 0
    max_attempts = limit * 3  # 無限ループ防止
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    while len(tracks) < limit and attempts < max_attempts:
        attempts += 1
        
        # 検索クエリ用のランダムな文字
        characters = string.ascii_lowercase
        random_char = random.choice(characters)
        query = f"{random_char}%"
        
        try:
            # ランダムなオフセットで検索
            offset = random.randint(0, 950)
            results = sp.search(q=query, type='track', limit=1, offset=offset)
            items = results['tracks']['items']
            
            if items:
                track = items[0]
                # アートワークとプレビューURLがあるものだけ採用
                if track['album']['images'] and track['preview_url']:
                    # 重複チェック（IDで確認）
                    if not any(t['id'] == track['id'] for t in tracks):
                        tracks.append(track)
                        # 進捗更新
                        progress = len(tracks) / limit
                        progress_bar.progress(progress)
                        status_text.text(f"楽曲収集中... {len(tracks)}/{limit}")
                        
        except Exception:
            continue
            
    status_text.empty()
    progress_bar.empty()
    return tracks

def main():
    st.title("🎵 Spotify Random Tracks Grid")
    st.write("ランダムに収集した楽曲をグリッドで表示します。")

    sp = init_spotify()
    
    # セッションステート初期化
    if 'tracks' not in st.session_state:
        st.session_state.tracks = []

    if sp:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎲 新しい楽曲を見つける", type="primary"):
                with st.spinner("世界中から音楽を集めています..."):
                    st.session_state.tracks = get_random_tracks(sp, limit=12)
        
        st.write("---")
        
        # グリッド表示
        if st.session_state.tracks:
            # 4列のグリッドを作成
            cols_count = 4
            rows = [st.session_state.tracks[i:i + cols_count] for i in range(0, len(st.session_state.tracks), cols_count)]
            
            for row in rows:
                cols = st.columns(cols_count)
                for i, track in enumerate(row):
                    with cols[i]:
                        # アートワーク
                        img_url = track['album']['images'][0]['url']
                        st.image(img_url, use_column_width=True)
                        
                        # 曲情報
                        track_name = track['name']
                        artist_name = track['artists'][0]['name']
                        
                        st.markdown(f'<div class="track-title" title="{track_name}">{track_name}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="track-artist" title="{artist_name}">{artist_name}</div>', unsafe_allow_html=True)
                        
                        # プレビュー再生
                        if track['preview_url']:
                            st.audio(track['preview_url'], format='audio/mp3')
                        
                        # Spotifyリンク
                        st.link_button("Spotifyで開く", track['external_urls']['spotify'])
                        
                st.write("") # 行間のスペース
        
        elif st.session_state.tracks == []:
             st.info("上のボタンを押して、音楽の旅を始めましょう！")

if __name__ == "__main__":
    main()
