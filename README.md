# Spotify Random Track App

Streamlitを使用してSpotify APIからランダムに楽曲情報を取得し、アートワークを表示するWebアプリケーションです。

## セットアップ

1. リポジトリをクローンまたはダウンロードします。

2. 必要なパッケージをインストールします。
   ```bash
   pip install -r requirements.txt
   ```

3. Spotify Developer Dashboard (https://developer.spotify.com/dashboard) でアプリケーションを作成し、`Client ID` と `Client Secret` を取得します。
   - Redirect URIには `http://localhost:8501` を設定することをお勧めします（今回のアプリでは認証フローはClient Credentials Flowを使用するため、厳密には必須ではありませんが、設定しておくと良いでしょう）。

4. `.env.example` ファイルをコピーして `.env` ファイルを作成し、取得した認証情報を入力します。
   ```bash
   cp .env.example .env
   ```
   `.env` ファイルの内容:
   ```env
   SPOTIPY_CLIENT_ID=あなたのClient ID
   SPOTIPY_CLIENT_SECRET=あなたのClient Secret
   ```

## 実行方法

以下のコマンドでアプリを起動します。

```bash
streamlit run app.py
```

