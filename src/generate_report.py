#!/usr/bin/env python3
"""
Daily Report Generator for macOS Activity Logger

hourly summaryをまとめて業務日報を生成します。
"""

import json
import argparse
from datetime import datetime
from pathlib import Path

from gemini_client import create_gemini_client, generate_content

# Configuration
LOGS_DIR = Path("logs")
REPORTS_DIR = Path("reports/daily")

# Create directories
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


def generate_daily_report(target_date: str) -> None:
    """
    指定日のhourly summaryをまとめて日報を生成

    入力: target_date - 日報作成日 (YYYY-MM-DD形式)
    """
    client = create_gemini_client()
    if not client:
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

    # Parse target_date for display
    try:
        date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        date_display = date_obj.strftime("%Y年%m月%d日")
    except ValueError:
        date_display = target_date

    prompt = f"""あなたは業務日報を作成するアシスタントです。

以下に1日の時間ごとの作業要約を提供します。これらを読んで、業務日報をMarkdown形式で作成してください。

重要：
- 各時間帯には詳細な作業内容が記載されています
- 「作業記録なし」という表現は使用しないでください
- 各時間帯のサマリは、該当時間帯の作業要約の内容を必ず反映してください
- 作業要約が長い場合は、重要な内容を3〜5項目に要約してください

出力フォーマット:
# 業務日報 - {date_display}

## 本日の主な作業
(重要な作業を3〜5項目で簡潔にまとめる)

## 各時間帯の作業内容
- HH:00-HH:59
  - 主な作業内容を箇条書きで（3〜5項目）

## 所感
(1日の振り返りと明日の予定)

---

時間ごとの作業要約:

{summary_text}
"""

    report_content = generate_content(client, prompt)

    if report_content:
        report_file = REPORTS_DIR / f"{target_date}.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"Daily report generated: {report_file}")


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
