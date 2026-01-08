#!/usr/bin/env python3
"""
Weekly Report Generator for macOS Activity Logger

今週のdaily reportをまとめて週報を生成します。
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path

from gemini_client import create_gemini_client, generate_content

# Configuration
DAILY_REPORTS_DIR = Path("reports/daily")
WEEKLY_REPORTS_DIR = Path("reports/weekly")

# Create directories
DAILY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
WEEKLY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def get_monthly_reports_dir(date: datetime) -> Path:
    """
    指定日の月ごとのレポートディレクトリを取得

    入力: date - 対象日時
    出力: 月ごとのレポートディレクトリパス (例: reports/daily/2026/01/)
    """
    return DAILY_REPORTS_DIR / date.strftime("%Y") / date.strftime("%m")


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


def get_daily_report_files(monday: datetime, sunday: datetime) -> list[dict]:
    """
    指定期間のdaily reportファイルパスを取得

    入力: monday, sunday - 対象週の月曜日と日曜日
    出力: daily reportのリスト[{"date": "YYYY-MM-DD", "file_path": Path}]
    """
    daily_reports = []
    current_date = monday

    while current_date <= sunday:
        date_str = current_date.strftime("%Y-%m-%d")
        monthly_dir = get_monthly_reports_dir(current_date)
        report_file = monthly_dir / f"{date_str}.md"

        if report_file.exists():
            daily_reports.append({"date": date_str, "file_path": report_file})
            print(f"  ✓ {date_str}")
        else:
            print(f"  - {date_str} (Not found)")

        current_date += timedelta(days=1)

    return daily_reports


def read_daily_reports_content(daily_reports: list[dict]) -> str:
    """
    日次レポートファイルの内容を読み込んで結合

    入力:
        daily_reports - [{"date": "YYYY-MM-DD", "file_path": Path}]
    出力:
        結合されたMarkdownテキスト
    """
    contents = []

    print("\nReading daily reports:")
    for report in daily_reports:
        date_str = report["date"]
        file_path = report["file_path"]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                contents.append(f"## {date_str}\n\n{content}")
                print(f"  ✓ Read {date_str}.md ({len(content)} chars)")
        except Exception as e:
            print(f"  ✗ Failed to read {date_str}.md: {e}")

    return "\n\n---\n\n".join(contents)


def generate_weekly_report(target_date: datetime) -> None:
    """
    指定日を含む週の週報を生成

    入力: target_date - 基準日(この日を含む週の週報を生成)
    """
    client = create_gemini_client()
    if not client:
        return

    monday, sunday = get_week_date_range(target_date)
    week_str = get_iso_week_string(target_date)

    print(f"Generating weekly report for {week_str}")
    print(f"Period: {monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')}")
    print("Finding daily reports:")

    daily_reports = get_daily_report_files(monday, sunday)

    if not daily_reports:
        print(
            "No daily reports found for this week. Skipping weekly report generation."
        )
        return

    print(f"\nFound {len(daily_reports)} daily report(s).")

    # 日次レポートの内容を読み込み
    combined_content = read_daily_reports_content(daily_reports)

    # 週の表示用文字列
    week_display = f"{monday.strftime('%Y年%m月%d日')}〜{sunday.strftime('%m月%d日')}"

    # プロンプトを作成
    prompt = f"""あなたは週報を作成するアシスタントです。

以下に1週間分の日次レポート（Markdownファイル）を提供します。これらを読んで、週報をMarkdown形式で作成してください。

重要：
- 各日次レポートには詳細な作業内容が記載されています
- 「作業記録なし」という表現は使用しないでください
- 各日のサマリは、該当日の日次レポートの内容を必ず反映してください
- 日次レポートが長い場合は、重要な内容を3〜5項目に要約してください

出力フォーマット:
# 週報 - {week_display} ({week_str})

## 今週の成果
(重要な成果を3〜5項目で簡潔にまとめる)

## 各日の作業内容
- YYYY-MM-DD
  - 主な作業内容を箇条書きで（3〜5項目）

## 所感
(1週間の振り返り)

---

1週間分の日次レポート:

{combined_content}
"""

    print(f"\nGenerating weekly report... (prompt length: {len(prompt)} chars)")

    report_content = generate_content(client, prompt)

    if report_content:
        report_file = WEEKLY_REPORTS_DIR / f"{week_str}.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"\nWeekly report generated: {report_file}")


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
