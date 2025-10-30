from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import re
import math
from datetime import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# 環境変数の読み込み
load_dotenv()

# Supabaseクライアントのインポート
from supabase_client import SupabaseClient

# LLMプロバイダーのインポート
from llm_providers import get_current_llm, CURRENT_PROVIDER, CURRENT_MODEL

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

class DashboardSummaryRequest(BaseModel):
    device_id: str
    date: str

class TimeBlockAnalysisRequest(BaseModel):
    """タイムブロック単位の分析リクエスト"""
    prompt: str
    device_id: Optional[str] = None
    date: Optional[str] = None
    time_block: Optional[str] = None

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

async def call_llm_with_retry(prompt: str) -> Dict[str, Any]:
    """リトライ機能付きLLM呼び出し（プロバイダー抽象化）"""
    try:
        # 現在設定されているLLMプロバイダーを取得
        llm = get_current_llm()

        # LLM呼び出し（各プロバイダーのリトライ機能が適用される）
        raw_response = llm.generate(prompt)

        # JSON抽出処理
        extracted_data = extract_json_from_response(raw_response)

        # NaN値の処理
        processed_data = process_nan_values(extracted_data)

        return processed_data

    except Exception as e:
        print(f"LLM API呼び出しエラー: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "VibeGraph Generation API"}

@app.post("/analyze/chatgpt")
async def relay_to_chatgpt(request: PromptRequest):
    """
    ⚠️ このエンドポイントは現在使用していません

    プロンプトをChatGPT APIに中継し、応答をJSON形式（dict）で返します。
    改善されたJSON抽出処理とNaN対応を含みます。
    """
    try:
        # LLM呼び出し（プロバイダー抽象化）
        llm = get_current_llm()
        raw_response = llm.generate(request.prompt)

        # 改善されたJSON抽出処理
        extracted_data = extract_json_from_response(raw_response)

        # NaN値の処理
        processed_data = process_nan_values(extracted_data)

        return processed_data
    
    except Exception as e:
        import traceback
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc().split('\n')[-5:]
        }
        print(f"❌ ERROR in relay_to_chatgpt: {error_details}")
        
        raise HTTPException(
            status_code=500, 
            detail={
                "message": "ChatGPT APIでエラーが発生しました",
                "error_details": error_details
            }
        )

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "llm_provider": CURRENT_PROVIDER,
        "llm_model": CURRENT_MODEL
    }

@app.post("/analyze-vibegraph-supabase")
async def analyze_vibegraph_supabase(request: VibeGraphRequest):
    """
    ⚠️ このエンドポイントは現在使用していません

    Supabase統合版の心理グラフ(VibeGraph)処理
    vibe_whisper_promptテーブルからプロンプトを取得し、処理後にvibe_whisper_summaryテーブルに保存
    """
    try:
        device_id = request.device_id
        
        # 日付パラメータは必須
        if not request.date:
            raise HTTPException(
                status_code=400,
                detail="date parameter is required"
            )
        
        search_date = request.date  # 検索用の日付
        
        processing_log = {
            "start_time": datetime.now().isoformat(),
            "mode": "supabase",
            "processing_steps": [],
            "complete": False,
            "warnings": [],
            "search_date": search_date
        }
        
        # Supabaseクライアントの取得
        supabase = get_supabase_client()
        
        # 1) vibe_whisper_promptテーブルからプロンプト取得
        prompt_data = await supabase.get_vibe_whisper_prompt(device_id, search_date)
        if prompt_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"プロンプトが見つかりません: device_id={device_id}, date={search_date}"
            )
        processing_log["processing_steps"].append("vibe_whisper_promptからプロンプト取得完了")
        
        if "prompt" not in prompt_data:
            raise HTTPException(
                status_code=400, 
                detail="プロンプトデータに'prompt'フィールドが見つかりません"
            )
        
        # 実際のデータの日付を取得（prompt_dataの日付を優先）
        actual_date = prompt_data.get('date', search_date)
        if actual_date != search_date:
            processing_log["warnings"].append(f"検索日付({search_date})と実データ日付({actual_date})が異なります")
            processing_log["actual_date"] = actual_date
        
        # 2) LLM処理（リトライ付き）
        analysis_result = await call_llm_with_retry(prompt_data["prompt"])
        processing_log["processing_steps"].append("LLM処理完了")
        
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
            target_date=actual_date,
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
            "date": actual_date,
            "search_date": search_date,
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
        import traceback
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc().split('\n')[-5:],  # 最後の5行のみ
            "device_id": device_id,
            "search_date": search_date,
            "processing_step": processing_log.get("processing_steps", [])[-1] if processing_log.get("processing_steps") else "初期化前"
        }
        
        # エラーログを出力
        print(f"❌ ERROR in analyze_vibegraph_supabase: {error_details}")
        
        raise HTTPException(
            status_code=500, 
            detail={
                "message": "Supabase統合心理グラフ(VibeGraph)処理中にエラーが発生しました",
                "error_details": error_details
            }
        )

@app.post("/analyze-timeblock")
async def analyze_timeblock(request: TimeBlockAnalysisRequest):
    """
    タイムブロック単位の分析処理 + dashboardテーブルへの保存
    """
    try:
        # 必須パラメータのチェック
        if not request.device_id or not request.date or not request.time_block:
            raise HTTPException(
                status_code=400,
                detail="device_id, date, time_block は必須パラメータです"
            )
        
        print(f"\n🔍 タイムブロック分析開始（保存あり）")
        print(f"  - Device ID: {request.device_id}")
        print(f"  - Date: {request.date}")
        print(f"  - Time Block: {request.time_block}")
        print(f"  - Prompt length: {len(request.prompt)} chars")
        
        # LLM処理（プロバイダー抽象化）
        print(f"📤 LLMに送信中... ({CURRENT_PROVIDER}/{CURRENT_MODEL})")
        analysis_result = await call_llm_with_retry(request.prompt)
        print(f"✅ LLM処理完了")
        
        # 結果をターミナルに表示
        print("\n" + "="*60)
        print("📊 分析結果:")
        print("="*60)
        print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
        print("="*60 + "\n")
        
        # Supabaseクライアントの取得
        supabase = get_supabase_client()
        
        # dashboardテーブルへの保存用データを準備
        dashboard_data = {
            'device_id': request.device_id,
            'date': request.date,
            'time_block': request.time_block,
            'summary': analysis_result.get('summary'),
            'behavior': analysis_result.get('behavior'),  # behaviorフィールドを追加
            'vibe_score': analysis_result.get('vibe_score'),
            'analysis_result': json.dumps(analysis_result, ensure_ascii=False),  # JSONBとして保存
            'status': 'completed',  # ステータスを完了に設定
            'processed_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # dashboardテーブルに保存（UPSERT）
        print("💾 dashboardテーブルに保存中...")
        try:
            result = supabase.client.table('dashboard').upsert(dashboard_data).execute()
            print(f"✅ dashboardテーブルへの保存完了")
            save_success = True
        except Exception as e:
            print(f"❌ dashboardテーブルへの保存失敗: {e}")
            save_success = False
            # 保存に失敗してもレスポンスは返す
        
        return {
            "status": "success" if save_success else "partial_success",
            "message": "タイムブロック分析が完了しました" + ("（DB保存成功）" if save_success else "（DB保存失敗）"),
            "device_id": request.device_id,
            "date": request.date,
            "time_block": request.time_block,
            "analysis_result": analysis_result,
            "database_save": save_success,
            "processed_at": datetime.now().isoformat(),
            "model_used": f"{CURRENT_PROVIDER}/{CURRENT_MODEL}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc()
        }
        
        print(f"❌ ERROR in analyze_timeblock_and_save: {error_details}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "message": "タイムブロック分析中にエラーが発生しました",
                "error_details": error_details
            }
        )

@app.post("/analyze-dashboard-summary")
async def analyze_dashboard_summary(request: DashboardSummaryRequest):
    """
    dashboard_summaryテーブルのpromptフィールドを使用してChatGPT分析を行い、
    結果をanalysis_resultフィールドに保存
    """
    try:
        device_id = request.device_id
        target_date = request.date
        
        print(f"\n🔍 Dashboard Summary分析開始")
        print(f"  - Device ID: {device_id}")
        print(f"  - Date: {target_date}")
        
        processing_log = {
            "start_time": datetime.now().isoformat(),
            "mode": "dashboard_summary",
            "processing_steps": [],
            "warnings": []
        }
        
        # Supabaseクライアントの取得
        supabase = get_supabase_client()
        
        # 1) dashboard_summaryテーブルからデータ取得
        dashboard_data = await supabase.get_dashboard_summary_prompt(device_id, target_date)
        if dashboard_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Dashboard summaryデータが見つかりません: device_id={device_id}, date={target_date}"
            )
        processing_log["processing_steps"].append("dashboard_summaryからデータ取得完了")
        
        # promptフィールドの確認
        prompt_data = dashboard_data.get('prompt')
        if not prompt_data:
            raise HTTPException(
                status_code=400,
                detail="dashboard_summaryにpromptデータが存在しません"
            )
        
        # promptがJSONBの場合、文字列に変換
        if isinstance(prompt_data, dict):
            # promptがJSON形式の場合、適切に文字列化
            if 'content' in prompt_data:
                prompt_text = prompt_data['content']
            elif 'text' in prompt_data:
                prompt_text = prompt_data['text']
            else:
                # JSON全体を文字列として使用
                prompt_text = json.dumps(prompt_data, ensure_ascii=False, indent=2)
        elif isinstance(prompt_data, list):
            # リスト形式の場合、結合
            prompt_text = "\n".join([str(item) for item in prompt_data])
        else:
            prompt_text = str(prompt_data)
        
        print(f"  - Prompt length: {len(prompt_text)} chars")
        processing_log["processing_steps"].append(f"プロンプト準備完了（{len(prompt_text)}文字）")
        
        # 2) LLM処理（リトライ付き）
        print(f"📤 LLMに送信中... ({CURRENT_PROVIDER}/{CURRENT_MODEL})")
        analysis_result = await call_llm_with_retry(prompt_text)
        processing_log["processing_steps"].append("LLM処理完了")
        print(f"✅ LLM処理完了")
        
        # 結果をターミナルに表示
        print("\n" + "="*60)
        print("📊 分析結果:")
        print("="*60)
        print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
        print("="*60 + "\n")
        
        # 3) analysis_resultから情報を抽出（オプション）
        vibe_scores = None
        average_vibe = None
        insights = None
        burst_events = None  # 追加
        
        # emotionScoresやvibeScoresがある場合は抽出
        if 'emotionScores' in analysis_result:
            vibe_scores = analysis_result['emotionScores']
        elif 'vibeScores' in analysis_result:
            vibe_scores = analysis_result['vibeScores']
        
        # averageScoreやaverageVibeがある場合は抽出
        if 'averageScore' in analysis_result:
            average_vibe = analysis_result['averageScore']
        elif 'averageVibe' in analysis_result:
            average_vibe = analysis_result['averageVibe']
        
        # cumulative_evaluationをinsightsとして保存（新規追加）
        # iOSアプリではこれをインサイトサマリーとして使用
        if 'cumulative_evaluation' in analysis_result:
            insights = analysis_result['cumulative_evaluation']
            print(f"📝 cumulative_evaluation検出: insightsカラムに保存")
        # 従来のinsightsフィールドも対応（後方互換性）
        elif 'insights' in analysis_result:
            insights = analysis_result['insights']
        
        # burst_eventsがある場合は抽出（新規追加）
        if 'burst_events' in analysis_result:
            burst_events = analysis_result['burst_events']
            print(f"📊 burst_events検出: {len(burst_events) if burst_events else 0}個のイベント")
        
        # 4) dashboard_summaryテーブルのanalysis_resultフィールドを更新
        print("💾 dashboard_summaryテーブルに保存中...")
        save_success = await supabase.update_dashboard_summary_analysis(
            device_id=device_id,
            target_date=target_date,
            analysis_result=analysis_result,
            vibe_scores=vibe_scores,
            average_vibe=average_vibe,
            insights=insights,
            burst_events=burst_events  # 追加
        )
        
        if save_success:
            processing_log["processing_steps"].append("dashboard_summaryテーブルへの保存完了")
            print(f"✅ dashboard_summaryテーブルへの保存完了")
            final_status = "success"
        else:
            processing_log["processing_steps"].append("dashboard_summaryテーブルへの保存失敗")
            processing_log["warnings"].append("データベースへの保存に失敗しました")
            print(f"❌ dashboard_summaryテーブルへの保存失敗")
            final_status = "failed"
        
        processing_log["end_time"] = datetime.now().isoformat()
        
        return {
            "status": final_status,
            "message": "Dashboard Summary分析が完了しました" if final_status == "success" else "処理中にエラーが発生しました",
            "device_id": device_id,
            "date": target_date,
            "database_save": save_success,
            "processed_at": datetime.now().isoformat(),
            "model_used": f"{CURRENT_PROVIDER}/{CURRENT_MODEL}",
            "processing_log": processing_log,
            "analysis_result": analysis_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc().split('\n')[-5:],
            "device_id": device_id,
            "date": target_date
        }
        
        print(f"❌ ERROR in analyze_dashboard_summary: {error_details}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Dashboard Summary処理中にエラーが発生しました",
                "error_details": error_details
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)