# ChatGPT Relay API ドキュメント

## 概要
このAPIは、ChatGPTとの中継機能と感情分析処理機能を提供します。

## ベースURL
```
http://localhost:8002
```

## エンドポイント一覧

### 1. ヘルスチェック
```
GET /health
```

**説明**: APIの稼働状況と設定情報を確認します。

**レスポンス例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-15T22:12:46.919978",
  "mode": "local",
  "ec2_base_url": "local",
  "openai_model": "gpt-4"
}
```

### 2. ChatGPT中継
```
POST /analyze/chatgpt
```

**説明**: プロンプトをChatGPT APIに中継し、応答をJSON形式で返します。

**リクエスト**:
```json
{
  "prompt": "あなたのプロンプトをここに入力"
}
```

**レスポンス**: ChatGPTからの応答をJSON形式で返します。

### 3. 感情分析処理（従来版）
```
POST /process/emotion-timeline
```

**説明**: 指定されたユーザーと日付のemotion-timeline_gpt_prompt.jsonを読み込み、ChatGPTで処理して結果をemotion-timeline.jsonに保存します。

**リクエスト**:
```json
{
  "username": "user123",
  "date": "2025-06-07"
}
```

**ファイルパス**:
- 入力: `/Users/kaya.matsumoto/data/data_accounts/{username}/{date}/transcriptions/emotion-timeline_gpt_prompt.json`
- 出力: `/Users/kaya.matsumoto/data/data_accounts/{username}/{date}/emotion-timeline.json`

### 4. ローカル感情分析処理（新版）
```
POST /analyze-mood
```

**説明**: ローカルファイルシステムから感情分析を実行します。

**リクエスト**:
```json
{
  "user_id": "user123",
  "date": "2025-06-07"
}
```

**ファイルパス**:
- 入力: `/Users/kaya.matsumoto/data/data_accounts/{user_id}/{date}/prompt/emotion-timeline_gpt_prompt.json`
- 出力: `/Users/kaya.matsumoto/data/data_accounts/{user_id}/{date}/emotion-timeline/emotion-timeline.json`

**レスポンス例**:
```json
{
  "status": "success",
  "message": "ローカル感情分析処理が完了しました",
  "user_id": "user123",
  "date": "2025-06-07",
  "local_file": "/Users/kaya.matsumoto/data/data_accounts/user123/2025-06-07/emotion-timeline/emotion-timeline.json",
  "processed_at": "2025-06-15T22:24:17.516853",
  "processing_log": {
    "start_time": "2025-06-15T22:24:00.000000",
    "mode": "local",
    "processing_steps": [...],
    "complete": true,
    "warnings": []
  },
  "validation_summary": {
    "total_warnings": 0,
    "structure_valid": true,
    "nan_handling": "not_required"
  }
}
```

### 5. EC2連携感情分析処理（新版）
```
POST /analyze-mood-ec2
```

**説明**: EC2からプロンプトを取得し、処理後にEC2にアップロードします。

**リクエスト**:
```json
{
  "user_id": "user123",
  "date": "2025-06-07"
}
```

**処理フロー**:
1. EC2からプロンプト取得: `GET {EC2_BASE_URL}/status/{user_id}/{date}/prompt/emotion-timeline_gpt_prompt.json`
2. ChatGPT処理（リトライ機能付き）
3. ローカル保存
4. EC2アップロード: `POST {EC2_BASE_URL}/upload/analysis/emotion-timeline`

**レスポンス例**:
```json
{
  "status": "success",
  "message": "EC2連携感情分析処理が完了しました",
  "user_id": "user123",
  "date": "2025-06-07",
  "local_file": "/Users/kaya.matsumoto/data/data_accounts/user123/2025-06-07/emotion-timeline/emotion-timeline.json",
  "ec2_upload": true,
  "processed_at": "2025-06-15T22:24:38.055276",
  "processing_log": {
    "start_time": "2025-06-15T22:24:20.000000",
    "mode": "ec2",
    "ec2_base_url": "https://api.hey-watch.me",
    "processing_steps": [...],
    "complete": true,
    "warnings": []
  },
  "validation_summary": {
    "total_warnings": 0,
    "structure_valid": true,
    "nan_handling": "not_required"
  }
}
```

### 6. EC2接続デバッグ
```
GET /debug-ec2-connection
```

**説明**: EC2接続状況をテストし、デバッグ情報を提供します。

**レスポンス例**:
```json
{
  "timestamp": "2025-06-15T22:12:56.674453",
  "environment": {
    "EC2_BASE_URL": "local",
    "mode": "local",
    "OPENAI_MODEL": "gpt-4",
    "has_openai_key": true
  },
  "tests": [
    {
      "test": "local_mode",
      "status": "active",
      "message": "ローカルモードで動作中"
    }
  ]
}
```

## 環境変数設定

### 必須環境変数
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### オプション環境変数
```bash
# OpenAIモデル（デフォルト: gpt-4）
OPENAI_MODEL=gpt-4

# EC2連携設定（デフォルト: local）
# ローカルモード: "local"
# EC2連携: "https://api.hey-watch.me"
EC2_BASE_URL=local
```

## 動作モード

### ローカルモード（EC2_BASE_URL="local"）
- プロンプト取得: ローカルファイルシステム
- 結果保存: ローカルファイルシステムのみ
- EC2アップロード: スキップ

### EC2連携モード（EC2_BASE_URL="https://api.hey-watch.me"）
- プロンプト取得: EC2サーバーからHTTP GET
- 結果保存: ローカル保存 → EC2アップロードの2段階
- リトライ機能: OpenAI API呼び出しに指数バックオフ付きリトライ

## エラーハンドリング

### 一般的なエラーレスポンス
```json
{
  "detail": "エラーメッセージ"
}
```

### ステータスコード
- `200`: 成功
- `400`: リクエストエラー（不正なJSON、必須フィールド不足など）
- `404`: ファイルまたはリソースが見つからない
- `500`: サーバー内部エラー（ChatGPT API エラー、ファイル操作エラーなど）

## 処理機能

### JSON抽出処理
ChatGPTの応答から以下のパターンでJSONを抽出：
1. 応答全体がJSON形式
2. ```json ... ``` 形式で囲まれている場合
3. { ... } の形式の最初のJSONブロック

### NaN値処理
- 文字列 "NaN" を float('nan') に変換
- 平均値計算時にNaN値を除外

### 構造バリデーション
- emotionScores配列が48個に満たない場合、NaNで補完
- averageScoreをNaN値を除外して再計算

### リトライ機能
- OpenAI API呼び出しに3回まで指数バックオフ付きリトライ
- レート制限（429エラー）に対応

## 依存関係

```
fastapi==0.100.0
uvicorn==0.23.0
pydantic==2.0.2
python-dotenv==1.0.0
openai>=1.0.0
requests>=2.31.0
python-multipart>=0.0.6
aiohttp>=3.8.0
tenacity>=8.2.0
```

## 起動方法

```bash
# 依存関係のインストール
pip install -r requirements.txt

# サーバー起動
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# または
python main.py
```

## テスト方法

```bash
# テストスクリプト実行
python test_mood_analysis.py

# または
./test_mood_analysis.sh
``` 