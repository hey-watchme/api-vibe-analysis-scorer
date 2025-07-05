import requests
import json

# APIのベースURL（ローカル開発環境）
BASE_URL = "http://localhost:8002"

# テスト用のプロンプトデータ
test_data = {
    "prompt": """
あなたは音声から読み取られた発話内容（文字起こし）をもとに、以下の3軸で発話者の状態を分析します：

🟦 心理（Emotion / Mental State）
🟨 認知（Cognition / Language）
🟩 行動（Behavior / Social / Environmental Context）

入力される文字列は会話や独白、ナレーションなどです。それに対して、以下のようなJSON形式で出力してください：

```json
{
  "心理": {
    "感情": "...",
    "ストレスレベル": "...",
    "モチベーション": "..."
  },
  "認知": {
    "注意": "...",
    "言語の複雑さ": "...",
    "認知負荷": "..."
  },
  "行動": {
    "社会的ふるまい": "...",
    "文脈": "...",
    "会話参加の特徴": "..."
  }
}
```

以下の文章を分析してください：
今日はとても疲れました。朝から会議が3つもあって、資料作成に追われていました。でも、プロジェクトが前に進んだので良かったです。明日は少し早く帰って休みたいですね。
"""
}

# 不正なJSON形式を返すテスト用のプロンプト
test_invalid_json_data = {
    "prompt": "こんにちは、今日の天気を教えてください。"
}

def test_chatgpt_relay():
    """ChatGPT中継APIをテストする関数"""
    
    print("テスト開始: /analyze/chatgpt エンドポイント")
    
    # 1. 正常なJSONが返ることが期待されるケース
    print("\n=== 正常なJSONレスポンステスト ===")
    response = requests.post(
        f"{BASE_URL}/analyze/chatgpt",
        json=test_data
    )
    
    # レスポンスの確認
    if response.status_code == 200:
        print("ステータスコード: 200 OK")
        result = response.json()  # レスポンスはJSONとしてパースできるはず
        
        # レスポンスの内容を表示
        print("\n--- レスポンス（dict形式） ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 辞書アクセスの動作確認
        if "心理" in result:
            print("\n--- 辞書アクセステスト ---")
            print(f"心理.感情: {result.get('心理', {}).get('感情', 'なし')}")
    else:
        print(f"エラー: ステータスコード {response.status_code}")
        print(response.text)
    
    # 2. 不正なJSON形式のプロンプトに対するフォールバック動作のテスト
    print("\n=== フォールバック動作テスト ===")
    response = requests.post(
        f"{BASE_URL}/analyze/chatgpt",
        json=test_invalid_json_data
    )
    
    if response.status_code == 200:
        print("ステータスコード: 200 OK")
        result = response.json()  # レスポンスはJSONとしてパースできるはず
        
        # フォールバック辞書の確認
        print("\n--- フォールバックレスポンス ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 辞書アクセスの動作確認
        print("\n--- 辞書アクセステスト ---")
        print(f"感情スコア: {result.get('感情スコア', {})}")
        print(f"解釈: {result.get('解釈', 'なし')}")
    else:
        print(f"エラー: ステータスコード {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_chatgpt_relay() 