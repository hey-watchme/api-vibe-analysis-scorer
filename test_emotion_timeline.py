import requests
import json
import os
import math
from datetime import datetime

# APIのベースURL（ローカル開発環境）
BASE_URL = "http://localhost:8002"

def create_test_prompt_file(username="user123", date=None):
    """テスト用のプロンプトファイルを作成する"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # ディレクトリパスの構築
    base_path = f"/Users/kaya.matsumoto/data/data_accounts/{username}/{date}/transcriptions"
    os.makedirs(base_path, exist_ok=True)
    
    # テスト用のプロンプトデータ（JSON形式で返すよう明確に指示）
    test_prompt_data = {
        "prompt": """
以下の音声文字起こしデータから感情のタイムラインを分析し、必ずJSON形式で結果を返してください：

```json
{
  "emotionScores": [0.8, 0.2, 0.9, 0.5, 0.3, 0.7, 0.6, 0.4, 0.8, 0.1, 0.9, 0.7, 0.5, 0.3, 0.8, 0.6, 0.4, 0.7, 0.2, 0.9, 0.5, 0.8, 0.3, 0.6, 0.7, 0.4, 0.9, 0.2, 0.8, 0.5, 0.6, 0.3, 0.7, 0.9, 0.4, 0.8, 0.2, 0.5, 0.7, 0.6, 0.3, 0.9, 0.4, 0.8, 0.5, 0.7, 0.2, 0.6],
  "averageScore": 0.6,
  "timeline": [
    {
      "timestamp": "00:00-00:30",
      "emotion": "positive",
      "intensity": 0.8
    },
    {
      "timestamp": "00:30-01:00",
      "emotion": "neutral",
      "intensity": 0.2
    }
  ],
  "summary": {
    "overall_emotion": "positive",
    "dominant_pattern": "stable",
    "peak_times": ["09:00", "10:30"]
  }
}
```

分析対象の文字起こしデータ：
「今日は本当に素晴らしい一日でした。朝から気分が良くて、仕事もスムーズに進みました。午後には友人と楽しいランチを取ることができて、とても充実した時間を過ごせました。夕方は少し疲れましたが、全体的にはとても満足しています。」

上記のJSON形式で、emotionScoresには48個の数値（0.0-1.0）を含めて返してください。
        """,
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "username": username,
            "date": date,
            "file_type": "emotion_timeline_prompt"
        }
    }
    
    # ファイルに保存
    file_path = f"{base_path}/emotion-timeline_gpt_prompt.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(test_prompt_data, f, ensure_ascii=False, indent=2)
    
    print(f"テスト用プロンプトファイルを作成しました: {file_path}")
    return file_path

def create_nan_test_prompt_file(username="testuser_nan", date=None):
    """NaN値を含むテスト用のプロンプトファイルを作成する"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # ディレクトリパスの構築
    base_path = f"/Users/kaya.matsumoto/data/data_accounts/{username}/{date}/transcriptions"
    os.makedirs(base_path, exist_ok=True)
    
    # NaN値を含むテスト用のプロンプトデータ
    test_prompt_data = {
        "prompt": """
以下のデータから感情分析を行い、JSON形式で返してください：

```json
{
  "emotionScores": [0.8, "NaN", 0.5, 0.3, "NaN", 0.7],
  "averageScore": "NaN",
  "analysis": "データに欠損値が含まれています"
}
```

上記のようにNaN値が含まれる場合の処理をテストします。
        """,
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "username": username,
            "date": date,
            "file_type": "nan_test_prompt"
        }
    }
    
    # ファイルに保存
    file_path = f"{base_path}/emotion-timeline_gpt_prompt.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(test_prompt_data, f, ensure_ascii=False, indent=2)
    
    print(f"NaNテスト用プロンプトファイルを作成しました: {file_path}")
    return file_path

def create_test_prompt_file_old(username="user123", date=None):
    """テスト用のプロンプトファイルを作成する"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # ディレクトリパスの構築
    base_path = f"/Users/kaya.matsumoto/data/data_accounts/{username}/{date}/transcriptions"
    os.makedirs(base_path, exist_ok=True)
    
    # テスト用のプロンプトデータ
    test_prompt_data = {
        "prompt": """
以下の音声文字起こしデータから感情のタイムラインを分析し、JSON形式で結果を返してください：

分析項目：
1. 感情スコア（ポジティブ、ネガティブ、ニュートラル）
2. 感情の変化パターン
3. 主要な感情キーワード
4. 時系列での感情推移

以下のJSON形式で返してください：
{
  "emotion_timeline": [
    {
      "timestamp": "00:00-00:30",
      "emotion_scores": {
        "positive": 0.8,
        "negative": 0.1,
        "neutral": 0.1
      },
      "primary_emotion": "喜び",
      "keywords": ["嬉しい", "楽しい"]
    }
  ],
  "summary": {
    "overall_emotion": "ポジティブ",
    "emotion_changes": 3,
    "dominant_emotion": "喜び"
  },
  "metadata": {
    "analysis_date": "2025-01-27",
    "total_segments": 5
  }
}

分析対象の文字起こしデータ：
「今日は本当に素晴らしい一日でした。朝から気分が良くて、仕事もスムーズに進みました。午後には友人と楽しいランチを取ることができて、とても充実した時間を過ごせました。夕方は少し疲れましたが、全体的にはとても満足しています。」
        """,
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "username": username,
            "date": date,
            "file_type": "emotion_timeline_prompt"
        }
    }
    
    # ファイルに保存
    file_path = f"{base_path}/emotion-timeline_gpt_prompt.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(test_prompt_data, f, ensure_ascii=False, indent=2)
    
    print(f"テスト用プロンプトファイルを作成しました: {file_path}")
    return file_path

def test_improved_chatgpt_endpoint():
    """改善されたChatGPTエンドポイントのテスト"""
    
    print("=== 改善されたChatGPTエンドポイントのテスト ===")
    
    # JSON形式で応答するプロンプト
    test_data = {
        "prompt": """
以下をJSON形式で返してください：

```json
{
  "test": "success",
  "values": [1, 2, "NaN", 4, 5],
  "status": "completed"
}
```
        """
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze/chatgpt",
        json=test_data
    )
    
    if response.status_code == 200:
        print("✅ ステータスコード: 200 OK")
        result = response.json()
        
        print("--- 改善されたJSON抽出処理の結果 ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # NaN処理の確認
        if "values" in result and isinstance(result["values"], list):
            nan_count = sum(1 for v in result["values"] if isinstance(v, float) and math.isnan(v))
            print(f"NaN値の数: {nan_count}")
    else:
        print(f"❌ エラー: ステータスコード {response.status_code}")
        print(response.text)

def test_emotion_timeline_processing():
    """emotion-timeline処理APIをテストする関数（改善版）"""
    
    print("\n=== emotion-timeline処理APIテスト（改善版） ===")
    
    # テスト用ファイルの作成
    username = "user123"
    date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        create_test_prompt_file(username, date)
        
        # 1. デフォルトパラメータでのテスト
        print("\n--- デフォルトパラメータテスト ---")
        response = requests.post(
            f"{BASE_URL}/process/emotion-timeline",
            json={}
        )
        
        if response.status_code == 200:
            print("✅ ステータスコード: 200 OK")
            result = response.json()
            
            print(f"処理結果: {result['message']}")
            print(f"入力ファイル: {result['input_file']}")
            print(f"出力ファイル: {result['output_file']}")
            
            # 改善された機能の確認
            if "processing_log" in result:
                processing_log = result["processing_log"]
                print(f"\n📋 処理ステップ数: {len(processing_log['processing_steps'])}")
                print(f"完了ステータス: {processing_log['complete']}")
                print(f"警告数: {len(processing_log.get('warnings', []))}")
                
                if processing_log.get('warnings'):
                    print("⚠️ 警告:")
                    for warning in processing_log['warnings']:
                        print(f"  - {warning}")
            
            if "validation_summary" in result:
                validation = result["validation_summary"]
                print(f"\n🔍 バリデーション結果:")
                print(f"  - 総警告数: {validation['total_warnings']}")
                print(f"  - 構造有効性: {validation['structure_valid']}")
                print(f"  - NaN処理: {validation['nan_handling']}")
            
            # 結果プレビューの確認
            if "result_preview" in result and "emotionScores" in result["result_preview"]:
                emotion_scores = result["result_preview"]["emotionScores"]
                print(f"\n📊 emotionScores:")
                print(f"  - 配列長: {len(emotion_scores) if isinstance(emotion_scores, list) else 'N/A'}")
                
                if isinstance(emotion_scores, list):
                    nan_count = sum(1 for score in emotion_scores if isinstance(score, float) and math.isnan(score))
                    valid_count = len(emotion_scores) - nan_count
                    print(f"  - 有効値: {valid_count}, NaN値: {nan_count}")
            
            # 保存されたファイルの確認
            output_file = result['output_file']
            if os.path.exists(output_file):
                print(f"\n✅ 出力ファイルが正常に作成されました")
                
                with open(output_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                print("--- 保存されたデータの概要 ---")
                print(f"キー数: {len(saved_data.keys())}")
                if "processing_log" in saved_data:
                    print("✅ processing_logが含まれています")
                if "emotionScores" in saved_data:
                    scores = saved_data["emotionScores"]
                    if isinstance(scores, list):
                        print(f"✅ emotionScores配列長: {len(scores)}")
            else:
                print(f"❌ 出力ファイルが見つかりません: {output_file}")
                
        else:
            print(f"❌ エラー: ステータスコード {response.status_code}")
            print(response.text)
        
        # 2. NaN処理のテスト
        print("\n--- NaN処理テスト ---")
        nan_username = "testuser_nan"
        create_nan_test_prompt_file(nan_username, date)
        
        response = requests.post(
            f"{BASE_URL}/process/emotion-timeline",
            json={
                "username": nan_username,
                "date": date
            }
        )
        
        if response.status_code == 200:
            print("✅ NaN処理テスト成功")
            result = response.json()
            
            if "processing_log" in result and "warnings" in result["processing_log"]:
                warnings = result["processing_log"]["warnings"]
                if warnings:
                    print("⚠️ NaN処理警告:")
                    for warning in warnings:
                        print(f"  - {warning}")
                else:
                    print("ℹ️ NaN処理に関する警告はありませんでした")
        else:
            print(f"❌ NaN処理テストエラー: {response.status_code}")
            
        # 3. 存在しないファイルのエラーテスト
        print("\n--- エラーハンドリングテスト ---")
        response = requests.post(
            f"{BASE_URL}/process/emotion-timeline",
            json={
                "username": "nonexistent_user",
                "date": "2000-01-01"
            }
        )
        
        if response.status_code == 404:
            print("✅ 期待通り404エラーが返されました")
            error_detail = response.json()
            print(f"エラー詳細: {error_detail['detail']}")
        else:
            print(f"❌ 予期しないステータスコード: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ テスト実行中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    # 改善されたChatGPTエンドポイントのテスト
    test_improved_chatgpt_endpoint()
    
    # emotion-timeline処理のテスト
    test_emotion_timeline_processing() 