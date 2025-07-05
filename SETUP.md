# プロファイル分析APIのセットアップと実行手順

## 環境セットアップ

### 前提条件
- Python 3.8以上
- OpenAI APIキー

### 手順

1. 仮想環境の作成（推奨）
   ```bash
   python -m venv venv
   
   # Windowsの場合
   venv\Scripts\activate
   
   # Mac/Linuxの場合
   source venv/bin/activate
   ```

2. 依存関係のインストール
   ```bash
   pip install -r requirements.txt
   ```

3. 環境変数の設定
   - `.env` ファイルを作成し、以下の内容を設定
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   - `your_openai_api_key_here` を実際のOpenAI APIキーに置き換えてください

## APIの起動

1. FastAPI サーバーの起動
   ```bash
   uvicorn main:app --reload
   ```
   - サーバーがポート8000で起動します
   - `--reload` オプションを使うと、コード変更時に自動的にサーバーが再起動します

2. APIドキュメントへのアクセス
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## APIのテスト

1. プロファイル分析APIのテスト
   ```bash
   python test_api.py
   ```
   
   あるいは、curlコマンドで直接リクエスト
   
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/analyze/profile' \
     -H 'Content-Type: application/json' \
     -d '{
     "transcription": "今日はとても疲れました。朝から会議が3つもあって、資料作成に追われていました。でも、プロジェクトが前に進んだので良かったです。明日は少し早く帰って休みたいですね。"
   }'
   ```

## 設定カスタマイズ

`main.py` でOpenAIのモデル指定や他のパラメータを変更できます。

1. モデルの変更
   - `model="gpt-4"` を `model="gpt-3.5-turbo"` に変更することで、より安価なモデルを使用できます

2. プロンプトのカスタマイズ
   - `prompt` 変数の内容を変更することで、分析内容や出力形式をカスタマイズできます 