# VibeGraph Generation API

Vault連携対応の心理グラフ(VibeGraph)生成・ChatGPT中継APIサービス

## 🎯 概要

このAPIは、ChatGPTとの中継機能と心理グラフ(VibeGraph)生成機能を提供するFastAPIベースのサービスです。Vault（WatchMeエコシステムのデータ保管庫）との連携により、音声転写データから心理状態のタイムラインを生成します。

## ✨ 主要機能

- **ChatGPT中継**: 任意のプロンプトをChatGPT APIに中継
- **心理グラフ(VibeGraph)生成**: 音声転写データから48時間分の心理状態スコアを生成
- **Vault連携**: WatchMeエコシステムのクラウドデータ保管庫との自動データ同期
- **リトライ機能**: OpenAI API呼び出しの安定性確保
- **NaN値処理**: 欠損データの適切な処理
- **構造バリデーション**: データ整合性の自動チェック

## 🚀 クイックスタート

### 1. 環境構築

```bash
# リポジトリのクローン
git clone <repository-url>
cd api_gpt_v1

# 仮想環境の作成・アクティベート
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate     # Windows

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. 環境変数設定

```bash
# 必須: OpenAI API キー
export OPENAI_API_KEY="sk-your-openai-api-key-here"

# オプション: モデル指定（デフォルト: gpt-4）
export OPENAI_MODEL="gpt-4"

# オプション: 動作モード
export EC2_BASE_URL="local"                    # ローカルモード
# または
export EC2_BASE_URL="https://api.hey-watch.me" # Vault連携モード（本番環境）
```

**注**: EC2_BASE_URLの"EC2"は歴史的な名称で、実際にはVault（WatchMeのデータ保管庫）への接続を意味します。

### 3. サーバー起動

```bash
# 開発モード（自動リロード有効）
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# または直接実行
python main.py
```

### 4. 動作確認

```bash
# ヘルスチェック
curl http://localhost:8002/health

# Vault接続テスト
curl http://localhost:8002/debug-ec2-connection
```

## 📚 API エンドポイント

### 基本情報
- **ベースURL**: `http://localhost:8002`
- **認証**: 不要（OpenAI APIキーは環境変数で設定）
- **レスポンス形式**: JSON

### エンドポイント一覧

#### 1. ヘルスチェック
```http
GET /health
```
APIの稼働状況と設定情報を確認

**レスポンス例:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-05T22:12:46.919978",
  "mode": "ec2",
  "ec2_base_url": "https://api.hey-watch.me",
  "openai_model": "gpt-4"
}
```

#### 2. ChatGPT中継
```http
POST /analyze/chatgpt
```
任意のプロンプトをChatGPT APIに中継

**リクエスト:**
```json
{
  "prompt": "あなたのプロンプトをここに入力"
}
```

#### 3. 心理グラフ(VibeGraph)生成 ⭐ 【メインエンドポイント】
```http
POST /analyze-vibegraph-vault
```
Vaultからプロンプトを取得し、ChatGPTで心理グラフを生成後、Vaultにアップロード

**リクエスト:**
```json
{
  "device_id": "d067d407-cf73-4174-a9c1-d91fb60d64d0",
  "date": "2025-07-05"
}
```

**レスポンス例:**
```json
{
  "status": "success",
  "message": "Vault連携心理グラフ(VibeGraph)処理が完了しました",
  "device_id": "d067d407-cf73-4174-a9c1-d91fb60d64d0",
  "date": "2025-07-05",
  "local_file": "/path/to/local/emotion-timeline.json",
  "ec2_upload": true,
  "processed_at": "2025-07-05T22:53:08.130876",
  "processing_log": {
    "mode": "ec2",
    "processing_steps": [
      "プロンプト取得完了",
      "ChatGPT処理完了",
      "構造バリデーション完了",
      "ローカル保存完了",
      "EC2アップロード完了"
    ],
    "warnings": []
  }
}
```

#### 4. Vault接続デバッグ
```http
GET /debug-ec2-connection
```
Vault接続状況をテストし、デバッグ情報を提供

**注**: エンドポイント名の"ec2"は歴史的な名称で、実際にはVault接続をテストします。

## 🔧 動作モード

### ローカルモード (`EC2_BASE_URL="local"`)
- プロンプト取得: ローカルファイルシステム
- 結果保存: ローカルファイルシステムのみ
- 用途: 開発・テスト環境

### Vault連携モード (`EC2_BASE_URL="https://api.hey-watch.me"`)
- プロンプト取得: Vault（データ保管庫）からHTTP GET
- 結果保存: ローカル保存 → Vaultアップロードの2段階
- 用途: 本番環境

**Vaultとは**: WatchMeエコシステムの中央データ保管庫。全てのユーザーデータ（音声、転写、心理グラフ等）を安全に保存・管理するクラウドサービスです。

## 📁 ファイル構造

### ローカルファイルシステム
```
/Users/kaya.matsumoto/data/data_accounts/{device_id}/{YYYY-MM-DD}/
├── prompt/
│   └── emotion-timeline_gpt_prompt.json   # 入力プロンプト
└── emotion-timeline/
    └── emotion-timeline.json             # 心理グラフ(VibeGraph)生成結果
```

### Vault（データ保管庫）
```
/data/data_accounts/{device_id}/{YYYY-MM-DD}/
├── prompt/
│   └── emotion-timeline_gpt_prompt.json   # 入力プロンプト
└── emotion-timeline/
    └── emotion-timeline.json             # 心理グラフ(VibeGraph)生成結果
```

## 🧪 テスト

### 基本テスト
```bash
# 全エンドポイントテスト
python test_mood_analysis.py

# Vault連携専用テスト
python test_ec2_mode.py

# シェルスクリプト実行
./test_mood_analysis.sh
```

### 手動テスト例
```bash
# 心理グラフ(VibeGraph)生成 - Vault連携
curl -X POST http://localhost:8002/analyze-vibegraph-vault \
  -H "Content-Type: application/json" \
  -d '{"device_id": "d067d407-cf73-4174-a9c1-d91fb60d64d0", "date": "2025-07-05"}'

# 汎用ChatGPT中継
curl -X POST http://localhost:8002/analyze/chatgpt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "あなたのプロンプトをここに入力"}'
```

## 🔍 処理機能詳細

### JSON抽出処理
ChatGPTの応答から以下のパターンでJSONを抽出：
1. 応答全体がJSON形式
2. ```json ... ``` 形式で囲まれている場合
3. { ... } の形式の最初のJSONブロック

### NaN値処理
- 文字列 "NaN" を `float('nan')` に変換
- 平均値計算時にNaN値を除外
- 欠損データの適切な処理

### 構造バリデーション
- `emotionScores`配列が48個に満たない場合、NaNで補完
- `averageScore`をNaN値を除外して再計算
- データ整合性の自動チェック

### リトライ機能
- OpenAI API呼び出しに3回まで指数バックオフ付きリトライ
- レート制限（429エラー）に対応
- 安定した処理の実現

## 📊 出力データ仕様

### 心理グラフ(VibeGraph)結果フォーマット
```json
{
  "timePoints": ["00:00", "00:30", ..., "23:30"],
  "emotionScores": [0, 15, 25, ..., 0],
  "averageScore": 15.2,
  "positiveHours": 18.0,
  "negativeHours": 2.0,
  "neutralHours": 28.0,
  "insights": [
    "午前中は静かな状態が続いた",
    "午後は心理状態の変動が少なかった",
    "全体として安定した心理状態"
  ],
  "emotionChanges": [
    {
      "time": "09:00",
      "event": "ポジティブな変化",
      "score": 75
    }
  ],
  "date": "2025-07-05"
}
```

## ⚠️ エラーハンドリング

### HTTPステータスコード
- `200`: 成功
- `400`: リクエストエラー（不正なJSON、必須フィールド不足など）
- `404`: ファイルまたはリソースが見つからない（プロンプトファイルなど）
- `500`: サーバー内部エラー（ChatGPT API エラー、ファイル操作エラー、Vault接続エラーなど）

### 一般的なエラーレスポンス
```json
{
  "detail": "エラーメッセージ"
}
```

## 📦 依存関係

```txt
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

## 🔐 セキュリティ

- OpenAI APIキーは環境変数で管理
- SSL/TLS通信対応（EC2連携時）
- 入力データのバリデーション
- エラー情報の適切な制限

## 🚀 デプロイ

### 本番環境設定
```bash
# 環境変数設定
export OPENAI_API_KEY="your-production-key"
export EC2_BASE_URL="https://api.hey-watch.me"  # Vault接続
export OPENAI_MODEL="gpt-4"

# サーバー起動（本番モード）
uvicorn main:app --host 0.0.0.0 --port 8002
```

### Docker対応（オプション）
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
```

## 📝 ログ

### 処理ログ
- 詳細な処理ステップログ（11段階）
- バリデーション情報の記録
- 警告とエラーの追跡
- 処理時間の記録

### デバッグ情報
- EC2接続状況
- 環境変数設定状況
- OpenAI API接続状況

## 🤝 貢献

1. フォークしてください
2. フィーチャーブランチを作成してください (`git checkout -b feature/AmazingFeature`)
3. 変更をコミットしてください (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュしてください (`git push origin feature/AmazingFeature`)
5. プルリクエストを開いてください

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesページでお知らせください。

---

**開発者**: WatchMe VibeGraph API Team  
**バージョン**: 2.0.0  
**最終更新**: 2025-07-05  
**主な変更**: device_id移行完了、心理グラフ(VibeGraph)名称統一、Vault連携最適化