# ChatGPT Gateway API 仕様書

## 📋 基本情報

| 項目 | 値 |
|------|-----|
| **API名** | ChatGPT Gateway API |
| **バージョン** | 1.0.0 |
| **ベースURL** | `http://localhost:8002` |
| **プロトコル** | HTTP/HTTPS |
| **認証方式** | 環境変数（OpenAI APIキー） |
| **レスポンス形式** | JSON |
| **文字エンコーディング** | UTF-8 |

## 🎯 API概要

ChatGPT Gateway APIは、OpenAI ChatGPTとの中継機能と感情分析処理機能を提供するRESTful APIです。ローカル開発環境とEC2クラウド環境の両方に対応し、音声転写データから感情タイムラインを自動生成します。

### 主要機能
- ChatGPTプロンプト中継
- 感情分析処理（ローカル・EC2連携）
- ファイルベースデータ処理
- 自動リトライ機能
- データバリデーション

## 🔧 環境設定

### 必須環境変数
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### オプション環境変数
```bash
# OpenAIモデル指定（デフォルト: gpt-4）
OPENAI_MODEL=gpt-4

# 動作モード設定（デフォルト: https://api.hey-watch.me）
EC2_BASE_URL=local                    # ローカルモード
EC2_BASE_URL=https://api.hey-watch.me # EC2連携モード
```

## 📚 エンドポイント仕様

### 1. ヘルスチェック

```http
GET /health
```

**説明**: APIサーバーの稼働状況と設定情報を取得

**パラメータ**: なし

**レスポンス**:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-15T22:12:46.919978",
  "mode": "ec2",
  "ec2_base_url": "https://api.hey-watch.me",
  "openai_model": "gpt-4"
}
```

**ステータスコード**:
- `200`: 正常

---

### 2. ChatGPT中継

```http
POST /analyze/chatgpt
```

**説明**: 任意のプロンプトをChatGPT APIに中継し、JSON形式で応答を返却

**リクエストボディ**:
```json
{
  "prompt": "string (required) - ChatGPTに送信するプロンプト"
}
```

**レスポンス**: ChatGPTからの応答をJSON形式で返却

**ステータスコード**:
- `200`: 正常処理完了
- `400`: リクエスト形式エラー
- `500`: ChatGPT API エラー

---

### 3. ローカル感情分析

```http
POST /analyze-mood
```

**説明**: ローカルファイルシステムから感情分析を実行

**リクエストボディ**:
```json
{
  "user_id": "string (required) - ユーザーID",
  "date": "string (optional) - 分析対象日 (YYYY-MM-DD形式、デフォルト: 今日)"
}
```

**処理フロー**:
1. ローカルプロンプトファイル読み込み
2. ChatGPT API呼び出し
3. 構造バリデーション
4. ローカルファイル保存

**ファイルパス**:
- 入力: `/Users/kaya.matsumoto/data/data_accounts/{user_id}/{date}/prompt/emotion-timeline_gpt_prompt.json`
- 出力: `/Users/kaya.matsumoto/data/data_accounts/{user_id}/{date}/emotion-timeline/emotion-timeline.json`

**レスポンス**:
```json
{
  "status": "success",
  "message": "ローカル感情分析処理が完了しました",
  "user_id": "user123",
  "date": "2025-06-15",
  "local_file": "/path/to/local/emotion-timeline.json",
  "processed_at": "2025-06-15T22:24:17.516853",
  "processing_log": {
    "start_time": "2025-06-15T22:24:00.000000",
    "mode": "local",
    "processing_steps": [
      "ローカルファイルパス構築完了",
      "プロンプトファイル存在確認完了",
      "プロンプトファイル読み込み完了",
      "ChatGPT処理完了",
      "構造バリデーション完了",
      "ローカル保存完了"
    ],
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

**ステータスコード**:
- `200`: 正常処理完了
- `404`: プロンプトファイルが見つからない
- `500`: 処理エラー

---

### 4. EC2連携感情分析 ⭐

```http
POST /analyze-mood-ec2
```

**説明**: EC2サーバーからプロンプトを取得し、処理後にEC2にアップロード

**リクエストボディ**:
```json
{
  "user_id": "string (required) - ユーザーID",
  "date": "string (optional) - 分析対象日 (YYYY-MM-DD形式、デフォルト: 今日)"
}
```

**処理フロー**:
1. EC2からプロンプト取得: `GET {EC2_BASE_URL}/status/{user_id}/{date}/prompt/emotion-timeline_gpt_prompt.json`
2. ChatGPT API呼び出し（リトライ機能付き）
3. 構造バリデーション
4. ローカル保存
5. EC2アップロード: `POST {EC2_BASE_URL}/upload/analysis/emotion-timeline`

**レスポンス**:
```json
{
  "status": "success",
  "message": "EC2連携感情分析処理が完了しました",
  "user_id": "user123",
  "date": "2025-06-15",
  "local_file": "/path/to/local/emotion-timeline.json",
  "ec2_upload": true,
  "processed_at": "2025-06-15T22:53:08.130876",
  "processing_log": {
    "start_time": "2025-06-15T22:24:20.000000",
    "mode": "ec2",
    "ec2_base_url": "https://api.hey-watch.me",
    "processing_steps": [
      "プロンプト取得完了",
      "ChatGPT処理完了",
      "構造バリデーション完了",
      "ローカル保存完了",
      "EC2アップロード完了"
    ],
    "complete": true,
    "warnings": []
  },
  "validation_summary": {
    "total_warnings": 0,
    "structure_valid": true,
    "nan_handling": "completed"
  }
}
```

**ステータスコード**:
- `200`: 正常処理完了（EC2アップロード成功/失敗問わず）
- `404`: プロンプトファイルが見つからない
- `500`: 処理エラー

---

### 5. 感情分析処理（従来版）

```http
POST /process/emotion-timeline
```

**説明**: 従来のディレクトリ構造での感情分析処理（後方互換性）

**リクエストボディ**:
```json
{
  "username": "string (optional) - ユーザー名 (デフォルト: user123)",
  "date": "string (optional) - 分析対象日 (YYYY-MM-DD形式、デフォルト: 今日)"
}
```

**ファイルパス**:
- 入力: `/Users/kaya.matsumoto/data/data_accounts/{username}/{date}/transcriptions/emotion-timeline_gpt_prompt.json`
- 出力: `/Users/kaya.matsumoto/data/data_accounts/{username}/{date}/emotion-timeline.json`

---

### 6. EC2接続デバッグ

```http
GET /debug-ec2-connection
```

**説明**: EC2接続状況をテストし、デバッグ情報を提供

**パラメータ**: なし

**レスポンス**:
```json
{
  "timestamp": "2025-06-15T22:12:56.674453",
  "environment": {
    "EC2_BASE_URL": "https://api.hey-watch.me",
    "mode": "ec2",
    "OPENAI_MODEL": "gpt-4",
    "has_openai_key": true
  },
  "tests": [
    {
      "test": "ec2_health_check",
      "url": "https://api.hey-watch.me/health",
      "status": 404,
      "success": false,
      "response": null
    }
  ]
}
```

**ステータスコード**:
- `200`: 正常（接続テスト結果は`tests`配列内で確認）

## 📊 データ形式仕様

### 感情分析結果フォーマット

```json
{
  "timePoints": [
    "00:00", "00:30", "01:00", ..., "23:30"
  ],
  "emotionScores": [
    0, 15, 25, 30, 75, 80, 40, ..., 0
  ],
  "averageScore": 15.2,
  "positiveHours": 18.0,
  "negativeHours": 2.0,
  "neutralHours": 28.0,
  "insights": [
    "午前中は静かな状態が続いた",
    "午後は感情の変動が少なかった",
    "全体として安定した心理状態"
  ],
  "emotionChanges": [
    {
      "time": "09:00",
      "event": "ポジティブな変化",
      "score": 75
    }
  ],
  "date": "2025-06-15",
  "processed_at": "2025-06-15T22:53:08.130876",
  "processing_log": { ... }
}
```

### フィールド仕様

| フィールド | 型 | 説明 | 制約 |
|------------|----|----|------|
| `timePoints` | Array[String] | 48個の時間ポイント | "00:00"〜"23:30"、30分間隔 |
| `emotionScores` | Array[Number] | 48個の感情スコア | -100〜+100の整数値、NaN可 |
| `averageScore` | Number | 平均感情スコア | NaN値除外して計算 |
| `positiveHours` | Number | ポジティブ感情の時間数 | 0.5時間単位 |
| `negativeHours` | Number | ネガティブ感情の時間数 | 0.5時間単位 |
| `neutralHours` | Number | 中立感情の時間数 | 0.5時間単位 |
| `insights` | Array[String] | 感情的・心理的傾向の分析 | 3件程度 |
| `emotionChanges` | Array[Object] | 感情の大きな変化 | 最大3件程度 |
| `date` | String | 分析対象日 | "YYYY-MM-DD"形式 |

## ⚠️ エラーハンドリング

### HTTPステータスコード

| コード | 説明 | 対応 |
|--------|------|------|
| `200` | 成功 | - |
| `400` | リクエストエラー | リクエスト形式を確認 |
| `404` | リソースが見つからない | ファイルパスやパラメータを確認 |
| `500` | サーバー内部エラー | ログを確認、再試行 |

### エラーレスポンス形式

```json
{
  "detail": "エラーメッセージの詳細"
}
```

### 一般的なエラー例

```json
// ファイルが見つからない場合
{
  "detail": "プロンプトファイルが見つかりません: /path/to/file.json"
}

// リクエスト形式エラー
{
  "detail": "プロンプトファイルに'prompt'フィールドが見つかりません"
}

// ChatGPT APIエラー
{
  "detail": "ChatGPT APIでエラーが発生しました: API rate limit exceeded"
}
```

## 🔍 高度な機能

### JSON抽出処理

ChatGPTの応答から以下の順序でJSONを抽出：

1. **応答全体がJSON形式**: `json.loads(content)`
2. **コードブロック形式**: ````json ... ```` パターンを正規表現で抽出
3. **JSONブロック形式**: `{ ... }` パターンを正規表現で抽出

### NaN値処理

- 文字列 `"NaN"` を `float('nan')` に自動変換
- 再帰的なデータ構造処理に対応
- 平均値計算時にNaN値を除外

### 構造バリデーション

- `emotionScores`が48個未満の場合、NaNで自動補完
- `averageScore`の再計算（有効値のみ使用）
- データ整合性の自動チェック

### リトライ機能

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(Exception)
)
```

- 最大3回まで指数バックオフ付きリトライ
- レート制限（429エラー）に対応
- 安定した処理の実現

## 🔐 セキュリティ仕様

### 認証・認可
- OpenAI APIキーは環境変数で管理
- APIキー情報はレスポンスに含めない
- 入力データのバリデーション実施

### 通信セキュリティ
- EC2連携時はHTTPS通信
- SSL証明書検証（本番環境）
- タイムアウト設定（10秒）

### データ保護
- 個人情報の適切な処理
- ログ出力時の機密情報マスキング
- エラー情報の適切な制限

## 📈 パフォーマンス仕様

### レスポンス時間
- ヘルスチェック: < 100ms
- ChatGPT中継: 5-30秒（OpenAI API依存）
- 感情分析処理: 15-60秒（ChatGPT処理時間含む）

### 同時接続数
- 推奨: 10接続以下
- OpenAI APIの制限に依存

### ファイルサイズ制限
- プロンプトファイル: 最大10MB
- 出力ファイル: 最大5MB

## 🧪 テスト仕様

### 単体テスト
```bash
python test_mood_analysis.py      # 全エンドポイントテスト
python test_ec2_mode.py          # EC2連携専用テスト
```

### 統合テスト
```bash
./test_mood_analysis.sh          # シェルスクリプト実行
```

### 手動テスト例
```bash
# ヘルスチェック
curl -X GET http://localhost:8002/health

# ChatGPT中継
curl -X POST http://localhost:8002/analyze/chatgpt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, ChatGPT!"}'

# EC2連携感情分析
curl -X POST http://localhost:8002/analyze-mood-ec2 \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "date": "2025-06-15"}'
```

## 📝 ログ仕様

### 処理ログ
```json
{
  "start_time": "2025-06-15T22:24:00.000000",
  "mode": "ec2",
  "processing_steps": [
    "プロンプト取得完了",
    "ChatGPT処理完了",
    "構造バリデーション完了",
    "ローカル保存完了",
    "EC2アップロード完了"
  ],
  "complete": true,
  "warnings": [],
  "end_time": "2025-06-15T22:24:30.000000"
}
```

### バリデーション情報
```json
{
  "original_score_count": 48,
  "expected_score_count": 48,
  "score_length_warning": false,
  "missing_scores_filled": 0,
  "nan_scores_detected": 0,
  "average_calculated_from": 48
}
```

## 🚀 デプロイ仕様

### 本番環境要件
- Python 3.11+
- メモリ: 最小512MB、推奨1GB
- ディスク: 最小1GB、推奨5GB
- ネットワーク: HTTPS対応

### 環境変数（本番）
```bash
OPENAI_API_KEY=sk-prod-key-here
EC2_BASE_URL=https://api.hey-watch.me
OPENAI_MODEL=gpt-4
```

### 起動コマンド（本番）
```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --workers 4
```

## 📋 変更履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2025-06-15 | 初回リリース、EC2連携機能追加 |

---

**文書作成者**: ChatGPT Gateway API Team  
**最終更新**: 2025-06-15  
**文書バージョン**: 1.0.0 