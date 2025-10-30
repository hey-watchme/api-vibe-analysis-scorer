# LLMプロバイダー切り替え機能実装計画

**作成日**: 2025-10-30
**目的**: 複数のLLMプロバイダー（OpenAI、Groq等）を柔軟に切り替えられる構造に移行

---

## 🎯 背景・目的

### なぜこの機能が必要か

1. **LLMの進化が速い**
   - 新しいモデルが頻繁にリリースされる
   - より高性能・低コストなモデルに素早く切り替えたい

2. **コスト最適化**
   - プロバイダーごとに価格が異なる
   - 用途によって最適なモデルを選択したい

3. **A/Bテスト・比較検証**
   - 複数のモデルで品質・速度・コストを比較したい
   - 段階的な移行が必要

---

## 📊 現状

### 現在の実装（2025-10-30時点）

- **単一プロバイダー**: OpenAI固定
- **現在使用中のモデル**: `gpt-5-nano`
- **環境変数**: `OPENAI_MODEL`で指定
- **問題点**: プロバイダー変更には大規模なコード修正が必要

```python
# main.py（現状）
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL")  # gpt-5-nano

# 各エンドポイントで直接呼び出し
response = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=[{"role": "user", "content": prompt}]
)
```

---

## 🎯 目標アーキテクチャ

### 設計方針

**推奨アプローチ**: 単一API内でプロバイダー切り替え（Factory Pattern）

**メリット**:
- コードの重複を避けられる
- 1つのデプロイで全プロバイダーを管理
- リクエスト時にモデルを指定できるので柔軟
- A/Bテストや比較が容易

---

## 🏗️ 実装設計

### 1. プロバイダー抽象化レイヤー

```
api/vibe-analysis/scorer/
├── main.py
├── llm_providers.py          # 新規作成
│   ├── LLMProvider (抽象クラス)
│   ├── OpenAIProvider
│   ├── GroqProvider
│   └── LLMFactory
├── supabase_client.py
└── requirements.txt           # groq依存関係追加
```

### 2. クラス構造（llm_providers.py）

```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """LLMプロバイダーの抽象クラス"""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._model = model

    async def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    @property
    def model_name(self) -> str:
        return f"openai/{self._model}"

class GroqProvider(LLMProvider):
    def __init__(self, model: str = "llama-3.1-70b-versatile"):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self._model = model

    async def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    @property
    def model_name(self) -> str:
        return f"groq/{self._model}"

class LLMFactory:
    """LLMプロバイダーのファクトリークラス"""

    @staticmethod
    def create(provider: str, model: str = None) -> LLMProvider:
        if provider == "openai":
            return OpenAIProvider(model or "gpt-4")
        elif provider == "groq":
            return GroqProvider(model or "llama-3.1-70b-versatile")
        else:
            raise ValueError(f"Unknown provider: {provider}")

    @staticmethod
    def get_default() -> LLMProvider:
        """環境変数から読み込み"""
        provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4")
        return LLMFactory.create(provider, model)
```

### 3. リクエストスキーマ拡張

```python
# main.py
class PromptRequest(BaseModel):
    prompt: str
    model_provider: Optional[str] = None  # "openai", "groq"
    model_name: Optional[str] = None      # "gpt-4", "llama-3.1-70b-versatile"

class TimeBlockAnalysisRequest(BaseModel):
    prompt: str
    device_id: Optional[str] = None
    date: Optional[str] = None
    time_block: Optional[str] = None
    model_provider: Optional[str] = None  # 追加
    model_name: Optional[str] = None      # 追加
```

### 4. エンドポイント修正例

```python
@app.post("/analyze/chatgpt")
async def relay_to_llm(request: PromptRequest):
    """プロンプトをLLMに中継（プロバイダー選択可能）"""
    try:
        # プロバイダーの選択
        if request.model_provider and request.model_name:
            llm = LLMFactory.create(request.model_provider, request.model_name)
        elif request.model_provider:
            llm = LLMFactory.create(request.model_provider)
        else:
            llm = LLMFactory.get_default()

        print(f"🤖 使用モデル: {llm.model_name}")

        # LLM呼び出し
        raw_response = await llm.generate(request.prompt)

        # JSON抽出処理（既存のロジック）
        extracted_data = extract_json_from_response(raw_response)
        processed_data = process_nan_values(extracted_data)

        return {
            "result": processed_data,
            "model_used": llm.model_name,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🔧 実装手順

### Phase 1: リファクタリング（現状維持）

1. **llm_providers.py作成**
   - 抽象クラス定義
   - OpenAIProvider実装
   - LLMFactory実装

2. **main.py修正**
   - 既存のOpenAI呼び出しをFactoryパターンに置き換え
   - 動作確認（既存機能が正常動作すること）

3. **テスト**
   - 既存エンドポイント全て動作確認
   - レスポンス形式が変わっていないこと確認

### Phase 2: 新規プロバイダー追加

4. **Groq追加**
   - GroqProvider実装
   - requirements.txt更新（`groq` パッケージ追加）
   - 環境変数追加（`.env`に`GROQ_API_KEY`）

5. **比較テスト**
   - 同じプロンプトで両方のプロバイダーをテスト
   - 品質・速度・コストを比較

6. **ドキュメント更新**
   - README.mdに使用方法を追記

---

## 📝 環境変数設定

### .envファイル

```bash
# OpenAI（既存）
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5-nano

# Groq（新規）
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-70b-versatile

# デフォルト設定（新規）
DEFAULT_LLM_PROVIDER=openai  # または groq
DEFAULT_LLM_MODEL=gpt-5-nano
```

---

## 🔄 運用方法

### 切り替え方法1: リクエスト時に指定（推奨）

```bash
# OpenAI使用
curl -X POST https://api.hey-watch.me/vibe-analysis/scoring/analyze/chatgpt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "こんにちは",
    "model_provider": "openai",
    "model_name": "gpt-4"
  }'

# Groq使用
curl -X POST https://api.hey-watch.me/vibe-analysis/scoring/analyze/chatgpt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "こんにちは",
    "model_provider": "groq",
    "model_name": "llama-3.1-70b-versatile"
  }'

# デフォルト使用（環境変数から）
curl -X POST https://api.hey-watch.me/vibe-analysis/scoring/analyze/chatgpt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "こんにちは"
  }'
```

### 切り替え方法2: 環境変数で一括切り替え

```bash
# EC2で.envを編集
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82
vi /home/ubuntu/vibe-analysis-scorer/.env

# DEFAULT_LLM_PROVIDERをgroqに変更
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL=llama-3.1-70b-versatile

# サービス再起動
sudo systemctl restart vibe-analysis-scorer
```

---

## ⚠️ 注意事項

### 1. 後方互換性の保持

- 既存のリクエスト（`model_provider`なし）は引き続き動作すること
- デフォルトは現在のOpenAI（gpt-5-nano）を維持

### 2. エラーハンドリング

- プロバイダーAPIのエラーを適切にキャッチ
- リトライロジック（tenacity）を各プロバイダーに適用

### 3. レスポンス形式の統一

- プロバイダーが変わってもレスポンス形式は同じにする
- `model_used`フィールドでどのモデルを使用したか明示

### 4. コスト管理

- プロバイダーごとのAPI使用量を記録
- モニタリングダッシュボードで確認できるようにする（将来）

---

## 📊 比較基準

新しいプロバイダーを追加したら、以下を比較：

| 項目 | OpenAI (gpt-5-nano) | Groq (llama-3.1-70b) |
|------|---------------------|----------------------|
| **コスト** | $/1Mトークン | $/1Mトークン |
| **速度** | レスポンスタイム | レスポンスタイム |
| **品質** | 分析精度 | 分析精度 |
| **安定性** | エラー率 | エラー率 |

---

## 📁 影響範囲

### 修正が必要なファイル

1. ✅ `/api/vibe-analysis/scorer/llm_providers.py` - 新規作成
2. ✅ `/api/vibe-analysis/scorer/main.py` - リファクタリング
3. ✅ `/api/vibe-analysis/scorer/requirements.txt` - groq追加
4. ✅ `/api/vibe-analysis/scorer/.env` - 環境変数追加
5. ✅ `/api/vibe-analysis/scorer/README.md` - ドキュメント更新

### 修正不要（影響なし）

- ❌ Nginx設定（エンドポイント変更なし）
- ❌ Lambda関数（APIインターフェース変更なし）
- ❌ systemd設定（環境変数は.envで管理）

---

## 🚀 次のステップ

1. **Phase 1実装** - OpenAIをFactoryパターンに移行
2. **動作確認** - 既存機能が正常に動作することを確認
3. **Phase 2実装** - Groq追加
4. **比較検証** - 両方のプロバイダーで品質・コスト・速度を比較
5. **本番適用** - 最適なプロバイダーを選択して運用

---

**作成者**: Claude (Session 2025-10-30)
**次のセッションへ**: この計画に基づいて実装を進めてください
