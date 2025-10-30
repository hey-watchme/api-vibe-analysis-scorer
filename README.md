# Vibe Scorer API(ChatGPT Gateway)

気分(Vibe)(心理グラフ)生成のためのChatGPT中継APIサービス

## 🌐 外部公開URL

**本番環境URL**: `https://api.hey-watch.me/vibe-analysis/scorer/`

- マイクロサービスとして外部から利用可能
- SSL/HTTPS対応
- CORS設定済み

## 🎯 概要

このAPIは、受け取ったPromptをChatGPTへと中継し、返ってきた値を心理グラフ(VibeGraph)の生成に使用するJSONへと変換するFastAPIベースのサービスです。Supabaseデータベースとの統合により、発話データから心理グラフ、気分スコアを生成します。

## 🗺️ ルーティング詳細

| 項目 | 値 | 説明 |
|------|-----|------|
| **🏷️ サービス名** | Vibe Scorer API | ChatGPT中継・心理グラフ生成 |
| **📦 機能** | LLM Gateway & Analysis | ChatGPT中継、心理グラフ(VibeGraph)生成 |
| | | |
| **🌐 外部アクセス（Nginx）** | | |
| └ 公開エンドポイント | `https://api.hey-watch.me/vibe-analysis/scorer/` | 外部公開URL |
| └ Nginx設定ファイル | `/etc/nginx/sites-available/api.hey-watch.me` | |
| └ proxy_pass先 | `http://localhost:8002/` | 内部転送先 |
| └ タイムアウト | 180秒 | read/connect/send |
| | | |
| **🔌 API内部エンドポイント** | | |
| └ ヘルスチェック | `/health` | GET - モデル情報含む |
| └ ルート情報 | `/` | GET - API情報表示 |
| └ ChatGPT中継 | `/analyze/chatgpt` | POST - 汎用LLM中継 |
| └ 心理グラフ生成 | `/analyze-vibegraph-supabase` | POST - 48タイムブロック統合 |
| └ タイムブロック分析 | `/analyze-timeblock` | POST - 30分単位分析 |
| └ ダッシュボードサマリー | `/analyze-dashboard-summary` | POST - 1日統合分析 |
| | | |
| **🐳 Docker/コンテナ** | | |
| └ コンテナ名 | `vibe-analysis-scorer` | `docker ps`で表示される名前 |
| └ ポート（内部） | 8002 | コンテナ内 |
| └ ポート（公開） | `127.0.0.1:8002:8002` | ローカルホストのみ |
| └ ヘルスチェック | `/health` | Docker healthcheck |
| | | |
| **☁️ AWS ECR** | | |
| └ リポジトリ名 | `watchme-vibe-analysis-scorer` | ECRリポジトリ |
| └ リージョン | ap-southeast-2 (Sydney) | |
| └ URI | `754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-vibe-analysis-scorer:latest` | |
| | | |
| **⚙️ systemd** | | |
| └ サービス名 | `vibe-analysis-scorer.service` | systemdサービス名 |
| └ 起動コマンド | `docker-compose up -d` | |
| └ 自動起動 | enabled | サーバー再起動時に自動起動 |
| | | |
| **📂 ディレクトリ** | | |
| └ ソースコード | `/Users/kaya.matsumoto/projects/watchme/api/vibe-analysis/scorer` | ローカル |
| └ GitHubリポジトリ | `hey-watchme/api-vibe-analysis-scorer` | |
| └ EC2配置場所 | Docker内部のみ（ディレクトリなし） | ECR経由デプロイ |
| | | |
| **🔗 呼び出し元** | | |
| └ プロンプト生成API | `api_gen-prompt_mood-chart_v1` | タイムブロック分析連携 |
| └ Dashboard | `watchme_v8` | 心理グラフ表示 |
| └ iOS App | `ios_watchme_v9` | モバイル連携 |

---

## 🤖 使用モデル情報

**現在使用中のAIモデル**: `gpt-5-nano`

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
# ヘルスチェック
curl https://api.hey-watch.me/vibe-analysis/scorer/health
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
curl -X POST https://api.hey-watch.me/vibe-analysis/scorer/analyze-timeblock \
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
curl -X POST https://api.hey-watch.me/vibe-analysis/scorer/analyze-dashboard-summary \
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
        "https://api.hey-watch.me/vibe-analysis/scorer/analyze-timeblock",
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

## 🚀 デプロイメント

### 🎯 CI/CD による自動デプロイ（推奨）

**2025年9月より、GitHub Actions による完全自動CI/CDパイプラインが稼働しています。**

#### ✨ デプロイ方法（超簡単！）

```bash
# 1. コードを修正
# 2. コミット＆プッシュするだけ！
git add .
git commit -m "feat: 新機能追加"
git push origin main

# 3. 自動デプロイ完了を待つ（約5分）
# GitHub Actions: https://github.com/matsumotokaya/watchme-api-whisper-gpt/actions
```

これだけです！mainブランチへのpushで自動的に以下が実行されます：
1. ARM64対応Dockerイメージのビルド
2. ECRへのプッシュ
3. EC2での自動デプロイ
4. ヘルスチェック

#### 📋 CI/CD 初期設定手順

他のAPIでも同様のCI/CDを導入する場合の設定手順：

##### 1. GitHub Secrets の設定

GitHubリポジトリの Settings > Secrets and variables > Actions で以下を設定：

| Secret名 | 説明 | 取得方法 |
|---------|------|---------|
| `AWS_ACCESS_KEY_ID` | AWS アクセスキー | AWS IAMコンソール or `cat ~/.aws/credentials` |
| `AWS_SECRET_ACCESS_KEY` | AWS シークレットキー | 同上 |
| `EC2_SSH_KEY` | EC2のSSH秘密鍵 | `cat ~/watchme-key.pem` の内容全体 |

**重要**: EC2_SSH_KEYは`-----BEGIN RSA PRIVATE KEY-----`から`-----END RSA PRIVATE KEY-----`まで全て含める

##### 2. ワークフローファイルの作成

`.github/workflows/deploy-ecr.yml` を作成（本リポジトリのものを参考に）

##### 3. 必要な調整項目

```yaml
env:
  AWS_REGION: ap-southeast-2  # リージョン
  ECR_REPOSITORY: watchme-vibe-analysis-scorer  # ECRリポジトリ名
  SERVICE_NAME: vibe-analysis-scorer  # systemdサービス名
```

#### ⚠️ ハマったポイントと解決策

1. **SSH接続エラー**
   - 問題：GitHub ActionsからEC2への接続で環境変数が渡らない
   - 解決：`webfactory/ssh-agent@v0.9.0`を使用し、known_hostsを明示的に追加

2. **ARM64アーキテクチャ対応**
   - 問題：EC2がARM64（t4g.small）だがイメージがAMD64
   - 解決：Docker Buildxを使用して`--platform linux/arm64`を指定

3. **ECRレジストリURL**
   - 問題：ハードコードされたURLでエラー
   - 解決：`${{ steps.login-ecr.outputs.registry }}`で動的に取得

4. **権限エラー**
   - 問題：ECRへのpush権限不足
   - 解決：IAMユーザーに`AmazonEC2ContainerRegistryPowerUser`ポリシーを付与

5. **ヘルスチェック失敗**
   - 問題：デプロイ直後にヘルスチェックが失敗
   - 解決：`sleep 5`で起動待機時間を設ける

### 🔧 手動デプロイ（CI/CDが使えない場合）

#### ローカルでのDocker実行

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

#### 手動での本番デプロイ

##### 1. ローカルでECRへデプロイ

```bash
# プロジェクトディレクトリに移動
cd /path/to/api_gpt_v1

# ECRへイメージをビルド＆プッシュ
./deploy-ecr.sh
```

このスクリプトは以下を自動で実行します：
- ECRへのログイン
- Dockerイメージのビルド（Dockerfile.prod使用）
- イメージのタグ付け
- ECRへのプッシュ

##### 2. EC2サーバーでサービス再起動

```bash
# 既存のコンテナが残っている場合は削除
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82 "docker rm -f vibe-analysis-scorer"

# systemdサービスを再起動
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82 "sudo systemctl restart vibe-analysis-scorer"

# ステータス確認
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82 "sudo systemctl status vibe-analysis-scorer"
```

##### 3. 動作確認

```bash
# ヘルスチェック（外部URL）
curl https://api.hey-watch.me/vibe-analysis/scorer/health

# 期待されるレスポンス
# {"status":"healthy","timestamp":"2025-09-15T23:49:51.000343","openai_model":"gpt-5-nano"}
```

### 📋 インフラ情報

#### ECR（Elastic Container Registry）
- **レジストリ**: `754724220380.dkr.ecr.ap-southeast-2.amazonaws.com`
- **リポジトリ**: `watchme-vibe-analysis-scorer`
- **イメージURI**: `754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-vibe-analysis-scorer:latest`

#### EC2
- **ホスト**: 3.24.16.82
- **ユーザー**: ubuntu
- **アーキテクチャ**: ARM64 (t4g.small)
- **ポート**: 8002（内部）
- **外部URL**: https://api.hey-watch.me/vibe-analysis/scorer/

### 🔧 トラブルシューティング

#### CI/CD関連

##### GitHub Actions が失敗する場合

1. **Actions タブで詳細を確認**
   ```
   https://github.com/matsumotokaya/watchme-api-whisper-gpt/actions
   ```

2. **よくあるエラーと対処法**
   - `invalid reference format`: Dockerfile.prodが存在するか確認
   - `no basic auth credentials`: AWS認証情報のSecretsを確認
   - `Permission denied (publickey)`: EC2_SSH_KEYが正しく設定されているか確認
   - `exec format error`: ARM64用のイメージがビルドされているか確認

3. **手動での動作確認**
   ```bash
   # ローカルでDockerイメージをビルド
   docker build -f Dockerfile.prod -t test-api .
   
   # ARM64向けビルドのテスト
   docker buildx build --platform linux/arm64 -f Dockerfile.prod -t test-api .
   ```

#### サービス関連

```bash
# サービスログの確認
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82 "sudo journalctl -u vibe-analysis-scorer -n 50"

# Dockerコンテナのログ確認
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82 "docker logs vibe-analysis-scorer --tail 50"

# コンテナの状態確認
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82 "docker ps | grep vibe-analysis-scorer"

# systemd サービスの再起動
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82 "sudo systemctl restart vibe-analysis-scorer"

# ECRから手動でイメージをプル
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82 "aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 754724220380.dkr.ecr.ap-southeast-2.amazonaws.com && docker pull 754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-vibe-analysis-scorer:latest"
```

### 📝 移行ガイド（他のAPIをCI/CD化する場合）

#### Step 1: 必要なファイルの準備
- [ ] `Dockerfile.prod` が存在することを確認
- [ ] `.github/workflows/deploy-ecr.yml` をコピーして修正
- [ ] ECRリポジトリが作成済みであることを確認

#### Step 2: GitHub Secrets の設定
- [ ] AWS_ACCESS_KEY_ID
- [ ] AWS_SECRET_ACCESS_KEY  
- [ ] EC2_SSH_KEY

#### Step 3: ワークフローのカスタマイズ
```yaml
# 以下を各APIに合わせて変更
env:
  ECR_REPOSITORY: your-api-name  # ECRリポジトリ名
  SERVICE_NAME: your-service-name  # systemdサービス名
```

#### Step 4: systemd設定の確認
EC2上でサービスが設定済みであることを確認：
```bash
sudo systemctl status your-service-name
```

#### Step 5: テストデプロイ
mainブランチにプッシュして動作確認：
```bash
git push origin main
# GitHub Actions を確認
```

## 🔧 systemd による自動起動設定

このサービスは **watchme-server-configs** リポジトリで一元管理されています。

### systemdサービス情報

- **サービス名**: `vibe-analysis-scorer.service`
- **設定ファイル**: `/home/ubuntu/watchme-server-configs/docker-compose-files/vibe-analysis-scorer-docker-compose.prod.yml`
- **自動起動**: 有効（EC2再起動時に自動起動）

### サービス管理コマンド

```bash
# サービスの状態確認
sudo systemctl status vibe-analysis-scorer

# サービスの再起動
sudo systemctl restart vibe-analysis-scorer

# サービスの停止
sudo systemctl stop vibe-analysis-scorer

# サービスの開始
sudo systemctl start vibe-analysis-scorer

# ログの確認（リアルタイム）
sudo journalctl -u vibe-analysis-scorer -f
```

## 📊 運用管理

### 監視とトラブルシューティング

```bash
# コンテナの状態確認
docker ps | grep api-gpt

# ポート使用状況の確認
sudo lsof -i :8002

# APIヘルスチェック
curl https://api.hey-watch.me/vibe-analysis/scorer/health

# ECRから最新イメージを取得
aws ecr get-login-password --region ap-southeast-2 | \
  docker login --username AWS --password-stdin \
  754724220380.dkr.ecr.ap-southeast-2.amazonaws.com

docker pull 754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-vibe-analysis-scorer:latest
```

## 📚 API エンドポイント

### 基本情報
- **本番環境URL**: `https://api.hey-watch.me/vibe-analysis/scorer`
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

```bash
# 心理グラフ(VibeGraph)生成 - Supabase統合
curl -X POST https://api.hey-watch.me/vibe-analysis/scorer/analyze-vibegraph-supabase \
  -H "Content-Type: application/json" \
  -d '{"device_id": "d067d407-cf73-4174-a9c1-d91fb60d64d0", "date": "2025-07-14"}'

# 汎用ChatGPT中継
curl -X POST https://api.hey-watch.me/vibe-analysis/scorer/analyze/chatgpt \
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

### 本番環境情報

- **EC2インスタンス**: 3.24.16.82
- **外部URL**: https://api.hey-watch.me/vibe-analysis/scorer/
- **内部ポート**: 8002
- **コンテナ管理**: AWS ECR + systemd

### 環境変数設定（.envファイル）

```bash
OPENAI_API_KEY="実際のAPIキー"
SUPABASE_URL="https://qvtlwotzuzbavrzqhyvt.supabase.co"
SUPABASE_KEY="実際のSupabaseキー"
OPENAI_MODEL="gpt-5-nano"  # 必須: 使用するOpenAIモデルを指定
```

デプロイ手順は[本番環境（EC2）へのデプロイ](#本番環境ec2へのデプロイ)セクションを参照してください。

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


## 🔗 マイクロサービス統合

### 外部サービスからの利用方法

```python
import requests
import asyncio
import aiohttp

# 同期版
def analyze_vibegraph(device_id: str, date: str):
    url = "https://api.hey-watch.me/vibe-analysis/scorer/analyze-vibegraph-supabase"
    data = {"device_id": device_id, "date": date}
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.text}")

# 非同期版
async def analyze_vibegraph_async(device_id: str, date: str):
    url = "https://api.hey-watch.me/vibe-analysis/scorer/analyze-vibegraph-supabase"
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

- **Swagger UI**: `https://api.hey-watch.me/vibe-analysis/scorer/docs`
- **ReDoc**: `https://api.hey-watch.me/vibe-analysis/scorer/redoc`

### セキュリティ設定

- ✅ HTTPS対応（SSL証明書あり）
- ✅ CORS設定済み
- ✅ 適切なヘッダー設定
- ✅ レート制限対応（Nginxレベル）

---

**開発者**: WatchMe
**バージョン**: 3.1.0  