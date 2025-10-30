#!/usr/bin/env python3
"""
burst_eventsフィールドの保存機能をテストするスクリプト
"""

import requests
import json
from datetime import datetime
import sys

# APIエンドポイント
API_URL = "http://localhost:8002/analyze-dashboard-summary"

# テスト用のリクエストデータ
test_data = {
    "device_id": "test-burst-events-device",
    "date": datetime.now().strftime("%Y-%m-%d")
}

def test_burst_events():
    """burst_eventsの保存をテスト"""
    
    print("\n" + "="*60)
    print("🧪 burst_eventsフィールド保存テスト")
    print("="*60)
    
    print(f"\n📋 テストデータ:")
    print(f"  - device_id: {test_data['device_id']}")
    print(f"  - date: {test_data['date']}")
    
    print(f"\n🚀 APIエンドポイントにリクエストを送信中...")
    print(f"  URL: {API_URL}")
    
    try:
        # APIにリクエストを送信
        response = requests.post(
            API_URL,
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📬 レスポンス受信:")
        print(f"  - ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 処理成功!")
            print(f"  - status: {result.get('status')}")
            print(f"  - message: {result.get('message')}")
            print(f"  - database_save: {result.get('database_save')}")
            
            # analysis_resultの内容を確認
            analysis_result = result.get('analysis_result', {})
            
            # burst_eventsがあるか確認
            if 'burst_events' in analysis_result:
                burst_events = analysis_result['burst_events']
                print(f"\n🎯 burst_events検出:")
                print(f"  - イベント数: {len(burst_events) if burst_events else 0}")
                
                if burst_events:
                    print(f"\n📊 burst_eventsの内容:")
                    for i, event in enumerate(burst_events, 1):
                        print(f"\n  イベント {i}:")
                        print(f"    - time: {event.get('time')}")
                        print(f"    - event: {event.get('event')}")
                        print(f"    - score_change: {event.get('score_change')}")
                        print(f"    - from_score: {event.get('from_score')}")
                        print(f"    - to_score: {event.get('to_score')}")
                else:
                    print("  burst_eventsは空または未定義です")
            else:
                print("\n⚠️  burst_eventsフィールドがanalysis_resultに含まれていません")
                print("  これは正常な動作です（ChatGPTがburst_eventsを返さなかった場合）")
            
            # 完全なレスポンスをファイルに保存
            output_file = f"test_burst_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n💾 完全なレスポンスを保存しました: {output_file}")
            
        elif response.status_code == 404:
            print("\n⚠️  データが見つかりません")
            print("  dashboard_summaryテーブルにテストデータが存在しない可能性があります")
            print("  プロンプト生成APIを先に実行してください")
            
        else:
            print(f"\n❌ エラーが発生しました:")
            error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(json.dumps(error_detail, ensure_ascii=False, indent=2))
            
    except requests.exceptions.ConnectionError:
        print("\n❌ APIサーバーに接続できません")
        print("  APIサーバーが起動していることを確認してください")
        print("  コマンド: python3 main.py")
        
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()

def main():
    """メイン処理"""
    print("\n🔧 burst_eventsフィールド保存機能テスト")
    print("-" * 60)
    print("このスクリプトは、ChatGPT API (api_gpt_v1) の")
    print("burst_events保存機能が正しく動作することを確認します。")
    print("-" * 60)
    
    # 注意事項
    print("\n⚠️  注意事項:")
    print("1. APIサーバーが起動している必要があります (port 8002)")
    print("2. dashboard_summaryテーブルにテストデータが必要です")
    print("3. .envファイルにOpenAI APIキーが設定されている必要があります")
    
    # 実行確認
    response = input("\n続行しますか？ (y/n): ")
    if response.lower() != 'y':
        print("テストを中止しました")
        sys.exit(0)
    
    # テスト実行
    test_burst_events()
    
    print("\n" + "="*60)
    print("✨ テスト完了!")
    print("="*60)

if __name__ == "__main__":
    main()