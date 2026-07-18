"""
fetch_contributions.py
Fetches your public contribution calendar HTML fragment (no GraphQL API,
no personal access token needed) and writes data/contributions.json with
raw days plus derived stats (current streak, longest streak, best day,
monthly totals).

    python scripts/fetch_contributions.py
"""
import json
import os
from datetime import datetime, date
import requests
from bs4 import BeautifulSoup

USERNAME = "sejalraikwa"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT = os.path.join("data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    # GitHub renders each day as a <td> (or <rect> in newer markup) with
    # data-date and either data-level or data-count attributes.
    cells = soup.select("td.ContributionCalendar-day") or soup.select("rect.ContributionCalendar-day")
    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue
        level = cell.get("data-level")
        count = cell.get("data-count")
        # fall back to parsing the tooltip text if attributes are missing
        if count is None:
            tooltip_id = cell.get("aria-labelledby") or cell.get("id")
            count = 0
        days.append({
            "date": d,
            "count": int(count) if count is not None else 0,
            "level": int(level) if level is not None else 0,
        })
    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days):
    if not days:
        return {}

    total = sum(d["count"] for d in days)
    best_day = max(days, key=lambda d: d["count"])

    # current streak: walk backward from the most recent day
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    # longest streak
    longest, running = 0, 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    monthly = {}
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_totals": monthly,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


if __name__ == "__main__":
    days = fetch_days()
    stats = derive_stats(days)
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump({"days": days, "stats": stats}, f, indent=2)
    print(f"Wrote {OUTPUT} ({len(days)} days, {stats.get('total_last_year', 0)} contributions)")
