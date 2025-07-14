# VibeGraph Generation API

Supabase統合版の心理グラフ(VibeGraph)生成・ChatGPT中継APIサービス

## 🎯 概要

このAPIは、ChatGPTとの中継機能と心理グラフ(VibeGraph)生成機能を提供するFastAPIベースのサービスです。Supabaseデータベースとの統合により、音声転写データから心理状態のタイムラインを生成します。

## ✨ 主要機能

- **ChatGPT中継**: 任意のプロンプトをChatGPT APIに中継
- **心理グラフ(VibeGraph)生成**: 音声転写データから48時間分の心理状態スコアを生成
- **Supabase統合**: `vibe_whisper_prompt`テーブルから読み込み、`vibe_whisper_summary`テーブルに保存
- **Docker対応**: 本番環境でのコンテナ化デプロイメント
- **systemd統合**: 自動起動・再起動機能
- **リトライ機能**: OpenAI API呼び出しの安定性確保
- **NaN値処理**: 欠損データの適切な処理
- **構造バリデーション**: データ整合性の自動チェック

## 📋 更新履歴

### 2025-07-14 - バージョン 3.0.0
- **重要な変更**: ローカルモード・Vault連携機能を完全削除
- データソースをSupabase統合に一本化
- EC2_BASE_URL環境変数を削除
- requirements.txtの依存関係を修正（httpx==0.24.1, gotrue==1.3.0を固定）
- Docker/systemdによる本番環境デプロイメント方法を追加

## 🚀 クイックスタート

### 1. 環境構築

```bash
# リポジトリのクローン
git clone <repository-url>
cd api_gpt_v1

# 仮想環境の作成・アクティベート
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate     # Windows

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. 環境変数設定

`.env`ファイルを作成し、以下の環境変数を設定：

```bash
# 必須: OpenAI API キー
OPENAI_API_KEY=sk-your-openai-api-key-here

# 必須: Supabase設定
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# オプション: モデル指定（デフォルト: gpt-4）
OPENAI_MODEL=gpt-4
```

### 3. 開発サーバー起動

```bash
# 開発モード（自動リロード有効）
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# または直接実行
python3 main.py
```

### 4. 動作確認

```bash
# ヘルスチェック
curl http://localhost:8002/health
```

## 🐳 Docker デプロイメント

### ローカルでのDocker実行

```bash
# Dockerイメージのビルド
docker-compose build

# コンテナの起動
docker-compose up -d

# ログの確認
docker-compose logs -f

# コンテナの停止
docker-compose down
```

### 本番環境（EC2）へのデプロイ

#### 1. 必要なファイルをEC2サーバーにコピー

```bash
# プロジェクトディレクトリをEC2に作成
ssh -i ~/your-key.pem ubuntu@your-ec2-ip "mkdir -p ~/api_gpt_v1"

# 必要なファイルをコピー
scp -i ~/your-key.pem \
  Dockerfile \
  docker-compose.yml \
  main.py \
  supabase_client.py \
  requirements.txt \
  README.md \
  ubuntu@your-ec2-ip:~/api_gpt_v1/
```

#### 2. EC2サーバーで環境設定

```bash
# EC2にSSH接続
ssh -i ~/your-key.pem ubuntu@your-ec2-ip

# api_gpt_v1ディレクトリに移動
cd ~/api_gpt_v1

# .envファイルを作成
cat > .env << 'EOF'
OPENAI_API_KEY=your-production-api-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
EOF
```

#### 3. Dockerコンテナのビルドと起動

```bash
# Dockerイメージをビルド
docker-compose build --no-cache

# コンテナを起動
docker-compose up -d

# 動作確認
curl http://localhost:8002/health
```

## 🔧 systemd による自動起動設定

### 1. systemdサービスファイルの作成

```bash
sudo tee /etc/systemd/system/api-gpt-v1.service > /dev/null << 'EOF'
[Unit]
Description=API GPT v1 Docker Container
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/api_gpt_v1
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0
Restart=on-failure
RestartSec=10
User=ubuntu
Group=ubuntu

[Install]
WantedBy=multi-user.target
EOF
```

### 2. サービスの有効化と起動

```bash
# systemdデーモンをリロード
sudo systemctl daemon-reload

# サービスを有効化（自動起動設定）
sudo systemctl enable api-gpt-v1.service

# サービスを開始
sudo systemctl start api-gpt-v1.service

# 状態確認
sudo systemctl status api-gpt-v1.service
```

## 📊 運用管理

### サービス管理コマンド

```bash
# サービスの状態確認
sudo systemctl status api-gpt-v1

# サービスの停止
sudo systemctl stop api-gpt-v1

# サービスの開始
sudo systemctl start api-gpt-v1

# サービスの再起動
sudo systemctl restart api-gpt-v1

# ログの確認（リアルタイム）
sudo journalctl -u api-gpt-v1 -f

# Dockerコンテナのログ確認
docker logs -f api-gpt-v1
```

### 監視とトラブルシューティング

```bash
# コンテナの状態確認
docker ps | grep api-gpt

# ポート使用状況の確認
sudo lsof -i :8002

# APIヘルスチェック
curl http://localhost:8002/health

# Dockerコンテナの再起動
docker-compose restart

# 全体のリセット（データは保持）
docker-compose down && docker-compose up -d
```

## 📚 API エンドポイント

### 基本情報
- **ベースURL**: `http://your-server:8002`
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
  "timestamp": "2025-07-14T05:46:31.093872",
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

#### 3. 心理グラフ(VibeGraph)生成
```http
POST /analyze-vibegraph-supabase
```
`vibe_whisper_prompt`テーブルからプロンプトを取得し、ChatGPTで心理グラフを生成後、`vibe_whisper_summary`テーブルに保存

**リクエスト:**
```json
{
  "device_id": "d067d407-cf73-4174-a9c1-d91fb60d64d0",
  "date": "2025-07-13"
}
```

**レスポンス例:**
```json
{
  "status": "success",
  "message": "Supabase統合心理グラフ(VibeGraph)処理が完了しました",
  "device_id": "d067d407-cf73-4174-a9c1-d91fb60d64d0",
  "date": "2025-07-13",
  "database_save": true,
  "processed_at": "2025-07-14T05:40:38.875410",
  "processing_log": {
    "mode": "supabase",
    "processing_steps": [
      "vibe_whisper_promptからプロンプト取得完了",
      "ChatGPT処理完了",
      "構造バリデーション完了",
      "vibe_whisper_summaryテーブルに保存完了"
    ],
    "warnings": []
  }
}
```

## 📁 データベース構造

### Supabaseテーブル
- **vibe_whisper_prompt**: 入力プロンプトデータを格納
- **vibe_whisper_summary**: 心理グラフ(VibeGraph)生成結果を格納

## 🧪 テスト

### 基本テスト
```bash
# 全エンドポイントテスト
python3 test_mood_analysis.py

# シェルスクリプト実行
./test_mood_analysis.sh
```

### 手動テスト例
```bash
# 心理グラフ(VibeGraph)生成 - Supabase統合
curl -X POST http://localhost:8002/analyze-vibegraph-supabase \
  -H "Content-Type: application/json" \
  -d '{"device_id": "d067d407-cf73-4174-a9c1-d91fb60d64d0", "date": "2025-07-13"}'

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
  "date": "2025-07-13"
}
```

## ⚠️ エラーハンドリング

### HTTPステータスコード
- `200`: 成功
- `400`: リクエストエラー（不正なJSON、必須フィールド不足など）
- `404`: データが見つからない（プロンプトデータなど）
- `500`: サーバー内部エラー（ChatGPT API エラー、Supabase接続エラーなど）

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
httpx==0.24.1  # gotrue互換性のため固定
gotrue==1.3.0  # httpx互換性のため固定
supabase==2.3.4
```

## 🔐 セキュリティ

- OpenAI APIキーは環境変数で管理
- 入力データのバリデーション
- エラー情報の適切な制限

## 🚀 デプロイ

### 本番環境設定
```bash
# 環境変数設定
export OPENAI_API_KEY="your-production-key"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
export OPENAI_MODEL="gpt-4"

# サーバー起動（本番モード）
uvicorn main:app --host 0.0.0.0 --port 8002
```

### Docker対応
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
COPY supabase_client.py .
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
```

## 📝 ログ

### 処理ログ
- 詳細な処理ステップログ
- バリデーション情報の記録
- 警告とエラーの追跡
- 処理時間の記録

### デバッグ情報
- 環境変数設定状況
- OpenAI API接続状況
- Supabase接続状況

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

## 🧪 テスト実績

### 2025年7月14日テスト結果（Supabase統合版）

**テストデバイス**: `d067d407-cf73-4174-a9c1-d91fb60d64d0`

```bash
# ✅ Supabase統合版テスト
curl -X POST "http://3.24.16.82:8002/analyze-vibegraph-supabase" \
  -H "Content-Type: application/json" \
  -d '{"device_id": "d067d407-cf73-4174-a9c1-d91fb60d64d0", "date": "2025-07-13"}'
# → 成功: vibe_whisper_summaryテーブルに保存
```

**処理結果**:
- 📊 処理時間: 約21秒（ChatGPT API呼び出し含む）
- 📊 感情スコア: 平均-7.5（ネガティブ：1.0時間、ニュートラル：1.0時間）
- ✅ データベース保存: 正常完了
- ✅ 構造バリデーション: 48個のスコア正常処理

---

**開発者**: WatchMe VibeGraph API Team  
**バージョン**: 3.0.0  
**最終更新**: 2025-07-14  
**主な変更**: ローカルモード・Vault連携削除、Supabase統合一本化、Docker/systemdデプロイメント追加