#!/usr/bin/env python3
"""
macOS Activity Logger for Daily Reports

アクティブウィンドウをキャプチャし、OCRでテキストを抽出、
1分ごとにJSONLログを記録し、1時間ごとにLLMで要約します。
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from dotenv import load_dotenv
from openai import OpenAI

# OCR imports
try:
    from ocrmac import ocrmac
except ImportError:
    print("Error: ocrmac is required.")
    print("Install with: pip install ocrmac")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOGS_DIR = Path("logs")
REPORTS_DIR = Path("reports")
SCREENSHOT_PATH = "/tmp/maclogger_screenshot.png"
CAPTURE_INTERVAL = 60  # seconds
HOURLY_SUMMARY_INTERVAL = 3600  # 1 hour in seconds

# Create directories
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


def get_active_window_info() -> Dict[str, str]:
    """
    AppleScriptを使用してアクティブなアプリケーションとウィンドウ情報を取得

    出力: {"application": str, "window_title": str}
    """
    applescript = """
tell application "System Events"
    set frontApp to name of first application process whose frontmost is true
    try
        set frontWindow to name of front window of first application process whose frontmost is true
    on error
        set frontWindow to ""
    end try
    return frontApp & "|" & frontWindow
end tell
"""

    try:
        result = subprocess.run(
            ["osascript", "-e", applescript], capture_output=True, text=True, timeout=5
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            parts = output.split("|", 1)
            return {
                "application": parts[0] if len(parts) > 0 else "",
                "window_title": parts[1] if len(parts) > 1 else "",
            }
    except Exception as e:
        print(f"Error getting active window info: {e}")

    return {"application": "", "window_title": ""}


def get_frontmost_window_id() -> Optional[str]:
    """
    最前面のウィンドウのCGWindowIDを取得

    出力: ウィンドウIDの文字列、取得できない場合はNone
    """
    # Python script to get the frontmost window ID using Quartz
    script = """
import Quartz
import sys

# Get all windows
window_list = Quartz.CGWindowListCopyWindowInfo(
    Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
    Quartz.kCGNullWindowID
)

# Find the frontmost window (layer 0, not menu bar or dock)
for window in window_list:
    layer = window.get(Quartz.kCGWindowLayer, 999)
    owner = window.get(Quartz.kCGWindowOwnerName, "")
    # Skip system UI elements
    if layer == 0 and owner not in ["Window Server", "Dock", "SystemUIServer"]:
        window_id = window.get(Quartz.kCGWindowNumber)
        if window_id:
            print(window_id)
            sys.exit(0)
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    return None


def capture_screenshot(window_id: Optional[str] = None) -> bool:
    """
    screencaptureコマンドでスクリーンショットをキャプチャ
    window_idが指定されていればそのウィンドウのみ、なければ全画面

    入力: window_id (Optional) - キャプチャするウィンドウのID
    出力: 成功したらTrue、失敗したらFalse
    """
    try:
        if window_id:
            # Capture specific window
            cmd = ["screencapture", "-x", "-l", window_id, SCREENSHOT_PATH]
        else:
            # Capture all screens
            cmd = ["screencapture", "-x", SCREENSHOT_PATH]

        result = subprocess.run(cmd, capture_output=True, timeout=10)
        return result.returncode == 0 and Path(SCREENSHOT_PATH).exists()
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return False


def perform_ocr(image_path: str) -> str:
    """
    ocrmacライブラリを使用してOCRを実行(macOS Vision Framework)

    入力: 画像ファイルパス
    出力: 抽出されたテキスト
    """
    try:
        # Check if file exists
        if not Path(image_path).exists():
            return ""

        # Perform OCR using ocrmac (macOS Vision Framework wrapper)
        annotations = ocrmac.OCR(
            image_path, language_preference=["ja-JP", "en-US"]
        ).recognize()

        if not annotations:
            return ""

        # Extract text from annotations
        # Each annotation is a tuple: (text, confidence, bbox)
        text_lines = [annotation[0] for annotation in annotations if annotation[0]]

        return "\n".join(text_lines)

    except Exception as e:
        print(f"Error performing OCR: {e}")
        return ""


def summarize_hourly_activities() -> None:
    """
    過去1時間分のアクティビティログを読み込んで要約し、hourly summaryとして保存
    """
    if not OPENAI_API_KEY:
        print("OpenAI API key not set. Skipping hourly summary.")
        return

    now = datetime.now()
    hour_ago = now - timedelta(hours=1)
    today = now.strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"activity_{today}.jsonl"

    if not log_file.exists():
        return

    # 過去1時間分のログを収集
    activities = []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                timestamp = datetime.fromisoformat(entry["timestamp"])
                if timestamp >= hour_ago:
                    activities.append(
                        {
                            "time": timestamp.strftime("%H:%M"),
                            "app": entry["application"],
                            "window": entry.get("window_title", ""),
                            "ocr": entry.get("ocr_text", ""),  # 全文使用
                        }
                    )
    except Exception as e:
        print(f"Error loading logs for hourly summary: {e}")
        return

    if not activities:
        print("No activities found in the past hour. Skipping hourly summary.")
        return

    print(f"Generating hourly summary from {len(activities)} activities...")

    # まとめて要約
    summary_text = "\n".join(
        [f"[{a['time']}] {a['app']} - {a['window']}: {a['ocr']}" for a in activities]
    )

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは作業ログから活動内容を要約するアシスタントです。",
                },
                {
                    "role": "user",
                    "content": f"""以下は過去1時間の作業ログです。
時系列で主な作業内容を3-5行で日本語で要約してください:

{summary_text}
""",
                },
            ],
        )

        summary = response.choices[0].message.content
        if summary:
            # hourly summaryを保存
            hourly_summary_file = LOGS_DIR / f"hourly_summary_{today}.jsonl"
            with open(hourly_summary_file, "a", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": now.isoformat(),
                        "hour": now.strftime("%H:00"),
                        "activities_count": len(activities),
                        "summary": summary.strip(),
                    },
                    f,
                    ensure_ascii=False,
                )
                f.write("\n")

            print(f"Hourly summary saved: {now.strftime('%H:00')}")

    except Exception as e:
        print(f"Error generating hourly summary: {e}")


def save_log_entry(entry: Dict) -> None:
    """
    JSONL形式でログを記録

    入力: ログエントリ(dict)
    """
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"activity_{today}.jsonl"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")
    except Exception as e:
        print(f"Error saving log entry: {e}")


def load_todays_logs() -> List[Dict]:
    """
    本日のログを読み込み

    出力: ログエントリのリスト
    """
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"activity_{today}.jsonl"

    if not log_file.exists():
        return []

    logs = []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    logs.append(json.loads(line))
    except Exception as e:
        print(f"Error loading logs: {e}")

    return logs


def main_loop() -> None:
    """
    メインループ: 1分ごとに実行し、1時間ごとに要約
    """
    print("macOS Activity Logger started.")
    print(f"Capturing every {CAPTURE_INTERVAL} seconds.")
    print(f"Hourly summary will be generated every hour.")
    print("Press Ctrl+C to stop.\n")

    last_hourly_summary = datetime.now().replace(minute=0, second=0, microsecond=0)

    try:
        while True:
            # Get frontmost window ID for accurate capture
            window_id = get_frontmost_window_id()

            # Get active window info
            window_info = get_active_window_info()

            if not window_info["application"]:
                print("No active window found. Skipping this cycle.")
                time.sleep(CAPTURE_INTERVAL)
                continue

            print(
                f"Capturing: {window_info['application']} - {window_info['window_title']}"
            )

            # Capture screenshot of the frontmost window
            if not capture_screenshot(window_id):
                print("Failed to capture screenshot. Skipping this cycle.")
                time.sleep(CAPTURE_INTERVAL)
                continue

            # Perform OCR
            ocr_text = perform_ocr(SCREENSHOT_PATH)

            # Create log entry (OCR text only, no LLM summary yet)
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "application": window_info["application"],
                "window_title": window_info["window_title"],
                "ocr_text": ocr_text,  # Full OCR text for better context
            }

            # Save log
            save_log_entry(log_entry)
            print(f"Logged: {window_info['application']}\n")

            # Clean up screenshot
            try:
                if Path(SCREENSHOT_PATH).exists():
                    Path(SCREENSHOT_PATH).unlink()
            except Exception as e:
                print(f"Error deleting screenshot: {e}")

            # Check if we should generate hourly summary (毎正時)
            now = datetime.now()
            current_hour = now.replace(minute=0, second=0, microsecond=0)
            if current_hour > last_hourly_summary:
                print("\n" + "=" * 50)
                print("Generating hourly summary...")
                print("=" * 50 + "\n")
                summarize_hourly_activities()
                last_hourly_summary = current_hour

            # Wait for next cycle
            time.sleep(CAPTURE_INTERVAL)

    except KeyboardInterrupt:
        print("\n\nStopping macOS Activity Logger...")

        # Clean up screenshot if exists
        try:
            if Path(SCREENSHOT_PATH).exists():
                Path(SCREENSHOT_PATH).unlink()
        except Exception:
            pass

        print("Goodbye!")


if __name__ == "__main__":
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY not set. LLM features will be disabled.")
        print("Set it with: export OPENAI_API_KEY=your_key")
        print()

    main_loop()

