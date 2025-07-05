#!/bin/bash

echo "新しい感情分析エンドポイントのテスト開始"
echo "================================================"

# 必要な依存関係をインストール
echo "依存関係のインストール..."
pip install -r requirements.txt

echo ""
echo "テストスクリプトを実行..."
python test_mood_analysis.py 