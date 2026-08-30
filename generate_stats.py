#!/usr/bin/env python3
"""freehp AIチームの稼働状況を匿名化してstats.jsonにまとめる。

入力: ~/.threads-watch/ の sent_log.jsonl（送信履歴）と hot_leads_YYYY-MM-DD.json（AI選別結果）。
出力: 件数と日時のみ。ユーザー名・投稿本文・URLなど個人を特定できる情報は一切含めない。
"""
import json
import glob
import os
from datetime import datetime, date

WATCH_DIR = os.path.expanduser("~/.threads-watch")
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats.json")

# 見本URLに含まれるサイトID等も個人情報ではないが、投稿URL・ユーザー名は絶対に出さない。
SENT_LOG = os.path.join(WATCH_DIR, "sent_log.jsonl")


def load_sent_log():
    rows = []
    if not os.path.exists(SENT_LOG):
        return rows
    with open(SENT_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def load_today_hot_leads():
    today = date.today().isoformat()
    path = os.path.join(WATCH_DIR, f"hot_leads_{today}.json")
    if not os.path.exists(path):
        # 今日分がまだ無ければ直近の日付のものを使う
        candidates = sorted(glob.glob(os.path.join(WATCH_DIR, "hot_leads_*.json")))
        if not candidates:
            return [], None
        path = candidates[-1]
    day = os.path.basename(path).replace("hot_leads_", "").replace(".json", "")
    with open(path, encoding="utf-8") as f:
        return json.load(f), day


def bucket(score):
    # A/B/Cの3段階に丸める。しきい値は運用上の目安（4以上=A, 3=B, 2以下=C）。
    if score is None:
        return "C"
    if score >= 4:
        return "A"
    if score >= 3:
        return "B"
    return "C"


def main():
    sent_rows = load_sent_log()
    leads, leads_day = load_today_hot_leads()

    total_sent = len(sent_rows)
    last_sent_at = None
    if sent_rows:
        last_sent_at = max(r.get("at", "") for r in sent_rows if r.get("at"))

    today_str = date.today().isoformat()
    sent_today = sum(1 for r in sent_rows if str(r.get("at", "")).startswith(today_str))

    gift_confirmed = sum(1 for r in sent_rows if r.get("gift_url"))

    counts = {"A": 0, "B": 0, "C": 0}
    for lead in leads:
        counts[bucket(lead.get("score"))] += 1

    stats = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "last_run_at": last_sent_at,
        "total_outreach_count": total_sent,
        "today": {
            "date": today_str,
            "sent_count": sent_today,
        },
        "selection": {
            "date": leads_day,
            "A": counts["A"],
            "B": counts["B"],
            "C": counts["C"],
            "total": len(leads),
        },
        "delivery_confirmed_count": gift_confirmed,
        "daily_send_limit": 3,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
