"""Unit tests for gen_stats (stdlib unittest: `python3 -m unittest discover scripts`)."""
from __future__ import annotations

import datetime as dt
import random
import sys
import unittest
import xml.dom.minidom
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_stats as gs  # noqa: E402
from svgkit import DARK  # noqa: E402


def fake_payload(seed: int = 7, today: dt.date = dt.date(2026, 9, 11)) -> dict:
    rnd = random.Random(seed)
    start = today - dt.timedelta(days=370)
    days = [{"date": (start + dt.timedelta(days=i)).isoformat(),
             "contributionCount": rnd.choice([0, 0, 1, 2, 3, 5, 8, 13])} for i in range(371)]
    weeks = [{"contributionDays": days[i:i + 7]} for i in range(0, len(days), 7)]
    return {
        "login": "octo", "name": "Octo", "generated_at": f"{today.isoformat()}T10:00:00+00:00",
        "followers": {"totalCount": 12}, "pullRequests": {"totalCount": 34}, "issues": {"totalCount": 5},
        "contributionsCollection": {
            "totalCommitContributions": 900, "restrictedContributionsCount": 300,
            "totalPullRequestContributions": 30, "totalPullRequestReviewContributions": 11,
            "totalIssueContributions": 4,
            "contributionCalendar": {"totalContributions": sum(d["contributionCount"] for d in days), "weeks": weeks},
        },
        "commit_times": [f"2026-09-{d:02d}T{h:02d}:15:00Z" for d in range(1, 11) for h in (4, 16, 17, 20)],
        "repos": [
            {"stargazerCount": 3, "forkCount": 0, "languages": {"edges": [
                {"size": 5000, "node": {"name": "PHP", "color": "#4F5D95"}},
                {"size": 2000, "node": {"name": "Blade", "color": "#f7523f"}}]}},
            {"stargazerCount": 1, "forkCount": 0, "languages": {"edges": [
                {"size": 3000, "node": {"name": "Python", "color": "#3572A5"}},
                {"size": 10, "node": {"name": "<script>", "color": "javascript:alert(1)"}}]}},
        ],
    }


class StreakTests(unittest.TestCase):
    def test_today_zero_does_not_break_streak(self):
        d = dt.date(2026, 1, 10)
        days = [(d - dt.timedelta(days=i), n) for i, n in enumerate([0, 1, 1, 0, 1])][::-1]
        self.assertEqual(gs.streaks(days, d), (2, 2))

    def test_longest(self):
        d = dt.date(2026, 1, 10)
        days = [(d - dt.timedelta(days=i), n) for i, n in enumerate([1, 0, 1, 1, 1, 0])][::-1]
        self.assertEqual(gs.streaks(days, d), (1, 3))


class AggregateTests(unittest.TestCase):
    def test_aggregate_and_exclude(self):
        s = gs.aggregate(fake_payload(), exclude={"blade"})
        names = [n for n, _, _ in s.langs]
        self.assertNotIn("Blade", names)
        self.assertAlmostEqual(sum(sh for *_, sh in s.langs), 1.0, places=6)
        self.assertEqual(s.commits, 1200)
        self.assertEqual(s.stars, 4)

    def test_untrusted_values_are_escaped_and_colours_sanitised(self):
        s = gs.aggregate(fake_payload(), exclude=set())
        svg = gs.langs_card(s, DARK)
        self.assertNotIn("<script>", svg)
        self.assertNotIn("javascript:", svg)
        xml.dom.minidom.parseString(svg)   # well-formed

    def test_all_cards_are_valid_xml(self):
        s = gs.aggregate(fake_payload(), exclude=set())
        for fn in (gs.stats_card, gs.langs_card, gs.activity_card, gs.pulse_card):
            xml.dom.minidom.parseString(fn(s, DARK))


class PulseTests(unittest.TestCase):
    def test_hours_are_bucketed_in_ist(self):
        s = gs.aggregate(fake_payload(), exclude=set())
        # 16:15Z -> 21:45 IST, 17:15Z -> 22:45 IST, 04:15Z -> 09:45, 20:15Z -> 01:45
        self.assertEqual(s.hours[21], 10)
        self.assertEqual(s.hours[22], 10)
        self.assertEqual(s.hours[9], 10)
        self.assertEqual(s.hours[1], 10)
        self.assertEqual(s.commits_90d, 40)

    def test_peak_window_wraps_midnight(self):
        hours = [0] * 24
        hours[23] = hours[0] = hours[1] = 5
        self.assertEqual(gs.peak_window(hours), 23)

    def test_missing_commit_times_is_tolerated(self):
        raw = fake_payload()
        raw.pop("commit_times")
        s = gs.aggregate(raw, exclude=set())
        self.assertEqual(sum(s.hours), 0)
        xml.dom.minidom.parseString(gs.pulse_card(s, DARK))


class HumanTests(unittest.TestCase):
    def test_human(self):
        self.assertEqual([gs.human(x) for x in (7, 1000, 1540, 12_345, 2_000_000)], ["7", "1k", "1.5k", "12k", "2M"])


if __name__ == "__main__":
    unittest.main()
