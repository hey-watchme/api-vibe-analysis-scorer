# Vibe Scorer API(ChatGPT Gateway)

気分(Vibe)(心理グラフ)生成のためのChatGPT中継APIサービス

## 🌐 外部公開URL

**本番環境URL**: `https://api.hey-watch.me/vibe-scorer/`

- マイクロサービスとして外部から利用可能
- SSL/HTTPS対応
- CORS設定済み

## 🎯 概要

このAPIは、受け取ったPromptをChatGPTへと中継し、返ってきた値を心理グラフ(VibeGraph)の生成に使用するJSONへと変換するFastAPIベースのサービスです。Supabaseデータベースとの統合により、発話データから心理グラフ、気分スコアを生成します。

## 🤖 使用モデル情報

**現在使用中のAIモデル**: `gpt-5-nano`

### モデル変更履歴
- **2025-09-05**: `o4-mini` → `gpt-5-nano` (検証用設定)
- **2025-07-29**: デフォルト値削除、環境変数での明示的指定を必須化
- **初期設定**: `o4-mini`

### モデル設定方法
環境変数 `OPENAI_MODEL` で指定：
```bash
# .envファイル
OPENAI_MODEL=gpt-5-nano
```

## ✨ 主要機能

- **ChatGPT中継**: 任意のプロンプトをChatGPT APIに中継
- **心理グラフ(VibeGraph)生成**: 音声転写データから30分区切り、24時間、計48ブロックの心理スコアを生成
- **Supabase統合**: `vibe_whisper_prompt`テーブルから読み込み、`vibe_whisper_summary`テーブルに保存
- **Docker対応**: ECRを使ったデプロイ
- **systemd統合**: 自動起動・再起動機能
- **リトライ機能**: OpenAI API呼び出しの安定性確保
- **NaN値処理**: 欠損データの適切な処理
- **構造バリデーション**: データ整合性の自動チェック

## 📋 更新履歴

### 2025-09-11 - バージョン 3.4.0
- **新エンドポイント追加**: `/analyze-dashboard-summary` - dashboard_summaryテーブルと連携
- **機能追加**: dashboard_summaryテーブルのpromptフィールドからプロンプトを取得し、ChatGPT分析後にanalysis_resultフィールドに保存
- **Supabaseクライアント拡張**: dashboard_summary用のメソッドを追加
- **本番環境デプロイ完了**: EC2環境で正常動作確認済み

### 2025-09-05 - バージョン 3.3.2
- **OpenAIモデル変更**: `o4-mini` → `gpt-5-nano` に変更
- **検証用モデル設定**: モデル切り替えによる性能評価を実施
- **READMEモデル情報追加**: 使用モデル情報セクションを新設

### 2025-08-29 - バージョン 3.3.1
- **watchme-networkインフラ管理体制への移行**: docker-compose.ymlに`external: true`設定を追加
- **ネットワーク設定の明示化**: 本番環境で既に接続済みのwatchme-networkを設定ファイルに反映
- **systemd依存関係の追加**: watchme-infrastructure.serviceへの依存を設定（watchme-server-configs）
- **安定性向上**: 全マイクロサービス間の通信を統一ネットワークで保証

### 2025-08-01 - バージョン 3.3.0
- **日付処理の改善**: 音声ファイルの実際の記録日時を優先使用するように修正
- **データ整合性の向上**: `vibe_whisper_prompt`テーブルの日付を真実のデータとして扱う
- **エラーハンドリング強化**: 日付パラメータを必須化し、欠落時は明確なエラーを返す
- **トレーサビリティ向上**: 検索日付と実データ日付の両方をログに記録

### 2025-07-29 - バージョン 3.2.0
- **モデル指定方法の変更**: デフォルト値を削除し、環境変数での明示的な指定を必須化
- **現在のモデル**: `o4-mini`を使用
- **エラーハンドリング改善**: 環境変数未設定時に明確なエラーメッセージを表示

### 2025-07-15 - バージョン 3.1.0
- **外部URL公開**: `https://api.hey-watch.me/vibe-scorer/` で外部アクセス可能
- **Nginxリバースプロキシ設定**: SSL/HTTPS対応、CORS設定完了
- **ヘルスチェック修正**: Dockerfileにcurlを追加してヘルスチェック問題を解決

### 2025-07-14 - バージョン 3.0.0
- **重要な変更**: ローカルモード・Vault連携機能を完全削除
- データソースをSupabase統合に一本化
- EC2_BASE_URL環境変数を削除
- requirements.txtの依存関係を修正（httpx==0.24.1, gotrue==1.3.0を固定）
- Docker/systemdによる本番環境デプロイメント方法を追加

## ⚠️ 開発環境構築の注意事項

### Python バージョンの互換性
- **推奨バージョン**: Python 3.11
- **互換性の問題**: Python 3.13では`pydantic-core`のビルドで問題が発生する可能性があります
- **対処法**: 
  1. 仮想環境を使用することを強く推奨
  2. システムパッケージを直接使用する場合は`--break-system-packages`フラグが必要
  3. 本番環境ではDockerコンテナを使用するため、ローカル環境の問題は影響しません

### 必要なシステムパッケージ
以下のパッケージがシステムレベルでインストールされていない場合、手動でインストールが必要です：
```bash
pip3 install openai --user --break-system-packages
pip3 install tenacity --user --break-system-packages
```

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

# 必須: モデル指定
OPENAI_MODEL=gpt-5-nano  # 現在設定されているモデル
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
# ヘルスチェック（本番環境）
curl https://api.hey-watch.me/vibe-scorer/health

# ヘルスチェック（本番環境）
curl https://api.hey-watch.me/vibe-scorer/health
```

## 📌 API エンドポイント

### エンドポイント1

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/` | GET | ルートエンドポイント |
| `/health` | GET | ヘルスチェック |
| `/analyze/chatgpt` | POST | 任意のプロンプトをChatGPTに中継 |
| `/analyze-vibegraph-supabase` | POST | 1日分の心理グラフ生成（48タイムブロック統合） |
| `/analyze-dashboard-summary` | POST | Dashboard Summary分析（新規） |

### エンドポイント2 タイムブロック分析エンドポイント

| エンドポイント | メソッド | 説明 | 保存先 |
|--------------|---------|------|---------|
| `/analyze-timeblock` | POST | タイムブロック単位の分析処理 | dashboardテーブル |

#### タイムブロック分析の使用方法

```bash
# タイムブロック分析（ChatGPT処理＋DB保存）
curl -X POST https://api.hey-watch.me/vibe-scorer/analyze-timeblock \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "分析用プロンプト",
    "device_id": "9f7d6e27-98c3-4c19-bdfb-f7fda58b9a93",
    "date": "2025-08-31",
    "time_block": "17-00"
  }'
```

#### レスポンス形式

```json
{
  "status": "success",
  "message": "タイムブロック分析が完了しました（DB保存成功）",
  "device_id": "9f7d6e27-98c3-4c19-bdfb-f7fda58b9a93",
  "date": "2025-08-31",
  "time_block": "17-00",
  "analysis_result": {
    "time_block": "17-00",
    "summary": "30分間の状況説明",
    "vibe_score": -30,
    "confidence_score": 0.75,
    "key_observations": ["観察点1", "観察点2"],
    "detected_mood": "frustrated",
    "detected_activities": ["活動1", "活動2"],
    "context_notes": "時間帯から推測される状況"
  },
  "database_save": true,
  "processed_at": "2025-09-01T17:00:00.000Z",
  "model_used": "gpt-5-nano"
}
```

### エンドポイント3 Dashboard Summary分析エンドポイント

| エンドポイント | メソッド | 説明 | データソース | 保存先 |
|--------------|---------|------|------------|--------|
| `/analyze-dashboard-summary` | POST | Dashboard Summary統合分析 | dashboard_summaryテーブル | 同テーブルのanalysis_result |

#### Dashboard Summary分析の使用方法

```bash
# Dashboard Summary分析（ChatGPT処理＋更新）
curl -X POST https://api.hey-watch.me/vibe-scorer/analyze-dashboard-summary \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "9f7d6e27-98c3-4c19-bdfb-f7fda58b9a93",
    "date": "2025-09-11"
  }'
```

#### レスポンス形式

```json
{
  "status": "success",
  "message": "Dashboard Summary分析が完了しました",
  "device_id": "9f7d6e27-98c3-4c19-bdfb-f7fda58b9a93",
  "date": "2025-09-11",
  "database_save": true,
  "processed_at": "2025-09-11T17:23:26.945093",
  "model_used": "gpt-5-nano",
  "processing_log": {
    "processing_steps": [
      "dashboard_summaryからデータ取得完了",
      "プロンプト準備完了（4721文字）",
      "ChatGPT処理完了",
      "dashboard_summaryテーブルへの保存完了"
    ]
  },
  "analysis_result": {
    "current_time": "15:00",
    "time_context": "午後",
    "cumulative_evaluation": "1日の総合評価テキスト",
    "mood_trajectory": "positive_trend",
    "current_state_score": 36
  }
}
```

## 🔄 プロンプト生成APIとの連携

タイムブロック分析は、プロンプト生成APIと連携して高精度な心理分析を実現します：

### 処理フロー

```
1. プロンプト生成API (api_gen-prompt_mood-chart_v1)
   ├─ /generate-timeblock-prompt-v1 (Whisperのみ)
   └─ /generate-timeblock-prompt-v2 (Whisper + YAMNet)
           ↓
   生成されたプロンプト
           ↓
2. ChatGPT処理API (api_gpt_v1) 
   └─ /analyze-timeblock
           ↓
3. dashboardテーブル
   ├─ prompt: 生成されたプロンプト
   ├─ summary: ChatGPT分析結果のサマリー
   ├─ vibe_score: 感情スコア (-100〜100)
   └─ analysis_result: 完全なJSON応答 (JSONB)
```

### 連携例（Python）

```python
import requests

# 1. プロンプト生成
prompt_response = requests.get(
    "http://localhost:8009/generate-timeblock-prompt-v2",
    params={
        "device_id": "9f7d6e27-98c3-4c19-bdfb-f7fda58b9a93",
        "date": "2025-08-31",
        "time_block": "17-00"
    }
)

# 2. 生成されたプロンプトでChatGPT分析＋保存
if prompt_response.status_code == 200:
    # dashboardテーブルからプロンプトを取得
    # または prompt_response から直接取得
    
    analysis_response = requests.post(
        "https://api.hey-watch.me/vibe-scorer/analyze-timeblock",
        json={
            "prompt": prompt_text,
            "device_id": "9f7d6e27-98c3-4c19-bdfb-f7fda58b9a93",
            "date": "2025-08-31",
            "time_block": "17-00"
        }
    )
```

### データベース構造

#### dashboardテーブル
```sql
-- スキーマ更新済み (2025-09-01)
CREATE TABLE public.dashboard (
    device_id UUID NOT NULL,
    date DATE NOT NULL,
    time_block VARCHAR(5) NOT NULL,
    prompt TEXT,                    -- プロンプト生成APIから
    summary TEXT,                    -- ChatGPT分析結果
    vibe_score DOUBLE PRECISION,    -- 感情スコア
    analysis_result JSONB,           -- 完全なJSON応答（新規追加）
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (device_id, date, time_block)
);
```

#### dashboard_summaryテーブル（新規対応）
```sql
-- Dashboard Summary用テーブル (2025-09-11対応)
CREATE TABLE public.dashboard_summary (
    device_id UUID NOT NULL,
    date DATE NOT NULL,
    prompt JSONB NULL,               -- プロンプトデータ（JSONBフォーマット）
    processed_count INTEGER NULL,
    last_time_block VARCHAR(5) NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    average_vibe REAL NULL,
    insights JSONB NULL,
    analysis_result JSONB NULL,      -- ChatGPT分析結果（新エンドポイントで更新）
    vibe_scores JSONB NULL,
    PRIMARY KEY (device_id, date)
);
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

**EC2インスタンス情報:**
- IPアドレス: `3.24.16.82`
- ユーザー: `ubuntu`
- SSHキー: `~/watchme-key.pem`

#### 1. 必要なファイルをEC2サーバーにコピー

```bash
# プロジェクトディレクトリをEC2に作成
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82 "mkdir -p ~/api_gpt_v1"

# 必要なファイルをコピー（.envファイルも含む）
scp -i ~/watchme-key.pem \
  Dockerfile \
  docker-compose.yml \
  main.py \
  supabase_client.py \
  requirements.txt \
  README.md \
  .env \
  ubuntu@3.24.16.82:~/api_gpt_v1/
```

#### 2. EC2サーバーで環境設定

```bash
# EC2にSSH接続
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82

# api_gpt_v1ディレクトリに移動
cd ~/api_gpt_v1

# .envファイルがコピーされていることを確認
ls -la .env

# 必要に応じて.envファイルの内容を確認・修正
# 注意: .envファイルは手順1でコピー済みなので、APIキーは既に設定されています
cat .env
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
curl https://api.hey-watch.me/vibe-scorer/health

# Dockerコンテナの再起動
docker-compose restart

# 全体のリセット（データは保持）
docker-compose down && docker-compose up -d
```

## 📚 API エンドポイント

### 基本情報
- **本番環境URL**: `https://api.hey-watch.me/vibe-scorer`
- **本番環境URL**: `https://api.hey-watch.me/vibe-scorer`
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
  "timestamp": "2025-09-05T10:00:00.000000",
  "openai_model": "gpt-5-nano"
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

#### 本番環境
```bash
# 心理グラフ(VibeGraph)生成 - Supabase統合
curl -X POST https://api.hey-watch.me/vibe-scorer/analyze-vibegraph-supabase \
  -H "Content-Type: application/json" \
  -d '{"device_id": "d067d407-cf73-4174-a9c1-d91fb60d64d0", "date": "2025-07-14"}'

# 汎用ChatGPT中継
curl -X POST https://api.hey-watch.me/vibe-scorer/analyze/chatgpt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "あなたのプロンプトをここに入力"}'
```

#### 本番環境（外部URL）
```bash
# 心理グラフ(VibeGraph)生成 - Supabase統合
curl -X POST https://api.hey-watch.me/vibe-scorer/analyze-vibegraph-supabase \
  -H "Content-Type: application/json" \
  -d '{"device_id": "d067d407-cf73-4174-a9c1-d91fb60d64d0", "date": "2025-07-14"}'

# 汎用ChatGPT中継
curl -X POST https://api.hey-watch.me/vibe-scorer/analyze/chatgpt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "あなたのプロンプトをここに入力"}'
```

## 🔍 処理機能詳細

### 日付処理フロー（重要）
このAPIは音声ファイルの実際の記録日時を正確に保持するため、以下のフローで日付を処理します：

1. **API Managerからの日付受信**
   - `request.date`として検索用の日付を受け取る（必須パラメータ）
   - 例：`2025-07-31`

2. **データベース検索**
   - 受信した日付で`vibe_whisper_prompt`テーブルを検索
   - 該当するプロンプトデータを取得

3. **実データの日付を優先使用**
   - プロンプトデータに含まれる`date`フィールドを実際の日付として使用
   - これは音声ファイルのパス（例：`files/.../2025-07-31/14-30/audio.wav`）から抽出された真実の日付

4. **保存時の日付**
   - `vibe_whisper_summary`テーブルには実データの日付を保存
   - 検索日付と実データ日付が異なる場合は警告をログに記録

**重要**: 音声ファイルの記録時刻（ファイルパスに含まれる日付）が真実のデータとして扱われ、システム全体で一貫性が保たれます。

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

### 本番環境設定（EC2インスタンス: 3.24.16.82）
```bash
# 環境変数設定（.envファイルで管理）
OPENAI_API_KEY="実際のAPIキー"
SUPABASE_URL="https://qvtlwotzuzbavrzqhyvt.supabase.co"
SUPABASE_KEY="実際のSupabaseキー"
OPENAI_MODEL="gpt-5-nano"  # 必須: 使用するOpenAIモデルを指定

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

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🧪 テスト実績

### 2025年7月15日テスト結果（外部URL経由）

**テストデバイス**: `d067d407-cf73-4174-a9c1-d91fb60d64d0`

```bash
# ✅ 外部URL経由でのテスト
curl -X POST "https://api.hey-watch.me/vibe-scorer/analyze-vibegraph-supabase" \
  -H "Content-Type: application/json" \
  -d '{"device_id": "d067d407-cf73-4174-a9c1-d91fb60d64d0", "date": "2025-07-14"}'
# → 成功: vibe_whisper_summaryテーブルに保存
```

**処理結果**:
- 📊 処理時間: 約37秒（ChatGPT API呼び出し含む）
- 📊 感情スコア: 平均32.5（ポジティブ：2.0時間、ネガティブ：0.5時間、ニュートラル：45.5時間）
- ✅ データベース保存: 正常完了
- ✅ 構造バリデーション: 48個のスコア正常処理
- ✅ 外部アクセス: HTTPS経由で正常動作

### 2025年7月14日テスト結果（Supabase統合版）

**テストデバイス**: `d067d407-cf73-4174-a9c1-d91fb60d64d0`

```bash
# ✅ Supabase統合版テスト（EC2本番環境: 3.24.16.82）
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

## 🔗 マイクロサービス統合

### 外部サービスからの利用方法

```python
import requests
import asyncio
import aiohttp

# 同期版
def analyze_vibegraph(device_id: str, date: str):
    url = "https://api.hey-watch.me/vibe-scorer/analyze-vibegraph-supabase"
    data = {"device_id": device_id, "date": date}
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.text}")

# 非同期版
async def analyze_vibegraph_async(device_id: str, date: str):
    url = "https://api.hey-watch.me/vibe-scorer/analyze-vibegraph-supabase"
    data = {"device_id": device_id, "date": date}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"API Error: {await response.text()}")

# 使用例
result = analyze_vibegraph("d067d407-cf73-4174-a9c1-d91fb60d64d0", "2025-07-14")
print(result)
```

### 利用可能なエンドポイント

| エンドポイント | メソッド | 説明 | パラメータ |
|---------------|---------|------|-----------|
| `/health` | GET | ヘルスチェック | なし |
| `/analyze/chatgpt` | POST | ChatGPT中継 | `prompt` |
| `/analyze-vibegraph-supabase` | POST | VibeGraph生成 | `device_id`, `date` |
| `/docs` | GET | Swagger UI | なし |
| `/redoc` | GET | ReDoc | なし |

### APIドキュメント

- **Swagger UI**: `https://api.hey-watch.me/vibe-scorer/docs`
- **ReDoc**: `https://api.hey-watch.me/vibe-scorer/redoc`

### セキュリティ設定

- ✅ HTTPS対応（SSL証明書あり）
- ✅ CORS設定済み
- ✅ 適切なヘッダー設定
- ✅ レート制限対応（Nginxレベル）

---

**開発者**: WatchMe
**バージョン**: 3.1.0  