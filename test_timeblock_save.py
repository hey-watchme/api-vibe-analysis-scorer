#!/usr/bin/env python3
"""
タイムブロック分析API（保存機能付き）のテストスクリプト
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

def test_timeblock_analysis_with_save():
    """タイムブロック分析APIをテスト"""
    
    # APIのURL
    api_url = "http://localhost:8002/analyze-timeblock"
    
    # プロンプトを取得
    result = get_prompt_from_dashboard()
    
    if not result:
        print("\n⚠️ Dashboardからプロンプトを取得できませんでした")
        return
    
    prompt, device_id, date, time_block = result
    
    # リクエストデータ
    request_data = {
        "prompt": prompt,
        "device_id": device_id,
        "date": date,
        "time_block": time_block
    }
    
    print("\n📤 APIにリクエスト送信中（保存機能付き）...")
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
            print(f"Database Save: {result.get('database_save')}")
            print(f"Model Used: {result.get('model_used')}")
            print(f"Processed At: {result.get('processed_at')}")
            
            print("\n📊 分析結果:")
            analysis = result.get('analysis_result', {})
            print(json.dumps(analysis, ensure_ascii=False, indent=2))
            
            # 保存されたデータを確認
            if result.get('database_save'):
                print("\n" + "="*60)
                print("💾 データベース保存確認:")
                print("="*60)
                verify_saved_data(device_id, date, time_block)
            
        else:
            print(f"❌ APIエラー: Status Code {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ APIサーバーに接続できません")
        print("APIサーバーが起動していることを確認してください:")
        print("  source .venv/bin/activate && python3 main.py")
    except Exception as e:
        print(f"❌ エラー: {e}")

def verify_saved_data(device_id, date, time_block):
    """保存されたデータを確認"""
    from supabase import create_client
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        result = supabase.table('dashboard').select(
            'summary', 'vibe_score', 'analysis_result', 'processed_at'
        ).eq(
            'device_id', device_id
        ).eq(
            'date', date
        ).eq(
            'time_block', time_block
        ).execute()
        
        if result.data and len(result.data) > 0:
            data = result.data[0]
            print(f"✅ summary: {data.get('summary')[:100]}..." if data.get('summary') else "❌ summary: なし")
            print(f"✅ vibe_score: {data.get('vibe_score')}" if data.get('vibe_score') is not None else "❌ vibe_score: なし")
            print(f"✅ analysis_result: {'保存済み' if data.get('analysis_result') else 'なし'}")
            print(f"✅ processed_at: {data.get('processed_at')}")
            
            if data.get('analysis_result'):
                print("\n📄 analysis_result の内容:")
                # JSONBから辞書に変換
                if isinstance(data['analysis_result'], str):
                    analysis = json.loads(data['analysis_result'])
                else:
                    analysis = data['analysis_result']
                print(json.dumps(analysis, ensure_ascii=False, indent=2)[:500] + "...")
        else:
            print("❌ 保存されたデータが見つかりません")
            
    except Exception as e:
        print(f"❌ データ確認エラー: {e}")

if __name__ == "__main__":
    print("🚀 タイムブロック分析API（保存機能付き）テスト開始\n")
    test_timeblock_analysis_with_save()