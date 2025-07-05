import streamlit as st
import requests
import json
from datetime import datetime, date
import time

# API設定
API_BASE_URL = "http://localhost:8002"
HEADERS = {"Content-Type": "application/json"}

def check_api_health():
    """APIヘルスチェック"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"ステータスコード: {response.status_code}"
    except Exception as e:
        return False, f"接続エラー: {str(e)}"

def analyze_mood_ec2(user_id: str, target_date: str = None):
    """EC2連携感情分析を実行"""
    try:
        # リクエストデータ準備
        request_data = {"user_id": user_id}
        if target_date:
            request_data["date"] = target_date
        
        # API呼び出し
        response = requests.post(
            f"{API_BASE_URL}/analyze-mood-ec2",
            headers=HEADERS,
            json=request_data,
            timeout=120  # 2分タイムアウト
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            error_detail = response.json().get("detail", "不明なエラー")
            return False, f"エラー: {error_detail}"
            
    except requests.exceptions.Timeout:
        return False, "タイムアウトエラー: 処理に時間がかかりすぎています"
    except Exception as e:
        return False, f"リクエストエラー: {str(e)}"

def analyze_mood_local(user_id: str, target_date: str = None):
    """ローカル感情分析を実行"""
    try:
        request_data = {"user_id": user_id}
        if target_date:
            request_data["date"] = target_date
        
        response = requests.post(
            f"{API_BASE_URL}/analyze-mood",
            headers=HEADERS,
            json=request_data,
            timeout=120
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            error_detail = response.json().get("detail", "不明なエラー")
            return False, f"エラー: {error_detail}"
            
    except requests.exceptions.Timeout:
        return False, "タイムアウトエラー: 処理に時間がかかりすぎています"
    except Exception as e:
        return False, f"リクエストエラー: {str(e)}"

def debug_ec2_connection():
    """EC2接続デバッグ"""
    try:
        response = requests.get(f"{API_BASE_URL}/debug-ec2-connection", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"ステータスコード: {response.status_code}"
    except Exception as e:
        return False, f"接続エラー: {str(e)}"

# Streamlitアプリ
def main():
    st.title("🧠 感情分析ダッシュボード")
    st.markdown("ChatGPT Gateway APIを使用した感情分析処理")
    
    # サイドバー: API設定
    with st.sidebar:
        st.header("⚙️ API設定")
        
        # APIヘルスチェック
        if st.button("🔍 API接続確認"):
            with st.spinner("API接続を確認中..."):
                health_ok, health_data = check_api_health()
                
            if health_ok:
                st.success("✅ API接続正常")
                st.json(health_data)
            else:
                st.error(f"❌ API接続エラー: {health_data}")
        
        # EC2接続デバッグ
        if st.button("🔧 EC2接続デバッグ"):
            with st.spinner("EC2接続をテスト中..."):
                debug_ok, debug_data = debug_ec2_connection()
                
            if debug_ok:
                st.success("✅ デバッグ情報取得成功")
                st.json(debug_data)
            else:
                st.error(f"❌ デバッグ情報取得エラー: {debug_data}")
    
    # メインエリア: 感情分析処理
    st.header("📊 感情分析処理")
    
    # 入力フォーム
    col1, col2 = st.columns(2)
    
    with col1:
        user_id = st.text_input(
            "👤 ユーザーID", 
            value="user123",
            help="分析対象のユーザーIDを入力してください"
        )
    
    with col2:
        target_date = st.date_input(
            "📅 分析対象日",
            value=date.today(),
            help="感情分析を実行する日付を選択してください"
        )
    
    # 処理モード選択
    st.subheader("🔧 処理モード")
    mode = st.radio(
        "処理モードを選択してください:",
        ["EC2連携モード（推奨）", "ローカルモード（開発用）"],
        help="EC2連携モードは本番環境用、ローカルモードは開発・テスト用です"
    )
    
    # 実行ボタン
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 感情分析実行", type="primary"):
            if not user_id:
                st.error("❌ ユーザーIDを入力してください")
                return
            
            # 日付をstring形式に変換
            date_str = target_date.strftime("%Y-%m-%d")
            
            # プログレスバー表示
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 処理開始
                status_text.text("🔄 感情分析処理を開始しています...")
                progress_bar.progress(10)
                
                # API呼び出し
                if mode == "EC2連携モード（推奨）":
                    status_text.text("☁️ EC2連携で処理中...")
                    progress_bar.progress(30)
                    success, result = analyze_mood_ec2(user_id, date_str)
                else:
                    status_text.text("💻 ローカルで処理中...")
                    progress_bar.progress(30)
                    success, result = analyze_mood_local(user_id, date_str)
                
                progress_bar.progress(90)
                
                if success:
                    progress_bar.progress(100)
                    status_text.text("✅ 処理完了!")
                    
                    # 成功結果表示
                    st.success(f"🎉 {result['message']}")
                    
                    # 結果詳細
                    with st.expander("📋 処理結果詳細", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("👤 ユーザーID", result['user_id'])
                        with col2:
                            st.metric("📅 処理日", result['date'])
                        with col3:
                            if 'ec2_upload' in result:
                                upload_status = "✅ 成功" if result['ec2_upload'] else "❌ 失敗"
                                st.metric("☁️ EC2アップロード", upload_status)
                    
                    # 処理ログ
                    if 'processing_log' in result:
                        with st.expander("📝 処理ログ"):
                            log = result['processing_log']
                            
                            st.write("**処理ステップ:**")
                            for i, step in enumerate(log.get('processing_steps', []), 1):
                                st.write(f"{i}. {step}")
                            
                            if log.get('warnings'):
                                st.warning("⚠️ 警告:")
                                for warning in log['warnings']:
                                    st.write(f"• {warning}")
                    
                    # バリデーション情報
                    if 'validation_summary' in result:
                        with st.expander("🔍 バリデーション情報"):
                            validation = result['validation_summary']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("⚠️ 警告数", validation.get('total_warnings', 0))
                            with col2:
                                structure_valid = validation.get('structure_valid', True)
                                st.metric("📊 構造", "✅ 正常" if structure_valid else "❌ 異常")
                            with col3:
                                nan_handling = validation.get('nan_handling', 'not_required')
                                st.metric("🔢 NaN処理", nan_handling)
                    
                    # 生データ表示
                    with st.expander("🔍 生データ（JSON）"):
                        st.json(result)
                
                else:
                    progress_bar.progress(0)
                    status_text.text("")
                    st.error(f"❌ 処理失敗: {result}")
                    
            except Exception as e:
                progress_bar.progress(0)
                status_text.text("")
                st.error(f"❌ 予期しないエラー: {str(e)}")
    
    with col2:
        if st.button("🔄 画面リフレッシュ"):
            st.rerun()
    
    # フッター情報
    st.markdown("---")
    st.markdown("""
    **📚 使用方法:**
    1. ユーザーIDと分析対象日を入力
    2. 処理モードを選択（EC2連携推奨）
    3. 「感情分析実行」ボタンをクリック
    4. 処理完了まで待機（通常15-60秒）
    
    **⚠️ 注意事項:**
    - EC2連携モードは本番環境用です
    - 処理には時間がかかる場合があります
    - エラーが発生した場合は、API接続確認を実行してください
    """)

if __name__ == "__main__":
    main() 