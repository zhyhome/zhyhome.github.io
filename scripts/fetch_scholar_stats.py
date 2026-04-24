import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROFILE_ID = "ZIxQLz8AAAAJ"
PROFILE_URL = f"https://scholar.google.com/citations?user={PROFILE_ID}&hl=en"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "assets" / "scholar-stats.json"


def fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")


def parse_total_citations(html: str) -> int:
    stats = re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', html)
    if stats:
        return int(stats[0])

    single_stat = re.search(
        r'Citations</a></td><td class="gsc_rsb_std">(\d+)</td>',
        html,
    )
    if single_stat:
        return int(single_stat.group(1))

    raise ValueError("Could not parse total citations from Google Scholar.")


def write_stats(total_citations: int) -> None:
    payload = {
        "profile_id": PROFILE_ID,
        "total_citations": total_citations,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    try:
        html = fetch_html(PROFILE_URL)
        total_citations = parse_total_citations(html)
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        raise SystemExit(f"Failed to update Google Scholar stats: {exc}") from exc

    write_stats(total_citations)
    print(f"Updated total citations: {total_citations}")


if __name__ == "__main__":
    main()
