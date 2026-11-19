
import json
import os
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT / "data" / "contributions.json"

USERNAME = os.getenv("GITHUB_USERNAME", "Vignesh-5120")
TOKEN = os.getenv("GH_TOKEN")

if not TOKEN:
    raise RuntimeError("GH_TOKEN secret is missing.")


def fetch_contributions():
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=364)

    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
                weekday
              }
            }
          }
        }
      }
    }
    """

    payload = {
        "query": query,
        "variables": {
            "username": USERNAME,
            "from": start.isoformat() + "T00:00:00Z",
            "to": (today + timedelta(days=1)).isoformat() + "T00:00:00Z"
        }
    }

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "Vignesh-GitHub-Profile"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    if result.get("errors"):
        raise RuntimeError(
            f"GitHub GraphQL error: {result['errors']}"
        )

    user = result.get("data", {}).get("user")
    if not user:
        raise RuntimeError(f"GitHub user not found: {USERNAME}")

    calendar = user["contributionsCollection"]["contributionCalendar"]

    days = []
    for week in calendar["weeks"]:
        for item in week["contributionDays"]:
            days.append({
                "date": item["date"],
                "count": item["contributionCount"],
                "weekday": item["weekday"]
            })

    return calendar["totalContributions"], days


def calculate_streaks(days, today):
    counts = {
        date.fromisoformat(item["date"]): item["count"]
        for item in days
    }

    longest = 0
    running = 0

    for item in days:
        if item["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    current = 0
    check_day = today

    # If today has no contributions yet, start from yesterday.
    if counts.get(check_day, 0) == 0:
        check_day -= timedelta(days=1)

    while counts.get(check_day, 0) > 0:
        current += 1
        check_day -= timedelta(days=1)

    return current, longest


def build_data():
    today = datetime.now(timezone.utc).date()
    total, days = fetch_contributions()

    current, longest = calculate_streaks(days, today)

    active_days = sum(1 for day in days if day["count"] > 0)

    monthly = Counter()
    weekdays = Counter()

    for item in days:
        if item["count"] > 0:
            monthly[item["date"][:7]] += item["count"]
            weekdays[item["weekday"]] += item["count"]

    busiest_day = (
        weekdays.most_common(1)[0][0]
        if weekdays else "Not available"
    )

    months = [
        {"month": month, "contributions": count}
        for month, count in sorted(monthly.items())
    ]

    return {
        "username": USERNAME,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": total,
        "current_streak": current,
        "longest_streak": longest,
        "active_days": active_days,
        "busiest_day": busiest_day,
        "months": months,
        "weeks": days
    }


def main():
    data = build_data()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

    print("Contribution data updated successfully!")
    print("Total contributions:", data["total_contributions"])
    print("Current streak:", data["current_streak"])
    print("Longest streak:", data["longest_streak"])


if __name__ == "__main__":
    main()

