#!/usr/bin/env python3
"""
Weekly Report Generator for macOS Activity Logger

今週のdaily reportをまとめて週報を生成します。
"""

import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DAILY_REPORTS_DIR = Path("reports/daily")
WEEKLY_REPORTS_DIR = Path("reports/weekly")

# Create directories
DAILY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
WEEKLY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def get_week_date_range(target_date: datetime) -> tuple[datetime, datetime]:
    """
    指定日を含む週の月曜日と日曜日を取得
    
    入力: target_date - 基準日
    出力: (monday, sunday) - その週の月曜日と日曜日
    """
    # ISO週の月曜日(weekday 0)を基準とする
    monday = target_date - timedelta(days=target_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_iso_week_string(target_date: datetime) -> str:
    """
    ISO週番号の文字列を取得
    
    入力: target_date - 基準日
    出力: YYYY-WNN形式の文字列(例: 2025-W52)
    """
    year, week_num, _ = target_date.isocalendar()
    return f"{year}-W{week_num:02d}"


def load_daily_reports(monday: datetime, sunday: datetime) -> list[dict]:
    """
    指定期間のdaily reportを読み込む
    
    入力: monday, sunday - 対象週の月曜日と日曜日
    出力: daily reportのリスト[{"date": "YYYY-MM-DD", "content": "..."}]
    """
    daily_reports = []
    current_date = monday
    
    while current_date <= sunday:
        date_str = current_date.strftime("%Y-%m-%d")
        report_file = DAILY_REPORTS_DIR / f"{date_str}.md"
        
        if report_file.exists():
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    daily_reports.append({
                        "date": date_str,
                        "content": content
                    })
                print(f"  ✓ {date_str}")
            except Exception as e:
                print(f"  ✗ {date_str} (Error: {e})")
        else:
            print(f"  - {date_str} (Not found)")
        
        current_date += timedelta(days=1)
    
    return daily_reports


def generate_weekly_report(target_date: datetime) -> None:
    """
    指定日を含む週の週報を生成
    
    入力: target_date - 基準日(この日を含む週の週報を生成)
    """
    if not OPENAI_API_KEY:
        print("OpenAI API key not set. Skipping weekly report generation.")
        print("Set it with: export OPENAI_API_KEY=your_key")
        return

    monday, sunday = get_week_date_range(target_date)
    week_str = get_iso_week_string(target_date)
    
    print(f"Generating weekly report for {week_str}")
    print(f"Period: {monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')}")
    print("Loading daily reports:")
    
    daily_reports = load_daily_reports(monday, sunday)
    
    if not daily_reports:
        print("No daily reports found for this week. Skipping weekly report generation.")
        return
    
    print(f"\nFound {len(daily_reports)} daily report(s).")
    
    # daily reportを結合
    combined_content = "\n\n---\n\n".join([
        f"## {report['date']}\n\n{report['content']}"
        for report in daily_reports
    ])
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # 週の表示用文字列
        week_display = f"{monday.strftime('%Y年%m月%d日')}〜{sunday.strftime('%m月%d日')}"
        
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは週報を作成するアシスタントです。1週間分の業務日報から、週報を作成します。",
                },
                {
                    "role": "user",
                    "content": f"""以下は1週間分の業務日報です。これをまとめて週報をMarkdown形式で作成してください。

フォーマット:
# 週報 - {week_display} ({week_str})

## 今週の主な成果
(重要な成果を3〜5項目でまとめる)

## 各日のサマリ
(日付ごとに簡潔にまとめる)

## 使用ツール・技術
(今週使用したアプリケーションやツールを列挙)

## 所感と来週の予定
(1週間の振り返りと来週の予定)

1週間分の業務日報:
{combined_content}
""",
                },
            ],
        )
        
        report_content = response.choices[0].message.content
        
        if report_content:
            report_file = WEEKLY_REPORTS_DIR / f"{week_str}.md"
            
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            print(f"\nWeekly report generated: {report_file}")
    
    except Exception as e:
        print(f"Error generating weekly report: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="macOS Activity Loggerの週報を生成します"
    )
    parser.add_argument(
        "--date",
        help="基準日 (YYYY-MM-DD形式、デフォルト: 今日)",
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    args = parser.parse_args()
    
    try:
        target_date = datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format: {args.date}")
        print("Please use YYYY-MM-DD format")
        exit(1)
    
    generate_weekly_report(target_date)


