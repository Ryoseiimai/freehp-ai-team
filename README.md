# freehp AIチーム 組織図サイト

freehp AIチームの体制と稼働状況を見せる公開ページ。単一HTML（`index.html`）+ 静的JSON（`stats.json`）。

## 構成

- `index.html` — 単一ページ。ヒーロー / 組織図 / 無人パイプライン / 稼働状況（stats.jsonをfetch）/ フッター。
- `generate_stats.py` — `~/.threads-watch/` の `sent_log.jsonl`（送信履歴）と `hot_leads_YYYY-MM-DD.json`（AI選別結果）から匿名化した `stats.json` を生成する。ユーザー名・投稿本文・URLは一切出力しない。件数と日時のみ。
- `stats.json` — 生成済みの稼働状況データ。公開時はこのファイルを一緒にデプロイする。

## 更新方法

```bash
cd ~/dev/2026-08-31-freehp-ai-org-site
python3 generate_stats.py
```

`stats.json` が上書きされる。定期実行にする場合はlaunchdやcronから叩けばよい（このディレクトリの外に副作用は出ない）。

## ローカル確認

```bash
cd ~/dev/2026-08-31-freehp-ai-org-site
python3 -m http.server 8901
# ブラウザで http://localhost:8901/ を開く
```

## 注意

- `stats.json` に個人を特定できる情報（相手のユーザー名・投稿本文・URL）を混ぜないこと。件数と日時だけに保つ。
- A/B/C の区分は `hot_leads_*.json` の `score` を丸めたもの（4以上=A, 3=B, 2以下=C）。
