import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import random
import string

# 環境変数の読み込み
load_dotenv()

# ページ設定
st.set_page_config(page_title="Spotify Random Track", page_icon="🎵")

# CSSでスタイリング
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #1DB954;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1ed760;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def init_spotify():
    """Spotifyクライアントを初期化する"""
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        st.error("⚠️ Spotify APIの認証情報が設定されていません。.envファイルを確認してください。")
        st.info("README.mdの手順に従って、SPOTIPY_CLIENT_IDとSPOTIPY_CLIENT_SECRETを設定してください。")
        return None
        
    try:
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp
    except Exception as e:
        st.error(f"認証エラーが発生しました: {e}")
        return None

def get_random_track(sp):
    """ランダムに楽曲を取得する"""
    # 検索クエリ用のランダムな文字
    # アルファベットからランダムに選択
    characters = string.ascii_lowercase
    random_char = random.choice(characters)
    
    # 検索クエリ（ワイルドカードを使用してヒット率を上げる）
    # 年指定などを加えてより最近の曲に絞るなどの工夫も可能だが、
    # ここではシンプルにランダムな文字で検索する
    query = f"{random_char}%"
    
    try:
        # まずヒット数を確認（limit=1）
        # type='track'で楽曲を検索
        results = sp.search(q=query, type='track', limit=1)
        total = results['tracks']['total']
        
        if total == 0:
            return None
            
        # オフセットをランダムに決定
        # Spotify APIの検索結果のオフセット上限は1000（または2000の場合もあるが安全策で1000）
        max_offset = min(total, 1000)
        offset = random.randint(0, max_offset - 1)
        
        # 実際に楽曲を取得
        results = sp.search(q=query, type='track', limit=1, offset=offset)
        items = results['tracks']['items']
        
        if items:
            return items[0]
        return None
        
    except Exception as e:
        st.error(f"検索中にエラーが発生しました: {e}")
        return None

def main():
    st.title("🎵 Spotify Random Track")
    st.write("ボタンを押すと、Spotifyからランダムに楽曲を取得して表示します。")
    st.write("---")

    sp = init_spotify()
    
    # セッションステートを使用して楽曲情報を保持
    if 'track' not in st.session_state:
        st.session_state.track = None

    if sp:
        if st.button("🎲 楽曲をランダムに取得", type="primary"):
            with st.spinner("楽曲を探しています..."):
                track = get_random_track(sp)
                if track:
                    st.session_state.track = track
                else:
                    st.warning("楽曲が見つかりませんでした。もう一度試してください。")
        
        # 取得した楽曲情報の表示
        if st.session_state.track:
            track = st.session_state.track
            st.write("---")
            
            # カラム分割で見やすく表示
            col1, col2 = st.columns([1, 1.5])
            
            with col1:
                # アルバムアートワーク
                if track['album']['images']:
                    st.image(track['album']['images'][0]['url'], use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/300x300?text=No+Image", use_column_width=True)
                    
            with col2:
                st.subheader(track['name'])
                
                # アーティスト名（複数可）
                artists = [artist['name'] for artist in track['artists']]
                st.write(f"**アーティスト:** {', '.join(artists)}")
                
                st.write(f"**アルバム:** {track['album']['name']}")
                st.write(f"**リリース日:** {track['album']['release_date']}")
                
                # プレビュー再生
                if track['preview_url']:
                    st.audio(track['preview_url'])
                else:
                    st.info("🎵 プレビュー再生は利用できません")
                    
                # Spotifyリンクボタン
                st.link_button("Spotifyで聴く", track['external_urls']['spotify'])
                
                # 人気度表示
                st.progress(track['popularity'], text=f"人気度: {track['popularity']}/100")

if __name__ == "__main__":
    main()

