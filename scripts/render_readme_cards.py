
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


def main():
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data()
    render_activity(data)
    print("SVG card generation completed!")


if __name__ == "__main__":
    main()
