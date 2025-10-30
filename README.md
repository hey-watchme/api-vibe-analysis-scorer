# Vibe Scorer API

気分(Vibe)分析のためのLLM中継APIサービス

## 🌐 本番環境

**URL**: `https://api.hey-watch.me/vibe-analysis/scorer/`

- マイクロサービスとして外部から利用可能
- SSL/HTTPS対応、CORS設定済み
- Docker + ECR + systemd で運用

---

## 🎯 概要

このAPIは、プロンプトをLLM（OpenAI、Groq等）に中継し、返ってきた値をJSON形式に変換してSupabaseデータベースに保存するFastAPIベースのサービスです。

### 主要機能

- **タイムブロック分析**: 30分単位の感情分析（`/analyze-timeblock`）
- **Dashboard Summary分析**: 1日統合分析（`/analyze-dashboard-summary`）
- **複数LLMプロバイダー対応**: OpenAI、Groq等を簡単に切り替え可能
- **リトライ機能**: API呼び出しの安定性確保
- **NaN値処理**: 欠損データの適切な処理

---

## 🗺️ インフラ構成

| 項目 | 値 |
|------|-----|
| **外部URL** | `https://api.hey-watch.me/vibe-analysis/scorer/` |
| **内部ポート** | 8002 |
| **Nginx設定** | `/etc/nginx/sites-available/api.hey-watch.me` |
| **タイムアウト** | 180秒 |
| **コンテナ名** | `vibe-analysis-scorer` |
| **systemdサービス** | `vibe-analysis-scorer.service` |
| **ECRリポジトリ** | `watchme-vibe-analysis-scorer` |
| **リージョン** | ap-southeast-2 (Sydney) |
| **EC2** | 3.24.16.82 (ARM64 / t4g.small) |
| **GitHubリポジトリ** | `hey-watchme/api-vibe-analysis-scorer` |

---

## 🤖 LLMプロバイダー設定

### 設計コンセプト

このAPIは**複数のLLMプロバイダーに対応**し、簡単に切り替えられる設計になっています。

**目的**:
- 新しいモデルへの迅速な移行
- コスト最適化（プロバイダーごとに価格が異なる）
- パフォーマンス不良時の即座の切り戻し
- 複数のモデルを事前準備（APIキー設定済み、いつでも切り替え可能）

**特徴**:
- ✅ クライアント側（アプリ・他のAPI）の変更は不要
- ✅ コード1行変更 → git push で切り替え完了
- ✅ 3-5種類のプロバイダーを待機状態で保持可能
- ✅ モデルバージョンアップも同じ手順

### 現在使用中

- プロバイダー: **OpenAI**
- モデル: **gpt-5-nano**

### 対応プロバイダー

| プロバイダー | 対応モデル例 | 環境変数 | 状態 |
|------------|------------|---------|------|
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-5-nano, o1-preview | OPENAI_API_KEY | ✅ 設定済み |
| **Groq** | llama-3.1-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768 | GROQ_API_KEY | ⚠️ 要設定 |

### プロバイダー切り替え方法

#### OpenAI → Groq に切り替える場合

**ステップ1: Groq APIキーの準備**

1. Groq APIキーを取得: https://console.groq.com/
2. GitHub Secretsに追加:
   - リポジトリの Settings > Secrets and variables > Actions
   - New repository secret: `GROQ_API_KEY` = `gsk-...`

3. CI/CDワークフローを更新（`.github/workflows/deploy-to-ecr.yml`）:

```yaml
# "Create/Update .env file on EC2" ステップに追加
- name: Create/Update .env file on EC2
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}  # ← 追加
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
  run: |
    ssh ${EC2_USER}@${EC2_HOST} << ENDSSH
      cd /home/ubuntu/vibe-analysis-scorer
      echo "OPENAI_API_KEY=${OPENAI_API_KEY}" > .env
      echo "GROQ_API_KEY=${GROQ_API_KEY}" >> .env  # ← 追加
      echo "SUPABASE_URL=${SUPABASE_URL}" >> .env
      echo "SUPABASE_KEY=${SUPABASE_KEY}" >> .env
    ENDSSH
```

**ステップ2: プロバイダーを切り替え**

```bash
# llm_providers.py を編集
vi llm_providers.py
```

変更内容：
```python
# 変更前
CURRENT_PROVIDER = "openai"
CURRENT_MODEL = "gpt-5-nano"

# 変更後
CURRENT_PROVIDER = "groq"
CURRENT_MODEL = "llama-3.1-70b-versatile"
```

**ステップ3: デプロイ**

```bash
git add llm_providers.py .github/workflows/deploy-to-ecr.yml
git commit -m "feat: Switch to Groq llama-3.1-70b"
git push origin main

# CI/CDが自動実行（約5分）
```

**ステップ4: 動作確認**

```bash
# ヘルスチェックでモデルを確認
curl https://api.hey-watch.me/vibe-analysis/scorer/health

# レスポンス例
# {
#   "status": "healthy",
#   "llm_provider": "groq",  ← 変わっている
#   "llm_model": "llama-3.1-70b-versatile"
# }
```

#### モデルバージョンアップの場合（同じプロバイダー内）

APIキー設定は不要。llm_providers.pyのモデル名だけ変更：

```python
# 例：gpt-5-nano → gpt-5-nano-2025-11 にアップグレード
CURRENT_PROVIDER = "openai"  # プロバイダーはそのまま
CURRENT_MODEL = "gpt-5-nano-2025-11"  # モデル名だけ変更
```

#### 切り戻し（Groq → OpenAI に戻す）

```python
# llm_providers.py
CURRENT_PROVIDER = "openai"  # 1行変更
CURRENT_MODEL = "gpt-5-nano"
```

git push するだけで即座に戻ります。

---

## 📌 APIエンドポイント

### アクティブなエンドポイント

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/health` | GET | ヘルスチェック |
| `/analyze-timeblock` | POST | タイムブロック分析（30分単位） |
| `/analyze-dashboard-summary` | POST | Dashboard Summary分析（1日統合） |

### 非推奨エンドポイント（現在使用していません）

| エンドポイント | 説明 |
|--------------|------|
| `/analyze/chatgpt` | 汎用ChatGPT中継 |
| `/analyze-vibegraph-supabase` | 心理グラフ生成（48タイムブロック） |

---

## 🔌 エンドポイント詳細

### 1. ヘルスチェック

```bash
curl https://api.hey-watch.me/vibe-analysis/scorer/health
```

**レスポンス:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-30T12:00:00.000000",
  "llm_provider": "openai",
  "llm_model": "gpt-5-nano"
}
```

### 2. タイムブロック分析

```bash
curl -X POST https://api.hey-watch.me/vibe-analysis/scorer/analyze-timeblock \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "分析用プロンプト",
    "device_id": "uuid",
    "date": "2025-10-30",
    "time_block": "14-00"
  }'
```

**レスポンス:**
```json
{
  "status": "success",
  "message": "タイムブロック分析が完了しました（DB保存成功）",
  "device_id": "uuid",
  "date": "2025-10-30",
  "time_block": "14-00",
  "analysis_result": {
    "summary": "30分間の状況説明",
    "vibe_score": -30,
    "behavior": "作業中"
  },
  "database_save": true,
  "processed_at": "2025-10-30T14:30:00.000Z",
  "model_used": "openai/gpt-5-nano"
}
```

### 3. Dashboard Summary分析

```bash
curl -X POST https://api.hey-watch.me/vibe-analysis/scorer/analyze-dashboard-summary \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "uuid",
    "date": "2025-10-30"
  }'
```

**レスポンス:**
```json
{
  "status": "success",
  "message": "Dashboard Summary分析が完了しました",
  "device_id": "uuid",
  "date": "2025-10-30",
  "database_save": true,
  "processed_at": "2025-10-30T17:00:00.000000",
  "model_used": "openai/gpt-5-nano",
  "analysis_result": {
    "cumulative_evaluation": "1日の総合評価",
    "mood_trajectory": "positive_trend",
    "current_state_score": 36
  }
}
```

---

## 📊 データベース構造

### dashboardテーブル

タイムブロック分析結果を保存

```sql
CREATE TABLE public.dashboard (
    device_id UUID NOT NULL,
    date DATE NOT NULL,
    time_block VARCHAR(5) NOT NULL,
    prompt TEXT,
    summary TEXT,
    behavior TEXT,
    vibe_score DOUBLE PRECISION,
    analysis_result JSONB,
    status VARCHAR(20),
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (device_id, date, time_block)
);
```

### dashboard_summaryテーブル

Dashboard Summary分析結果を保存

```sql
CREATE TABLE public.dashboard_summary (
    device_id UUID NOT NULL,
    date DATE NOT NULL,
    prompt JSONB NULL,
    processed_count INTEGER NULL,
    last_time_block VARCHAR(5) NULL,
    average_vibe REAL NULL,
    insights JSONB NULL,
    analysis_result JSONB NULL,
    vibe_scores JSONB NULL,
    burst_events JSONB NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (device_id, date)
);
```

---

## 🚀 デプロイ

### CI/CDによる自動デプロイ

```bash
# コミット＆プッシュするだけで自動デプロイ
git add .
git commit -m "feat: 新機能追加"
git push origin main

# GitHub Actionsが自動実行（約5分）
# https://github.com/hey-watchme/api-vibe-analysis-scorer/actions
```

**自動実行内容:**
1. ARM64対応Dockerイメージのビルド
2. ECRへのプッシュ
3. EC2での自動デプロイ
4. ヘルスチェック

### サービス管理コマンド（EC2）

```bash
# サービスの状態確認
sudo systemctl status vibe-analysis-scorer

# サービスの再起動
sudo systemctl restart vibe-analysis-scorer

# ログ確認
sudo journalctl -u vibe-analysis-scorer -f
docker logs vibe-analysis-scorer --tail 50
```

---

## 🔧 環境変数（.env）

```bash
# LLM APIキー
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk-...  # Groq使用時のみ

# Supabase設定
SUPABASE_URL=https://qvtlwotzuzbavrzqhyvt.supabase.co
SUPABASE_KEY=your-supabase-key
```

**注意**: モデルの指定は `llm_providers.py` で行います（環境変数ではありません）。

---

## 📦 依存関係

```txt
fastapi==0.100.0
uvicorn==0.23.0
pydantic==2.0.2
python-dotenv==1.0.0
openai>=1.0.0
groq>=0.4.0
requests>=2.31.0
python-multipart>=0.0.6
aiohttp>=3.8.0
tenacity>=8.2.0
httpx==0.24.1
gotrue==1.3.0
supabase==2.3.4
```

---

## 🔗 連携サービス

- **プロンプト生成API**: `api_gen-prompt_mood-chart_v1`
- **Dashboard**: `watchme_v8`
- **iOS App**: `ios_watchme_v9`

---

## 📚 APIドキュメント

- **Swagger UI**: https://api.hey-watch.me/vibe-analysis/scorer/docs
- **ReDoc**: https://api.hey-watch.me/vibe-analysis/scorer/redoc

---

**開発者**: WatchMe
**バージョン**: 3.2.0
