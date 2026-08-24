#!/usr/bin/env python3
"""Fetch TSV Rudow Herren I/II/III league data from fussball.de.

This script collects:
- current standings row for each team
- one recent match metadata entry (without score)
- one upcoming match metadata entry

Note:
Scores are intentionally obfuscated in the public HTML. This script keeps match
links and metadata and marks score availability accordingly.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import urllib.request
from dataclasses import dataclass
from typing import Any

BASE_URL = "https://www.fussball.de"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class TeamConfig:
    key: str
    name: str
    staffel_id: str


TEAM_CONFIGS = [
    TeamConfig("herren1", "TSV Rudow", "0317AFL2VO000008VS5489BUVSBBVPEU-G"),
    TeamConfig("herren2", "TSV Rudow II", "0317AGKT5S000004VS5489BUVSBBVPEU-G"),
    TeamConfig("herren3", "TSV Rudow III", "0317AGUKM0000006VS5489BUVSBBVPEU-G"),
]

MATCH_META_CACHE: dict[str, dict[str, Any]] = {}


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read().decode("utf-8", errors="replace")


def strip_tags(fragment: str) -> str:
    no_script = re.sub(r"<script[^>]*>.*?</script>", "", fragment, flags=re.I | re.S)
    no_style = re.sub(r"<style[^>]*>.*?</style>", "", no_script, flags=re.I | re.S)
    no_tags = re.sub(r"<[^>]+>", " ", no_style)
    cleaned = html.unescape(no_tags)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def first_int(text: str) -> int | None:
    match = re.search(r"\d+", text)
    if not match:
        return None
    return int(match.group(0))


def parse_standing_row(table_html: str, team_name: str) -> dict[str, Any] | None:
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, flags=re.I | re.S):
        if "club-wrapper" not in row:
            continue

        club_match = re.search(
            r'<a[^>]*class="club-wrapper"[^>]*>(.*?)</a>', row, flags=re.I | re.S
        )
        if not club_match:
            continue

        club_name = normalize_space(strip_tags(club_match.group(1)))
        if club_name != team_name:
            continue

        cell_fragments = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.I | re.S)
        cell_texts = [normalize_space(strip_tags(cell)) for cell in cell_fragments]
        cell_texts = [c for c in cell_texts if c]
        if len(cell_texts) < 9:
            return None

        points_match = re.search(
            r'<td[^>]*class="[^"]*column-points[^"]*"[^>]*>(.*?)</td>',
            row,
            flags=re.I | re.S,
        )
        points = first_int(strip_tags(points_match.group(1))) if points_match else first_int(cell_texts[-1])

        return {
            "team": club_name,
            "rank": first_int(cell_texts[0]),
            "played": first_int(cell_texts[2]),
            "won": first_int(cell_texts[3]),
            "draw": first_int(cell_texts[4]),
            "lost": first_int(cell_texts[5]),
            "goals": cell_texts[6],
            "goalDiff": first_int(cell_texts[7]),
            "points": points,
        }

    return None


def parse_datetime_iso(date_text: str, default_year: int) -> str | None:
    full_date = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", date_text)
    short_date = re.search(r"(\d{2})\.(\d{2})\.", date_text)
    time_match = re.search(r"(\d{1,2}):(\d{2})", date_text)

    if full_date:
        day, month, year = map(int, full_date.groups())
    elif short_date:
        day, month = map(int, short_date.groups())
        year = default_year
    else:
        return None

    hour, minute = (0, 0)
    if time_match:
        hour, minute = map(int, time_match.groups())

    try:
        parsed = dt.datetime(year, month, day, hour, minute)
    except ValueError:
        return None

    return parsed.isoformat()


def parse_match_detail_metadata(match_url: str) -> dict[str, Any]:
    if not match_url:
        return {}

    if match_url in MATCH_META_CACHE:
        return MATCH_META_CACHE[match_url]

    metadata: dict[str, Any] = {}
    try:
        detail_html = fetch_text(match_url)
    except Exception:
        MATCH_META_CACHE[match_url] = metadata
        return metadata

    date_match = re.search(r"am\s+(\d{2}\.\d{2}\.\d{4})(?:\s+(\d{1,2}:\d{2}))?", detail_html)
    if date_match:
        date_part = date_match.group(1)
        time_part = date_match.group(2)
        metadata["dateLabel"] = f"{date_part} {time_part}".strip()
        if time_part:
            metadata["dateTime"] = parse_datetime_iso(f"{date_part} {time_part}", dt.datetime.now().year)
        else:
            metadata["dateTime"] = parse_datetime_iso(date_part, dt.datetime.now().year)

    if "dateTime" not in metadata:
        day_link = re.search(r"/spieldatum/(\d{4}-\d{2}-\d{2})/staffel/", detail_html)
        if day_link:
            yyyy_mm_dd = day_link.group(1)
            metadata["dateLabel"] = yyyy_mm_dd
            metadata["dateTime"] = f"{yyyy_mm_dd}T00:00:00"

    MATCH_META_CACHE[match_url] = metadata
    return metadata


def parse_matches(page_html: str, team_name: str, season_year: int) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []

    for row_index, row in enumerate(re.findall(r"<tr[^>]*>(.*?)</tr>", page_html, flags=re.I | re.S)):
        if "club-wrapper" not in row:
            continue

        club_parts = re.findall(
            r'<a[^>]*class="club-wrapper"[^>]*>(.*?)</a>', row, flags=re.I | re.S
        )
        clubs = [normalize_space(strip_tags(part)) for part in club_parts]
        if len(clubs) < 2 or team_name not in clubs:
            continue

        score_cell = re.search(
            r'<td[^>]*class="[^"]*column-score[^"]*"[^>]*>(.*?)</td>',
            row,
            flags=re.I | re.S,
        )
        score_cell_html = score_cell.group(1) if score_cell else ""
        match_link_match = re.search(r'href="([^"]*?/spiel/[^"]+)"', score_cell_html)
        if not match_link_match:
            match_link_match = re.search(r'href="([^"]*?/spiel/[^"]+)"', row)
        match_url = match_link_match.group(1) if match_link_match else ""
        if match_url.startswith("/"):
            match_url = BASE_URL + match_url

        date_cell_match = re.search(
            r'<td[^>]*class="[^"]*(align-right|column-date)[^"]*"[^>]*>(.*?)</td>',
            row,
            flags=re.I | re.S,
        )
        date_text = normalize_space(strip_tags(date_cell_match.group(2))) if date_cell_match else ""

        home_team = clubs[0]
        away_team = clubs[1]
        is_home = home_team == team_name
        opponent = away_team if is_home else home_team

        iso_datetime = parse_datetime_iso(date_text, season_year)

        status = "unknown"
        if "icon-verified" in row:
            status = "played"
        elif iso_datetime:
            status = "upcoming" if iso_datetime >= dt.datetime.now().isoformat() else "played"

        matches.append(
            {
                "rowIndex": row_index,
                "team": team_name,
                "homeTeam": home_team,
                "awayTeam": away_team,
                "opponent": opponent,
                "location": "Heim" if is_home else "Auswaerts",
                "dateLabel": date_text,
                "dateTime": iso_datetime,
                "status": status,
                "score": None,
                "scoreAvailable": False,
                "matchUrl": match_url,
            }
        )

    # Remove duplicate rows by URL + date + home/away tuple.
    seen: set[tuple[str, str, str, str]] = set()
    unique: list[dict[str, Any]] = []
    for item in matches:
        key = (
            item.get("matchUrl", ""),
            item.get("dateLabel", ""),
            item.get("homeTeam", ""),
            item.get("awayTeam", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    return unique


def enrich_matches(matches: list[dict[str, Any]], limit: int = 12) -> None:
    for item in matches[:limit]:
        detail = parse_match_detail_metadata(item.get("matchUrl", ""))
        if detail.get("dateLabel"):
            item["dateLabel"] = detail["dateLabel"]
        if detail.get("dateTime"):
            item["dateTime"] = detail["dateTime"]

        if item.get("dateTime"):
            item["status"] = "upcoming" if item["dateTime"] >= dt.datetime.now().isoformat() else "played"


def choose_last_and_next(matches: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    now_iso = dt.datetime.now().isoformat()

    with_date = [m for m in matches if m.get("dateTime")]
    with_date.sort(key=lambda m: m["dateTime"])

    played = [m for m in with_date if m["dateTime"] < now_iso or m.get("status") == "played"]
    upcoming = [m for m in with_date if m["dateTime"] >= now_iso and m.get("status") != "played"]

    last_result = played[-1] if played else None
    next_match = upcoming[0] if upcoming else None

    if not last_result:
        played_by_markup = [m for m in matches if m.get("status") == "played"]
        if played_by_markup:
            last_result = played_by_markup[-1]

    if not next_match and last_result and last_result.get("rowIndex") is not None:
        after_last = [m for m in matches if m.get("rowIndex", -1) > last_result["rowIndex"]]
        if after_last:
            next_match = after_last[0]

    if not next_match:
        unknown = [m for m in matches if m.get("status") != "played"]
        if unknown:
            next_match = unknown[0]

    return last_result, next_match


def build_team_payload(config: TeamConfig) -> dict[str, Any]:
    table_url = f"{BASE_URL}/ajax.actual.table/-/staffel/{config.staffel_id}"
    fixtures_url = f"{BASE_URL}/spielplan/-/staffel/{config.staffel_id}"

    table_html = fetch_text(table_url)
    fixture_html = fetch_text(fixtures_url)

    standing = parse_standing_row(table_html, config.name)
    season_year = dt.datetime.now().year
    matches = parse_matches(fixture_html, config.name, season_year)
    enrich_matches(matches)
    last_result, next_match = choose_last_and_next(matches)

    return {
        "key": config.key,
        "name": config.name,
        "staffelId": config.staffel_id,
        "tableUrl": table_url,
        "fixturesUrl": fixtures_url,
        "standing": standing,
        "lastResult": last_result,
        "nextMatch": next_match,
        "matchesPreview": matches[:6],
    }


def build_homepage_projection(teams: list[dict[str, Any]]) -> dict[str, Any]:
    table_rows = []
    recent_results = []
    upcoming_matches = []

    for team in teams:
        standing = team.get("standing") or {}
        table_rows.append(
            {
                "team": team["name"],
                "rank": standing.get("rank"),
                "played": standing.get("played"),
                "points": standing.get("points"),
                "goalDiff": standing.get("goalDiff"),
            }
        )

        last_result = team.get("lastResult")
        if last_result:
            recent_results.append(
                {
                    "team": team["name"],
                    "opponent": last_result.get("opponent"),
                    "dateLabel": last_result.get("dateLabel"),
                    "score": None,
                    "scoreAvailable": False,
                    "matchUrl": last_result.get("matchUrl"),
                }
            )

        next_match = team.get("nextMatch")
        if next_match:
            upcoming_matches.append(
                {
                    "team": team["name"],
                    "dateLabel": next_match.get("dateLabel"),
                    "opponent": next_match.get("opponent"),
                    "location": next_match.get("location"),
                    "matchUrl": next_match.get("matchUrl"),
                }
            )

    return {
        "tableRows": table_rows,
        "recentResults": recent_results,
        "upcomingMatches": upcoming_matches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch TSV Rudow league data")
    parser.add_argument(
        "--output",
        default="html/data/league-data.json",
        help="Path to generated JSON (default: html/data/league-data.json)",
    )
    args = parser.parse_args()

    teams = [build_team_payload(config) for config in TEAM_CONFIGS]

    payload = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": {
            "provider": "fussball.de",
            "method": "public-html-endpoints",
            "note": "Scores in public HTML are obfuscated; metadata and links are exported.",
        },
        "teams": teams,
        "homepage": build_homepage_projection(teams),
    }

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    js_output = os.path.splitext(args.output)[0] + ".js"
    with open(js_output, "w", encoding="utf-8") as handle:
        handle.write("window.__LEAGUE_DATA__ = ")
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2))
        handle.write(";\n")

    print(f"Wrote {args.output}")
    print(f"Wrote {js_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
