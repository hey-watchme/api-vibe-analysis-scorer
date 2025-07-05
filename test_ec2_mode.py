#!/usr/bin/env python3
"""
EC2連携モード専用のテストスクリプト
"""

import requests
import json
import os
from datetime import datetime

# API設定
API_BASE_URL = "http://localhost:8002"

def test_ec2_mood_analysis():
    """EC2連携感情分析のテスト（6月15日データ）"""
    print("=== EC2連携感情分析テスト（2025-06-15） ===")
    
    # テストデータ
    test_data = {
        "user_id": "user123",
        "date": "2025-06-15"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze-mood-ec2",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # ChatGPT処理のため長めのタイムアウト
        )
        
        print(f"ステータス: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"処理結果: {data['status']}")
            print(f"メッセージ: {data['message']}")
            print(f"ユーザーID: {data['user_id']}")
            print(f"日付: {data['date']}")
            print(f"ローカルファイル: {data['local_file']}")
            print(f"EC2アップロード: {data['ec2_upload']}")
            print(f"処理時刻: {data['processed_at']}")
            
            # 処理ログの表示
            if 'processing_log' in data:
                log = data['processing_log']
                print(f"モード: {log['mode']}")
                print(f"EC2 Base URL: {log.get('ec2_base_url', 'N/A')}")
                print(f"処理ステップ数: {len(log['processing_steps'])}")
                print(f"処理ステップ: {log['processing_steps']}")
                print(f"警告数: {len(log['warnings'])}")
                if log['warnings']:
                    print(f"警告: {log['warnings']}")
            
            # バリデーション結果の表示
            if 'validation_summary' in data:
                validation = data['validation_summary']
                print(f"バリデーション結果: {json.dumps(validation, indent=2, ensure_ascii=False)}")
            
            # 生成されたファイルの確認
            if data['status'] == 'success':
                local_file = data['local_file']
                if os.path.exists(local_file):
                    print(f"\n✅ ローカルファイル生成確認: {local_file}")
                    with open(local_file, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                    print(f"感情スコア数: {len(result_data.get('emotionScores', []))}")
                    print(f"平均スコア: {result_data.get('averageScore', 'N/A')}")
                    print(f"ポジティブ時間: {result_data.get('positiveHours', 'N/A')}")
                    print(f"ネガティブ時間: {result_data.get('negativeHours', 'N/A')}")
                    print(f"中立時間: {result_data.get('neutralHours', 'N/A')}")
                else:
                    print(f"❌ ローカルファイルが見つかりません: {local_file}")
                
                if data['ec2_upload']:
                    print("✅ EC2アップロード成功")
                else:
                    print("❌ EC2アップロード失敗")
                
        else:
            print(f"エラー: {response.text}")
            
    except Exception as e:
        print(f"リクエストエラー: {e}")
    print()

def test_debug_connection():
    """EC2接続デバッグ"""
    print("=== EC2接続デバッグ ===")
    try:
        response = requests.get(f"{API_BASE_URL}/debug-ec2-connection")
        print(f"ステータス: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"現在のモード: {data['environment']['mode']}")
            print(f"EC2 Base URL: {data['environment']['EC2_BASE_URL']}")
            print(f"OpenAI Key設定: {data['environment']['has_openai_key']}")
            print(f"テスト結果: {json.dumps(data['tests'], indent=2, ensure_ascii=False)}")
        else:
            print(f"エラー: {response.text}")
    except Exception as e:
        print(f"接続エラー: {e}")
    print()

def main():
    """メイン関数"""
    print("EC2連携モードテスト開始")
    print("=" * 50)
    
    # デバッグ情報確認
    test_debug_connection()
    
    # EC2連携テスト実行
    test_ec2_mood_analysis()
    
    print("テスト完了")

if __name__ == "__main__":
    main() 