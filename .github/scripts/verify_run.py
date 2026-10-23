"""Fail the workflow when no fresh news or HTML was generated."""
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

now = datetime.now(ZoneInfo("Asia/Shanghai"))
db = Path("output/news") / f"{now:%Y-%m-%d}.db"
if not db.is_file():
    raise SystemExit("No database was generated for today")
with sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True) as conn:
    if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
        raise SystemExit("SQLite integrity check failed")
    latest = conn.execute("SELECT id, crawl_time, total_items FROM crawl_records ORDER BY id DESC LIMIT 1").fetchone()
    if latest is None or latest[2] <= 0:
        raise SystemExit("The latest crawl returned no news")
    statuses = dict(conn.execute("SELECT status, count(*) FROM crawl_source_status WHERE crawl_record_id=? GROUP BY status", (latest[0],)))
    if not statuses.get("success"):
        raise SystemExit("No hotlist platform succeeded")
report = Path("index.html")
if not report.is_file() or report.stat().st_size < 1000:
    raise SystemExit("No HTML report was generated")
if report.read_bytes() != Path("output/index.html").read_bytes():
    raise SystemExit("The entry report does not match the generated report")
result = {"date": now.strftime("%Y-%m-%d"), "crawl_time": latest[1], "news_items": latest[2], "platforms": statuses, "report_bytes": report.stat().st_size}
print(json.dumps(result, ensure_ascii=False))
if statuses.get("failed"):
    print(f"::warning::{statuses['failed']} hotlist platforms failed; see crawler logs")
summary = os.environ.get("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary, "a", encoding="utf-8") as f:
        f.write("### TrendRadar trial results\n\n```json\n" + json.dumps(result, ensure_ascii=False, indent=2) + "\n```\n")
