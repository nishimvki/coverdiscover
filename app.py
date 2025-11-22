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
    /* ボタンのデフォルトスタイル */
    .stButton>button {
        width: 100%;
        border: none;
    }
    /* メインのアクションボタン（ランダム取得・もっと見る） */
    /* 最初のボタン（リフレッシュ） */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) .stButton > button {
        background-color: #1DB954;
        color: white;
        border-radius: 20px;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }
    div[data-testid="stVerticalBlock"] > div:nth-child(1) .stButton > button:hover {
        background-color: #1ed760;
        color: white;
        border-color: #1ed760;
    }
    /* グリッド内の詳細ボタン */
    div[data-testid="stColumn"] .stButton > button {
        margin-top: 5px;
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

def get_random_tracks(sp, limit=12, existing_tracks=None):
    """ランダムに複数の楽曲を取得する（高速化版）"""
    if existing_tracks is None:
        existing_tracks = []
        
    new_tracks = []
    attempts = 0
    max_attempts = 10
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    while len(new_tracks) < limit and attempts < max_attempts:
        attempts += 1
        
        characters = string.ascii_lowercase
        random_char = random.choice(characters)
        query = f"{random_char}%"
        
        try:
            offset = random.randint(0, 900)
            results = sp.search(q=query, type='track', limit=50, offset=offset)
            items = results['tracks']['items']
            
            random.shuffle(items)
            
            for track in items:
                if len(new_tracks) >= limit:
                    break
                    
                if track['album']['images']:
                    image = track['album']['images'][0]
                    if image['height'] == image['width']:
                        # 既存のトラックも含めて重複チェック
                        if not any(t['id'] == track['id'] for t in existing_tracks + new_tracks):
                            new_tracks.append(track)
                            
            progress = min(len(new_tracks) / limit, 1.0)
            progress_bar.progress(progress)
            status_text.text(f"楽曲収集中... {len(new_tracks)}/{limit}")
                        
        except Exception:
            continue
            
    status_text.empty()
    progress_bar.empty()
    return new_tracks

@st.dialog("楽曲詳細")
def show_track_details(track):
    """楽曲の詳細情報をモーダル表示する"""
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.image(track['album']['images'][0]['url'], use_container_width=True)
        
    with col2:
        st.subheader(track['name'])
        artists = [artist['name'] for artist in track['artists']]
        st.write(f"**アーティスト:** {', '.join(artists)}")
        st.write(f"**アルバム:** {track['album']['name']}")
        st.write(f"**リリース日:** {track['album']['release_date']}")
        
        if track['preview_url']:
            st.audio(track['preview_url'], format='audio/mp3')
        else:
            st.caption("🎵 プレビュー再生は利用できません")
            
        st.link_button("Spotifyで聴く", track['external_urls']['spotify'])
        st.progress(track['popularity'], text=f"人気度: {track['popularity']}/100")

def main():
    st.title("🎵 Spotify Random Tracks Grid")
    st.write("ランダムに収集した楽曲をグリッドで表示します。アートワーク下のボタンで詳細を確認できます。")

    sp = init_spotify()
    
    if 'tracks' not in st.session_state:
        st.session_state.tracks = []

    if sp:
        # 初回アクセス時（トラックリストが空の場合）に自動取得
        if not st.session_state.tracks:
            with st.spinner("世界中から音楽を集めています..."):
                initial_tracks = get_random_tracks(sp, limit=12)
                st.session_state.tracks = initial_tracks

        # リフレッシュボタン（上部）
        # col1, col2, col3 = st.columns([1, 2, 1])
        # with col2:
        #     if st.button("🔄 リセットして新しい楽曲を探す", type="primary"):
        #         with st.spinner("世界中から音楽を集めています..."):
        #             st.session_state.tracks = get_random_tracks(sp, limit=12)
        #             st.rerun()
        
        st.write("---")
        
        # グリッド表示
        if st.session_state.tracks:
            cols_count = 4
            rows = [st.session_state.tracks[i:i + cols_count] for i in range(0, len(st.session_state.tracks), cols_count)]
            
            for row in rows:
                cols = st.columns(cols_count)
                for i, track in enumerate(row):
                    with cols[i]:
                        st.image(track['album']['images'][0]['url'], use_container_width=True)
                        if st.button("詳細を見る", key=f"btn_{track['id']}", use_container_width=True):
                            show_track_details(track)
                        
                st.write("") 
            
            st.write("---")
            
            # 「もっと見る」ボタン（下部）
            col1_b, col2_b, col3_b = st.columns([1, 2, 1])
            with col2_b:
                if st.button("⬇️ もっと見る", key="load_more"):
                    with st.spinner("追加の楽曲を探しています..."):
                        additional_tracks = get_random_tracks(sp, limit=12, existing_tracks=st.session_state.tracks)
                        st.session_state.tracks.extend(additional_tracks)
                        st.rerun()

if __name__ == "__main__":
    main()
