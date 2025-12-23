#!/usr/bin/env python3
"""
Daily Report Generator for macOS Activity Logger

hourly summaryをまとめて業務日報を生成します。
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOGS_DIR = Path("logs")
REPORTS_DIR = Path("reports")

# Create directories
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


def generate_daily_report(target_date: str) -> None:
    """
    指定日のhourly summaryをまとめて日報を生成
    
    入力: target_date - 日報作成日 (YYYY-MM-DD形式)
    """
    if not OPENAI_API_KEY:
        print("OpenAI API key not set. Skipping report generation.")
        print("Set it with: export OPENAI_API_KEY=your_key")
        return

    hourly_summary_file = LOGS_DIR / f"hourly_summary_{target_date}.jsonl"

    if not hourly_summary_file.exists():
        print(f"No hourly summaries found for {target_date}.")
        print(f"Expected file: {hourly_summary_file}")
        return

    # hourly summaryを読み込み
    hourly_summaries = []
    try:
        with open(hourly_summary_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    hourly_summaries.append(json.loads(line))
    except Exception as e:
        print(f"Error loading hourly summaries: {e}")
        return

    if not hourly_summaries:
        print("No hourly summaries found. Skipping report generation.")
        return

    print(f"Generating daily report from {len(hourly_summaries)} hourly summaries...")

    # hourly summaryをまとめる
    summary_text = "\n\n".join(
        [f"【{s['hour']}】\n{s['summary']}" for s in hourly_summaries]
    )

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Parse target_date for display
        try:
            date_obj = datetime.strptime(target_date, "%Y-%m-%d")
            date_display = date_obj.strftime("%Y年%m月%d日")
        except ValueError:
            date_display = target_date

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは業務日報を作成するアシスタントです。時間ごとの作業要約から、1日の業務日報を作成します。",
                },
                {
                    "role": "user",
                    "content": f"""以下は1日の時間ごとの作業要約です。これをまとめて業務日報をMarkdown形式で作成してください。

フォーマット:
# 業務日報 - {date_display}

## 本日の主な作業
(時系列または プロジェクト別に整理して記載)

## 使用ツール・技術
(使用したアプリケーションやツールを列挙)

## 所感
(1日の振り返りと明日の予定)

時間ごとの作業要約:
{summary_text}
""",
                },
            ],
        )

        report_content = response.choices[0].message.content

        if report_content:
            report_file = REPORTS_DIR / f"{target_date}.md"

            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_content)

            print(f"Daily report generated: {report_file}")

    except Exception as e:
        print(f"Error generating daily report: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="macOS Activity Loggerの日報を生成します"
    )
    parser.add_argument(
        "--date",
        help="日報作成日 (YYYY-MM-DD形式)",
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    args = parser.parse_args()

    print(f"Generating report for {args.date}...")
    generate_daily_report(args.date)

