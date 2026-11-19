
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "contributions.json"
CARDS_DIR = ROOT / "cards"

STATIC = os.getenv("STATIC", "0") == "1"


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def render_activity(data):
    total = data.get("total_contributions", 0)
    streak = data.get("current_streak", 0)
    active = data.get("active_days", 0)

    animation = "" if STATIC else """
    <animate attributeName="opacity"
      values="0.3;1;0.3"
      dur="3s"
      repeatCount="indefinite"/>
    """

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
      width="900" height="240" viewBox="0 0 900 240">

      <defs>
        <linearGradient id="bg">
          <stop stop-color="#080B14"/>
          <stop offset="1" stop-color="#14213D"/>
        </linearGradient>
      </defs>

      <rect width="900" height="240" rx="22" fill="url(#bg)"/>
      <rect x="1" y="1" width="898" height="238"
        rx="21" stroke="#263B65"/>

      <text x="40" y="55" fill="#60A5FA"
        font-size="15" font-family="monospace">
        GITHUB ACTIVITY
      </text>

      <text x="40" y="110" fill="white"
        font-size="34" font-weight="bold"
        font-family="Arial">{total}</text>
      <text x="40" y="140" fill="#94A3B8"
        font-size="15" font-family="Arial">
        Total contributions
      </text>

      <text x="350" y="110" fill="#38BDF8"
        font-size="34" font-weight="bold"
        font-family="Arial">{streak}</text>
      <text x="350" y="140" fill="#94A3B8"
        font-size="15" font-family="Arial">
        Current streak
      </text>

      <text x="650" y="110" fill="#818CF8"
        font-size="34" font-weight="bold"
        font-family="Arial">{active}</text>
      <text x="650" y="140" fill="#94A3B8"
        font-size="15" font-family="Arial">
        Active days
      </text>

      <circle cx="850" cy="45" r="5" fill="#38BDF8">
        {animation}
      </circle>
    </svg>'''

    output = CARDS_DIR / "activity.svg"
    output.write_text(svg, encoding="utf-8")
    print(f"Generated: {output}")
def render_streak(data):
    current = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    active = data.get("active_days", 0)
    busiest = data.get("busiest_day", "Not available")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
      width="900" height="240" viewBox="0 0 900 240">

      <defs>
        <linearGradient id="streakBg">
          <stop stop-color="#111827"/>
          <stop offset="1" stop-color="#312E81"/>
        </linearGradient>
      </defs>

      <rect width="900" height="240" rx="22"
        fill="url(#streakBg)"/>

      <text x="40" y="50" fill="#A5B4FC"
        font-size="16" font-family="Arial">
        CONTRIBUTION STREAK
      </text>

      <text x="40" y="115" fill="white"
        font-size="38" font-weight="bold"
        font-family="Arial">{current}</text>
      <text x="40" y="145" fill="#CBD5E1"
        font-size="15" font-family="Arial">
        Current streak
      </text>

      <text x="330" y="115" fill="#FBBF24"
        font-size="38" font-weight="bold"
        font-family="Arial">{longest}</text>
      <text x="330" y="145" fill="#CBD5E1"
        font-size="15" font-family="Arial">
        Longest streak
      </text>

      <text x="620" y="115" fill="#67E8F9"
        font-size="38" font-weight="bold"
        font-family="Arial">{active}</text>
      <text x="620" y="145" fill="#CBD5E1"
        font-size="15" font-family="Arial">
        Active days
      </text>

      <text x="40" y="200" fill="#94A3B8"
        font-size="14" font-family="Arial">
        Busiest contribution weekday: {busiest}
      </text>
    </svg>'''

    output = CARDS_DIR / "streak.svg"
    output.write_text(svg, encoding="utf-8")
    print(f"Generated: {output}")
def render_heatmap(data):
    days = data.get("weeks", [])

   cell = 11
   gap = 3
   start_x = 70
   start_y = 62

    colors = [
        "#161B22",
        "#0E4429",
        "#006D32",
        "#26A641",
        "#39D353"
    ]

    squares = []

    for index, day in enumerate(days):
        weekday = day.get("weekday", 0)
       week = (index + days[0].get("weekday", 0)) // 7

        x = start_x + week * (cell + gap)
        y = start_y + weekday * (cell + gap)

        count = day.get("count", 0)

        if count == 0:
            color = colors[0]
        elif count <= 2:
            color = colors[1]
        elif count <= 5:
            color = colors[2]
        elif count <= 9:
            color = colors[3]
        else:
            color = colors[4]

        squares.append(
            f'<rect x="{x}" y="{y}" width="{cell}" '
            f'height="{cell}" rx="2" fill="{color}">'
            f'<title>{day.get("date", "")}: {count} contributions</title>'
            f'</rect>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
      width="900" height="195" viewBox="0 0 900 195"

      <rect width="900" height="180" rx="18"
        fill="#080B14"/>

      <text x="35" y="35" fill="#60A5FA"
        font-size="16" font-family="Arial">
        CONTRIBUTION HEATMAP
      </text>

      {''.join(squares)}

      <text x="70" y="178" fill="#94A3B8"
        font-size="12" font-family="Arial">
        Last 365 days of GitHub activity
      </text>
    </svg>'''

    output = CARDS_DIR / "heatmap.svg"
    output.write_text(svg, encoding="utf-8")
    print(f"Generated: {output}")
def main():
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data()
    render_activity(data)
    render_streak(data)
    render_heatmap(data)
    print("SVG card generation completed!")


if __name__ == "__main__":
    main()
