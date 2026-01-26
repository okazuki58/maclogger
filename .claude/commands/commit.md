# コミット＆プッシュ

ステージされた変更をコミットし、リモートにプッシュするコマンドです。

## 実行手順

1. `git status` で現在の状態を確認
2. `git diff --cached` でステージされた変更を確認
3. 変更内容を分析し、conventional commit形式のコミットメッセージを**英語**で生成
4. コミットを実行
5. リモートにプッシュ

## コミットメッセージの要件

- 形式: `{type}: {imperative verb} {what}`
- 一行で完結（50文字以内推奨）
- 動詞は命令形（add, fix, update, remove など）
- 詳細は不要。WHYが重要な場合のみ本文を追加

## 例

- `feat: add weekly report generation`
- `fix: correct date calculation in parser`
- `refactor: extract validation logic to util`

## 注意事項

- ステージされた変更がない場合は、何をステージすべきか確認する
- プッシュ先のブランチが存在しない場合は `-u` オプションで追跡設定する
- コンフリクトがある場合は警告して停止する
