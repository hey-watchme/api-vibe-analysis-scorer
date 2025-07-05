#!/usr/bin/env python3
"""
新しい感情分析エンドポイントのテストスクリプト
"""

import requests
import json
import os
from datetime import datetime

# API設定
API_BASE_URL = "http://localhost:8002"

def test_health_check():
    """ヘルスチェックのテスト"""
    print("=== ヘルスチェックテスト ===")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"ステータス: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"レスポンス: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"エラー: {response.text}")
    except Exception as e:
        print(f"接続エラー: {e}")
    print()

def test_debug_ec2_connection():
    """EC2接続デバッグのテスト"""
    print("=== EC2接続デバッグテスト ===")
    try:
        response = requests.get(f"{API_BASE_URL}/debug-ec2-connection")
        print(f"ステータス: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"レスポンス: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"エラー: {response.text}")
    except Exception as e:
        print(f"接続エラー: {e}")
    print()

def test_analyze_mood_local():
    """ローカル感情分析のテスト"""
    print("=== ローカル感情分析テスト ===")
    
    # テストデータ
    test_data = {
        "user_id": "user123",
        "date": "2025-06-07"  # 既存のテストデータを使用
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze-mood",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"ステータス: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"処理結果: {data['status']}")
            print(f"メッセージ: {data['message']}")
            print(f"ユーザーID: {data['user_id']}")
            print(f"日付: {data['date']}")
            print(f"ローカルファイル: {data['local_file']}")
            print(f"処理時刻: {data['processed_at']}")
            
            # 処理ログの表示
            if 'processing_log' in data:
                log = data['processing_log']
                print(f"処理ステップ数: {len(log['processing_steps'])}")
                print(f"警告数: {len(log['warnings'])}")
                if log['warnings']:
                    print(f"警告: {log['warnings']}")
            
            # バリデーション結果の表示
            if 'validation_summary' in data:
                validation = data['validation_summary']
                print(f"バリデーション結果: {json.dumps(validation, indent=2, ensure_ascii=False)}")
                
        else:
            print(f"エラー: {response.text}")
            
    except Exception as e:
        print(f"リクエストエラー: {e}")
    print()

def test_analyze_mood_ec2():
    """EC2連携感情分析のテスト"""
    print("=== EC2連携感情分析テスト ===")
    
    # テストデータ
    test_data = {
        "user_id": "user123",
        "date": "2025-06-07"  # 既存のテストデータを使用
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze-mood-ec2",
            json=test_data,
            headers={"Content-Type": "application/json"}
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
                print(f"警告数: {len(log['warnings'])}")
                if log['warnings']:
                    print(f"警告: {log['warnings']}")
            
            # バリデーション結果の表示
            if 'validation_summary' in data:
                validation = data['validation_summary']
                print(f"バリデーション結果: {json.dumps(validation, indent=2, ensure_ascii=False)}")
                
        else:
            print(f"エラー: {response.text}")
            
    except Exception as e:
        print(f"リクエストエラー: {e}")
    print()

def test_with_missing_data():
    """存在しないデータでのテスト"""
    print("=== 存在しないデータテスト ===")
    
    # 存在しないデータ
    test_data = {
        "user_id": "nonexistent_user",
        "date": "2025-01-01"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze-mood",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"ステータス: {response.status_code}")
        print(f"レスポンス: {response.text}")
            
    except Exception as e:
        print(f"リクエストエラー: {e}")
    print()

def main():
    """メイン関数"""
    print("新しい感情分析エンドポイントのテスト開始")
    print("=" * 50)
    
    # 各テストを実行
    test_health_check()
    test_debug_ec2_connection()
    test_analyze_mood_local()
    test_analyze_mood_ec2()
    test_with_missing_data()
    
    print("テスト完了")

if __name__ == "__main__":
    main() 