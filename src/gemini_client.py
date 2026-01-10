#!/usr/bin/env python3
"""
Gemini API Client

Gemini APIクライアントの生成と共通設定を提供します。
"""

import os
import requests
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3-pro-preview"


def create_gemini_client() -> genai.Client | None:
    """
    Geminiクライアントを生成して返す

    出力: genai.Client または None（APIキー未設定・生成失敗時）
    """
    if not GEMINI_API_KEY:
        print("Gemini API key not set. Skipping report generation.")
        print("Set it with: export GEMINI_API_KEY=your_key")
        return None

    try:
        return genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Failed to create Gemini client: {e}")
        return None


def check_network_connection() -> bool:
    """
    Gemini APIへの接続確認

    出力: 接続可能な場合True、接続不可の場合False
    """
    try:
        response = requests.get(
            "https://generativelanguage.googleapis.com",
            timeout=5
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Network connection check failed: {e}")
        return False


def generate_content(client: genai.Client, prompt: str) -> str | None:
    """
    Gemini APIでコンテンツを生成

    入力:
        client - Geminiクライアント
        prompt - プロンプト文字列
    出力:
        生成されたテキスト または None（エラー時）
    """
    try:
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return None
