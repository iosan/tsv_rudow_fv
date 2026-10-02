import importlib.util
import pathlib
import sys
import unittest
from unittest import mock


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "fetch_league_data.py"
SPEC = importlib.util.spec_from_file_location("fetch_league_data", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class FetchLeagueDataTests(unittest.TestCase):
    def test_match_detail_metadata_keeps_german_date_format_for_title_only_dates(self):
        html = """
        <html><head><title>TSV Rudow II - SFC Stern 1900 U23 Ergebnis: Berlin-Pokal - Herren - 03.10.2026</title></head></html>
        """

        with mock.patch.object(module, "fetch_text", return_value=html):
            metadata = module.parse_match_detail_metadata("https://example.test/match")

        self.assertEqual(metadata["dateLabel"], "03.10.2026")
        self.assertEqual(metadata["dateTime"], "2026-10-03T00:00:00")

    def test_enrich_matches_preserves_existing_time_when_detail_has_only_a_date(self):
        matches = [{
            "rowIndex": 0,
            "team": "TSV Rudow II",
            "homeTeam": "TSV Rudow II",
            "awayTeam": "SFC Stern 1900 U23",
            "opponent": "SFC Stern 1900 U23",
            "location": "Heim",
            "dateLabel": "07.10.2026 19:30",
            "dateTime": "2026-10-07T19:30:00",
            "status": "upcoming",
            "score": None,
            "scoreAvailable": False,
            "resultState": None,
            "verifiedMarkup": False,
            "matchUrl": "https://example.test/match",
        }]

        with mock.patch.object(module, "parse_match_detail_metadata", return_value={
            "dateLabel": "03.10.2026",
            "dateTime": "2026-10-03T00:00:00",
        }), mock.patch.object(module, "fetch_match_score_metadata", return_value={
            "score": None,
            "scoreAvailable": False,
            "resultState": None,
        }):
            module.enrich_matches(matches)

        self.assertEqual(matches[0]["dateLabel"], "07.10.2026 19:30")
        self.assertEqual(matches[0]["dateTime"], "2026-10-07T19:30:00")


if __name__ == "__main__":
    unittest.main()
