from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import re
import math
from datetime import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

# 環境変数の読み込み
load_dotenv()

# Supabaseクライアントのインポート（遅延初期化のため後で）
from supabase_client import SupabaseClient

# 設定
EC2_BASE_URL = os.getenv("EC2_BASE_URL", "https://api.hey-watch.me")  # デフォルトをEC2モードに変更
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# OpenAI クライアントの初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="VibeGraph Generation API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabaseクライアントの遅延初期化
supabase_client = None

def get_supabase_client():
    """Supabaseクライアントを遅延初期化して取得"""
    global supabase_client
    if supabase_client is None:
        try:
            supabase_client = SupabaseClient()
            print("✅ Supabase client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Supabase client: {e}")
            raise e
    return supabase_client

class PromptRequest(BaseModel):
    prompt: str

class VibeGraphRequest(BaseModel):
    device_id: str
    date: Optional[str] = None

def extract_json_from_response(raw_response: str) -> Dict[str, Any]:
    """ChatGPTの応答からJSONを抽出し、改善された処理を適用する"""
    
    # まず応答全体をstrip
    content = raw_response.strip()
    
    try:
        # パターン1: 応答全体がJSON形式の場合
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
            
        # パターン2: ```json ... ``` 形式で囲まれている場合（改善版）
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            json_content = json_match.group(1).strip()
            return json.loads(json_content)
            
        # パターン3: { ... } の形式の最初のJSONブロックを抽出（改善版）
        json_block_match = re.search(r'({.*})', content, re.DOTALL)
        if json_block_match:
            json_content = json_block_match.group(1).strip()
            return json.loads(json_content)
            
        # どのパターンにも一致しない場合
        raise ValueError("JSONデータを抽出できませんでした")
        
    except (json.JSONDecodeError, ValueError) as e:
        # JSON解析に失敗した場合のフォールバック
        return {
            "processing_error": f"JSON解析エラー: {str(e)}",
            "raw_response": raw_response,
            "extracted_content": content[:500] + "..." if len(content) > 500 else content
        }

def process_nan_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """NaN文字列をfloat('nan')に変換する"""
    
    def convert_nan_recursive(obj):
        if isinstance(obj, dict):
            return {k: convert_nan_recursive(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_nan_recursive(item) for item in obj]
        elif isinstance(obj, str) and obj.lower() == "nan":
            return float('nan')
        else:
            return obj
    
    return convert_nan_recursive(data)

def validate_emotion_scores(data: Dict[str, Any]) -> Dict[str, Any]:
    """emotionScoresの構造をバリデーションし、必要に応じて補完する"""
    
    validation_info = {
        "original_score_count": 0,
        "expected_score_count": 48,
        "score_length_warning": False,
        "missing_scores_filled": 0,
        "nan_scores_detected": 0
    }
    
    # emotionScoresが存在するかチェック
    if "emotionScores" in data and isinstance(data["emotionScores"], list):
        original_scores = data["emotionScores"]
        validation_info["original_score_count"] = len(original_scores)
        
        # NaN値の数をカウント
        for score in original_scores:
            if isinstance(score, float) and math.isnan(score):
                validation_info["nan_scores_detected"] += 1
            elif isinstance(score, str) and score.lower() == "nan":
                validation_info["nan_scores_detected"] += 1
        
        # 48個に満たない場合は補完
        if len(original_scores) < 48:
            missing_count = 48 - len(original_scores)
            validation_info["missing_scores_filled"] = missing_count
            validation_info["score_length_warning"] = True
            
            # NaNで補完
            data["emotionScores"] = original_scores + [float('nan')] * missing_count
        
        # averageScoreを再計算（NaNを除外）
        valid_scores = []
        for score in data["emotionScores"]:
            if isinstance(score, (int, float)) and not math.isnan(score):
                valid_scores.append(score)
        
        if valid_scores:
            data["averageScore"] = sum(valid_scores) / len(valid_scores)
            validation_info["average_calculated_from"] = len(valid_scores)
        else:
            data["averageScore"] = float('nan')
            validation_info["average_calculated_from"] = 0
    
    elif "emotionScores" not in data:
        # emotionScoresが存在しない場合は空のリストで初期化
        data["emotionScores"] = [float('nan')] * 48
        validation_info["missing_scores_filled"] = 48
        validation_info["score_length_warning"] = True
        data["averageScore"] = float('nan')
    
    return data, validation_info

# EC2連携ヘルパー関数
async def fetch_prompt_from_ec2(device_id: str, date: str) -> Optional[Dict[str, Any]]:
    """EC2からプロンプトファイルを取得"""
    if EC2_BASE_URL == "local":
        # ローカルモード
        local_path = f"/Users/kaya.matsumoto/data/data_accounts/{device_id}/{date}/prompt/emotion-timeline_gpt_prompt.json"
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"ローカルファイル読み込みエラー: {e}")
            return None
    else:
        # EC2モード
        url = f"{EC2_BASE_URL}/status/{device_id}/{date}/prompt/emotion-timeline_gpt_prompt.json"
        try:
            # SSL検証を無効にしてテスト
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"EC2からの取得失敗: {response.status} - URL: {url}")
                        error_text = await response.text()
                        print(f"エラー詳細: {error_text}")
                        return None
        except Exception as e:
            print(f"EC2接続エラー: {e}")
            return None

def save_analysis_locally(device_id: str, date: str, analysis_data: Dict[str, Any]) -> str:
    """分析結果をローカルに保存"""
    local_dir = f"/Users/kaya.matsumoto/data/data_accounts/{device_id}/{date}/emotion-timeline"
    local_path = f"{local_dir}/emotion-timeline.json"
    
    # ディレクトリ作成
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    
    # ファイル保存
    with open(local_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
    
    return local_path

async def upload_analysis_to_ec2(device_id: str, date: str, local_file_path: str) -> bool:
    """分析結果をEC2にアップロード"""
    if EC2_BASE_URL == "local":
        # ローカルモードでは何もしない
        return True
    
    # 新しいエンドポイントを使用
    url = f"{EC2_BASE_URL}/upload/analysis/emotion-timeline"
    
    try:
        with open(local_file_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename='emotion-timeline.json', content_type='application/json')
            data.add_field('device_id', device_id)
            data.add_field('date', date)
            
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        print(f"EC2アップロード成功: {response_data}")
                        return True
                    else:
                        print(f"EC2アップロード失敗: {response.status}")
                        error_text = await response.text()
                        print(f"エラー詳細: {error_text}")
                        return False
    except Exception as e:
        print(f"EC2アップロードエラー: {e}")
        return False

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(Exception)
)
async def call_chatgpt_with_retry(prompt: str) -> Dict[str, Any]:
    """リトライ機能付きChatGPT呼び出し"""
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        raw_response = response.choices[0].message.content
        
        # JSON抽出処理
        extracted_data = extract_json_from_response(raw_response)
        
        # NaN値の処理
        processed_data = process_nan_values(extracted_data)
        
        return processed_data
        
    except Exception as e:
        print(f"ChatGPT API呼び出しエラー: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "VibeGraph Generation API"}

@app.post("/analyze/chatgpt")
async def relay_to_chatgpt(request: PromptRequest):
    """
    プロンプトをChatGPT APIに中継し、応答をJSON形式（dict）で返します。
    改善されたJSON抽出処理とNaN対応を含みます。
    """
    try:
        # ChatGPT APIの呼び出し
        response = client.chat.completions.create(
            model="gpt-4",  # または "gpt-3.5-turbo"
            messages=[
                {"role": "user", "content": request.prompt}
            ]
        )

        # レスポンスの取得
        raw_response = response.choices[0].message.content
        
        # 改善されたJSON抽出処理
        extracted_data = extract_json_from_response(raw_response)
        
        # NaN値の処理
        processed_data = process_nan_values(extracted_data)
        
        return processed_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChatGPT APIでエラーが発生しました: {str(e)}")

# このエンドポイントは廃止されました。/analyze-vibegraph-vaultを使用してください。

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "local" if EC2_BASE_URL == "local" else "ec2",
        "ec2_base_url": EC2_BASE_URL,
        "openai_model": OPENAI_MODEL
    }

# このエンドポイントは廃止されました。/analyze-vibegraph-vaultを使用してください。

@app.post("/analyze-vibegraph-vault")
async def analyze_vibegraph_vault(request: VibeGraphRequest):
    """
    Vault連携版の心理グラフ(VibeGraph)処理
    Vaultからプロンプトを取得し、処理後にVaultにアップロード
    """
    try:
        device_id = request.device_id
        date = request.date or datetime.now().strftime("%Y-%m-%d")
        
        processing_log = {
            "start_time": datetime.now().isoformat(),
            "mode": "ec2" if EC2_BASE_URL != "local" else "local",
            "ec2_base_url": EC2_BASE_URL,
            "processing_steps": [],
            "complete": False,
            "warnings": []
        }
        
        # 1) プロンプト取得（EC2またはローカル）
        prompt_data = await fetch_prompt_from_ec2(device_id, date)
        if prompt_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"プロンプトファイルが見つかりません: {device_id}/{date}"
            )
        processing_log["processing_steps"].append("プロンプト取得完了")
        
        if "prompt" not in prompt_data:
            raise HTTPException(
                status_code=400, 
                detail="プロンプトファイルに'prompt'フィールドが見つかりません"
            )
        
        # 2) ChatGPT処理（リトライ付き）
        analysis_result = await call_chatgpt_with_retry(prompt_data["prompt"])
        processing_log["processing_steps"].append("ChatGPT処理完了")
        
        # 3) 構造バリデーション
        validated_data, validation_info = validate_emotion_scores(analysis_result)
        processing_log["validation_info"] = validation_info
        processing_log["processing_steps"].append("構造バリデーション完了")
        
        # 警告の追加
        if validation_info.get("score_length_warning", False):
            processing_log["warnings"].append(f"emotionScores不足: {validation_info['missing_scores_filled']}個のスコアをNaNで補完")
        
        if validation_info.get("nan_scores_detected", 0) > 0:
            processing_log["warnings"].append(f"{validation_info['nan_scores_detected']}個のNaN値を検出")
        
        # 処理時刻の追加
        validated_data["processed_at"] = datetime.now().isoformat()
        validated_data["processing_log"] = processing_log
        
        # 4) ローカル保存
        local_path = save_analysis_locally(device_id, date, validated_data)
        processing_log["processing_steps"].append("ローカル保存完了")
        
        # 5) EC2アップロード
        upload_success = await upload_analysis_to_ec2(device_id, date, local_path)
        if upload_success:
            processing_log["processing_steps"].append("EC2アップロード完了")
            final_status = "success"
        else:
            processing_log["processing_steps"].append("EC2アップロード失敗")
            processing_log["warnings"].append("EC2アップロードに失敗しました")
            final_status = "partial"
        
        processing_log["complete"] = True
        processing_log["end_time"] = datetime.now().isoformat()
        
        return {
            "status": final_status,
            "message": "Vault連携心理グラフ(VibeGraph)処理が完了しました" if final_status == "success" else "処理は完了しましたが、Vaultアップロードに失敗しました",
            "device_id": device_id,
            "date": date,
            "local_file": local_path,
            "ec2_upload": upload_success,
            "processed_at": datetime.now().isoformat(),
            "processing_log": processing_log,
            "validation_summary": {
                "total_warnings": len(processing_log["warnings"]),
                "structure_valid": not validation_info.get("score_length_warning", False),
                "nan_handling": "completed" if validation_info.get("nan_scores_detected", 0) > 0 else "not_required"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Vault連携心理グラフ(VibeGraph)処理中にエラーが発生しました: {str(e)}"
        )

@app.post("/analyze-vibegraph-supabase")
async def analyze_vibegraph_supabase(request: VibeGraphRequest):
    """
    Supabase統合版の心理グラフ(VibeGraph)処理
    vibe_whisper_promptテーブルからプロンプトを取得し、処理後にvibe_whisper_summaryテーブルに保存
    """
    try:
        device_id = request.device_id
        date = request.date or datetime.now().strftime("%Y-%m-%d")
        
        processing_log = {
            "start_time": datetime.now().isoformat(),
            "mode": "supabase",
            "processing_steps": [],
            "complete": False,
            "warnings": []
        }
        
        # Supabaseクライアントの取得
        supabase = get_supabase_client()
        
        # 1) vibe_whisper_promptテーブルからプロンプト取得
        prompt_data = await supabase.get_vibe_whisper_prompt(device_id, date)
        if prompt_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"プロンプトが見つかりません: device_id={device_id}, date={date}"
            )
        processing_log["processing_steps"].append("vibe_whisper_promptからプロンプト取得完了")
        
        if "prompt" not in prompt_data:
            raise HTTPException(
                status_code=400, 
                detail="プロンプトデータに'prompt'フィールドが見つかりません"
            )
        
        # 2) ChatGPT処理（リトライ付き）
        analysis_result = await call_chatgpt_with_retry(prompt_data["prompt"])
        processing_log["processing_steps"].append("ChatGPT処理完了")
        
        # 3) 構造バリデーション
        validated_data, validation_info = validate_emotion_scores(analysis_result)
        processing_log["validation_info"] = validation_info
        processing_log["processing_steps"].append("構造バリデーション完了")
        
        # 警告の追加
        if validation_info.get("score_length_warning", False):
            processing_log["warnings"].append(f"emotionScores不足: {validation_info['missing_scores_filled']}個のスコアをNaNで補完")
        
        if validation_info.get("nan_scores_detected", 0) > 0:
            processing_log["warnings"].append(f"{validation_info['nan_scores_detected']}個のNaN値を検出")
        
        # 4) データを整形してvibe_whisper_summaryテーブルに保存
        # emotionScoresをvibe_scoresに変換（キー名の変更）
        vibe_scores = validated_data.get("emotionScores", [])
        
        save_success = await supabase.save_to_vibe_whisper_summary(
            device_id=device_id,
            target_date=date,
            vibe_scores=vibe_scores,
            average_score=validated_data.get("averageScore", 0.0),
            positive_hours=validated_data.get("positiveHours", 0.0),
            negative_hours=validated_data.get("negativeHours", 0.0),
            neutral_hours=validated_data.get("neutralHours", 0.0),
            insights=validated_data.get("insights", []),
            vibe_changes=validated_data.get("emotionChanges", []),
            processing_log=processing_log
        )
        
        if save_success:
            processing_log["processing_steps"].append("vibe_whisper_summaryテーブルに保存完了")
            final_status = "success"
        else:
            processing_log["processing_steps"].append("vibe_whisper_summaryテーブルへの保存失敗")
            processing_log["warnings"].append("データベースへの保存に失敗しました")
            final_status = "failed"
        
        processing_log["complete"] = True
        processing_log["end_time"] = datetime.now().isoformat()
        
        return {
            "status": final_status,
            "message": "Supabase統合心理グラフ(VibeGraph)処理が完了しました" if final_status == "success" else "処理中にエラーが発生しました",
            "device_id": device_id,
            "date": date,
            "database_save": save_success,
            "processed_at": datetime.now().isoformat(),
            "processing_log": processing_log,
            "validation_summary": {
                "total_warnings": len(processing_log["warnings"]),
                "structure_valid": not validation_info.get("score_length_warning", False),
                "nan_handling": "completed" if validation_info.get("nan_scores_detected", 0) > 0 else "not_required"
            },
            "summary": {
                "vibe_scores": vibe_scores,
                "average_score": validated_data.get("averageScore", 0.0),
                "positive_hours": validated_data.get("positiveHours", 0.0),
                "negative_hours": validated_data.get("negativeHours", 0.0),
                "neutral_hours": validated_data.get("neutralHours", 0.0),
                "insights": validated_data.get("insights", []),
                "vibe_changes": validated_data.get("emotionChanges", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Supabase統合心理グラフ(VibeGraph)処理中にエラーが発生しました: {str(e)}"
        )

@app.get("/debug-ec2-connection")
async def debug_ec2_connection():
    """EC2接続テスト用デバッグエンドポイント"""
    debug_info = {
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "EC2_BASE_URL": EC2_BASE_URL,
            "mode": "local" if EC2_BASE_URL == "local" else "ec2",
            "OPENAI_MODEL": OPENAI_MODEL,
            "has_openai_key": bool(os.getenv("OPENAI_API_KEY"))
        },
        "tests": []
    }
    
    if EC2_BASE_URL == "local":
        debug_info["tests"].append({
            "test": "local_mode",
            "status": "active",
            "message": "ローカルモードで動作中"
        })
    else:
        # EC2接続テスト
        test_url = f"{EC2_BASE_URL}/health"
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    debug_info["tests"].append({
                        "test": "ec2_health_check",
                        "url": test_url,
                        "status": response.status,
                        "success": response.status == 200,
                        "response": await response.text() if response.status == 200 else None
                    })
        except Exception as e:
            debug_info["tests"].append({
                "test": "ec2_health_check",
                "url": test_url,
                "status": "error",
                "success": False,
                "error": str(e)
            })
    
    return debug_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 