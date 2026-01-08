#!/usr/bin/env python3
"""
既存のログとレポートを月ごとのフォルダ構造に移行するスクリプト

Usage:
    python scripts/migrate_to_monthly_folders.py [--dry-run]
"""

import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime


def extract_date_from_filename(filename: str) -> str | None:
    """
    ファイル名から日付(YYYY-MM-DD)を抽出
    
    入力: filename - ファイル名
    出力: YYYY-MM-DD形式の日付、見つからない場合はNone
    """
    # activity_2025-12-23.jsonl や 2025-12-23.md のパターンにマッチ
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None


def get_year_month_from_date(date_str: str) -> tuple[str, str]:
    """
    YYYY-MM-DD形式の日付から年と月を取得
    
    入力: date_str - YYYY-MM-DD形式の日付
    出力: (year, month) - 年(YYYY)と月(MM)のタプル
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.strftime("%Y"), date.strftime("%m")


def migrate_logs(dry_run: bool = False) -> None:
    """
    logsフォルダ内のファイルを月ごとのフォルダに移行
    
    入力: dry_run - Trueの場合は実際には移動せず、移動予定を表示するのみ
    """
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        print(f"Error: {logs_dir} directory not found.")
        return
    
    # 移動対象のファイルパターン
    patterns = ["activity_*.jsonl", "hourly_summary_*.jsonl"]
    
    # 除外するファイル（ログフォルダ直下に残す）
    exclude_files = {"auto_report.log", "launchd_stderr.log", "launchd_stdout.log"}
    
    moved_count = 0
    
    print("\n=== Migrating logs ===")
    
    for pattern in patterns:
        for file_path in logs_dir.glob(pattern):
            # 除外ファイルはスキップ
            if file_path.name in exclude_files:
                continue
            
            # ファイル名から日付を抽出
            date_str = extract_date_from_filename(file_path.name)
            if not date_str:
                print(f"⚠ Skipping {file_path.name} (no date found)")
                continue
            
            # 年月を取得
            year, month = get_year_month_from_date(date_str)
            
            # 移動先ディレクトリを作成
            target_dir = logs_dir / year / month
            target_path = target_dir / file_path.name
            
            if dry_run:
                print(f"[DRY RUN] {file_path} → {target_path}")
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(target_path))
                print(f"✓ Moved: {file_path.name} → {target_dir}")
            
            moved_count += 1
    
    print(f"\nTotal logs files to migrate: {moved_count}")


def migrate_reports(dry_run: bool = False) -> None:
    """
    reports/dailyフォルダ内のファイルを月ごとのフォルダに移行
    
    入力: dry_run - Trueの場合は実際には移動せず、移動予定を表示するのみ
    """
    reports_dir = Path("reports/daily")
    
    if not reports_dir.exists():
        print(f"Error: {reports_dir} directory not found.")
        return
    
    moved_count = 0
    
    print("\n=== Migrating daily reports ===")
    
    for file_path in reports_dir.glob("*.md"):
        # ファイル名から日付を抽出
        date_str = extract_date_from_filename(file_path.name)
        if not date_str:
            print(f"⚠ Skipping {file_path.name} (no date found)")
            continue
        
        # 年月を取得
        year, month = get_year_month_from_date(date_str)
        
        # 移動先ディレクトリを作成
        target_dir = reports_dir / year / month
        target_path = target_dir / file_path.name
        
        if dry_run:
            print(f"[DRY RUN] {file_path} → {target_path}")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(target_path))
            print(f"✓ Moved: {file_path.name} → {target_dir}")
        
        moved_count += 1
    
    print(f"\nTotal report files to migrate: {moved_count}")


def main() -> None:
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="既存のログとレポートを月ごとのフォルダ構造に移行"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際には移動せず、移動予定を表示するのみ",
    )
    args = parser.parse_args()
    
    if args.dry_run:
        print("=" * 60)
        print("DRY RUN MODE - ファイルは移動されません")
        print("=" * 60)
    
    # ログファイルを移行
    migrate_logs(dry_run=args.dry_run)
    
    # レポートファイルを移行
    migrate_reports(dry_run=args.dry_run)
    
    if args.dry_run:
        print("\n" + "=" * 60)
        print("DRY RUN完了。実際に移行する場合は --dry-run を外して実行してください")
        print("=" * 60)
    else:
        print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    main()
