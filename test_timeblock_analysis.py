#!/usr/bin/env python3
"""
タイムブロック分析APIのテストスクリプト
"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# Supabaseから実際のプロンプトを取得する関数
def get_prompt_from_dashboard():
    """Dashboardテーブルから保存されたプロンプトを取得"""
    from supabase import create_client
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase環境変数が設定されていません")
        return None
    
    supabase = create_client(supabase_url, supabase_key)
    
    # テストデータのパラメータ
    device_id = '9f7d6e27-98c3-4c19-bdfb-f7fda58b9a93'
    date = '2025-08-31'
    time_block = '17-00'
    
    print(f"📊 Dashboardテーブルからプロンプトを取得中...")
    print(f"  - Device ID: {device_id}")
    print(f"  - Date: {date}")
    print(f"  - Time Block: {time_block}")
    
    try:
        result = supabase.table('dashboard').select('prompt').eq(
            'device_id', device_id
        ).eq(
            'date', date
        ).eq(
            'time_block', time_block
        ).execute()
        
        if result.data and len(result.data) > 0:
            prompt = result.data[0].get('prompt')
            if prompt:
                print(f"✅ プロンプト取得成功: {len(prompt)} chars")
                return prompt, device_id, date, time_block
            else:
                print("❌ プロンプトが空です")
                return None
        else:
            print("❌ データが見つかりません")
            return None
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def test_timeblock_analysis():
    """タイムブロック分析APIをテスト"""
    
    # APIのURL
    api_url = "http://localhost:8002/analyze-timeblock"
    
    # プロンプトを取得
    result = get_prompt_from_dashboard()
    
    if not result:
        print("\n⚠️ Dashboardからプロンプトを取得できませんでした")
        print("テスト用のサンプルプロンプトを使用します")
        
        # サンプルプロンプト
        prompt = """📝 分析依頼
以下は2025-08-31の17-00（夕方）の30分間のマルチモーダルデータです。

【発話内容】
動画のアップロードについて話しています。23GBの大きなファイルで、ハードディスクの問題があり、最後まで完全にアップロードできませんでした。

✅ 出力形式・ルール
以下のJSON形式で分析結果を返してください。

{
  "time_block": "17-00",
  "summary": "この30分間の状況を2-3文で説明",
  "vibe_score": -100から100の整数値,
  "confidence_score": 0.0から1.0の小数値,
  "detected_mood": "neutral"
}

**JSONのみを返してください。**
"""
        device_id = "test-device"
        date = "2025-08-31"
        time_block = "17-00"
    else:
        prompt, device_id, date, time_block = result
    
    # リクエストデータ
    request_data = {
        "prompt": prompt,
        "device_id": device_id,
        "date": date,
        "time_block": time_block
    }
    
    print("\n📤 APIにリクエスト送信中...")
    print(f"URL: {api_url}")
    
    try:
        # APIを呼び出し
        response = requests.post(api_url, json=request_data)
        
        if response.status_code == 200:
            print("✅ APIレスポンス受信成功\n")
            
            # 結果を表示
            result = response.json()
            
            print("="*60)
            print("📊 API応答:")
            print("="*60)
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            print(f"Device ID: {result.get('device_id')}")
            print(f"Date: {result.get('date')}")
            print(f"Time Block: {result.get('time_block')}")
            print(f"Model Used: {result.get('model_used')}")
            print(f"Processed At: {result.get('processed_at')}")
            print("\n分析結果:")
            print(json.dumps(result.get('analysis_result', {}), ensure_ascii=False, indent=2))
            print("="*60)
            
        else:
            print(f"❌ APIエラー: Status Code {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ APIサーバーに接続できません")
        print("APIサーバーが起動していることを確認してください:")
        print("  uvicorn main:app --host 0.0.0.0 --port 8002 --reload")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    print("🚀 タイムブロック分析APIテスト開始\n")
    test_timeblock_analysis()