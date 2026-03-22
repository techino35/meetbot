# MeetBot

音声・動画ファイルから議事録を自動生成するWebアプリ。

## アーキテクチャ

```
[ブラウザ] → [React/Vite] → [FastAPI] → [Whisper API] → [Claude API] → [Google Docs]
```

## セットアップ

### 1. 環境変数

```bash
cp .env.example .env
# .envを編集してAPIキーを設定
```

必須:
- `OPENAI_API_KEY` - Whisper使用
- `ANTHROPIC_API_KEY` - Claude使用
- `GOOGLE_CREDENTIALS_JSON` - Google Docsへの書き込み

### 2. Docker Composeで起動

```bash
docker compose up --build
```

- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

### 3. ローカル開発（Docker不使用）

バックエンド:
```bash
cd products/meetbot
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

フロントエンド:
```bash
cd frontend
npm install
npm run dev
```

## Google Cloud設定

1. Google Cloud Consoleでサービスアカウント作成
2. Google Docs API + Google Drive APIを有効化
3. サービスアカウントにEditor権限付与
4. JSONキーをダウンロード → 1行にminifyして`GOOGLE_CREDENTIALS_JSON`に設定

```bash
# JSONを1行に変換
cat service-account.json | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)))"
```

## デプロイ（Railway）

1. GitHubリポジトリを連携
2. `Dockerfile.backend`を指定
3. 環境変数を設定
4. デプロイ

## 対応ファイル形式

音声: mp3, wav, m4a, ogg, flac, aac
動画: mp4, mov, mkv, avi, webm（ffmpegで音声抽出）

## ファイルサイズ制限

デフォルト500MB。Whisper APIは25MBまでのため、超える場合は自動チャンク分割。
