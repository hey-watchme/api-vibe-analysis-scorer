"""
Supabase Client for vibe_whisper_prompt and vibe_whisper_summary tables
"""

import os
import math
from typing import Dict, Any, Optional, List
from supabase import create_client, Client
from datetime import datetime
import json

class SupabaseClient:
    def __init__(self):
        """Initialize Supabase client"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.client: Client = create_client(url, key)
        print(f"✅ Supabase client initialized: {url}")
    
    async def get_vibe_whisper_prompt(self, device_id: str, target_date: str) -> Optional[Dict[str, Any]]:
        """
        vibe_whisper_promptテーブルから指定したdevice_idと日付のプロンプトを取得
        
        Args:
            device_id: デバイスID
            target_date: 対象日付 (YYYY-MM-DD)
        
        Returns:
            Optional[Dict]: プロンプトデータ
        """
        try:
            response = self.client.table('vibe_whisper_prompt').select('*').eq('device_id', device_id).eq('date', target_date).execute()
            
            if response.data and len(response.data) > 0:
                print(f"✅ Found prompt for device_id={device_id}, date={target_date}")
                return response.data[0]
            else:
                print(f"❌ No prompt found for device_id={device_id}, date={target_date}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching vibe_whisper_prompt: {str(e)}")
            raise e
    
    async def save_to_vibe_whisper_summary(
        self, 
        device_id: str, 
        target_date: str,
        vibe_scores: List[Optional[int]],
        average_score: float,
        positive_hours: float,
        negative_hours: float,
        neutral_hours: float,
        insights: List[str],
        vibe_changes: List[Dict[str, Any]],
        processing_log: Dict[str, Any]
    ) -> bool:
        """
        vibe_whisper_summaryテーブルにデータを保存（UPSERT）
        
        Args:
            device_id: デバイスID
            target_date: 対象日付 (YYYY-MM-DD)
            vibe_scores: 48個のスコア配列（null混在可）
            average_score: 平均スコア
            positive_hours: ポジティブな時間数
            negative_hours: ネガティブな時間数
            neutral_hours: ニュートラルな時間数
            insights: 分析結果のインサイト
            vibe_changes: 感情の変化ポイント
            processing_log: 処理ログ
        
        Returns:
            bool: 保存成功時True
        """
        try:
            # NaN/Infinity値をNoneに変換する関数
            def sanitize_value(value):
                if isinstance(value, float):
                    if math.isnan(value) or math.isinf(value):
                        return None
                return value
            
            def sanitize_list(lst):
                if lst is None:
                    return []
                return [sanitize_value(item) if not isinstance(item, dict) else sanitize_dict(item) for item in lst]
            
            def sanitize_dict(d):
                if d is None:
                    return {}
                result = {}
                for key, value in d.items():
                    if isinstance(value, list):
                        result[key] = sanitize_list(value)
                    elif isinstance(value, dict):
                        result[key] = sanitize_dict(value)
                    else:
                        result[key] = sanitize_value(value)
                return result
            
            # データをサニタイズ
            data = {
                'device_id': device_id,
                'date': target_date,
                'vibe_scores': sanitize_list(vibe_scores),  # NaN/InfinityをNoneに変換
                'average_score': sanitize_value(average_score),
                'positive_hours': sanitize_value(positive_hours),
                'negative_hours': sanitize_value(negative_hours),
                'neutral_hours': sanitize_value(neutral_hours),
                'insights': insights if insights else [],  # Noneの場合は空リスト
                'vibe_changes': sanitize_list(vibe_changes) if vibe_changes else [],  # NaN/InfinityをNoneに変換
                'processed_at': datetime.now().isoformat(),
                'processing_log': sanitize_dict(processing_log) if processing_log else {}  # NaN/InfinityをNoneに変換
            }
            
            # デバッグ用：保存するデータを確認
            import json
            print(f"📝 Saving data to vibe_whisper_summary:")
            print(f"   device_id: {data['device_id']}")
            print(f"   date: {data['date']}")
            print(f"   vibe_scores length: {len(data['vibe_scores']) if data['vibe_scores'] else 0}")
            print(f"   average_score: {data['average_score']}")
            
            # JSONシリアライズ可能か確認
            try:
                json.dumps(data)
            except (TypeError, ValueError) as json_error:
                print(f"❌ JSON serialization error: {json_error}")
                print(f"   Problematic data: {data}")
                raise ValueError(f"データがJSON形式に変換できません: {json_error}")
            
            # UPSERT (既存レコードがあれば更新、なければ挿入)
            response = self.client.table('vibe_whisper_summary').upsert(data).execute()
            
            if response.data:
                print(f"✅ Successfully saved to vibe_whisper_summary: device_id={device_id}, date={target_date}")
                return True
            else:
                print(f"❌ Failed to save to vibe_whisper_summary")
                return False
                
        except Exception as e:
            print(f"❌ Error saving to vibe_whisper_summary: {str(e)}")
            raise e