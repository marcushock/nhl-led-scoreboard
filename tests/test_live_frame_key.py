#!/usr/bin/env python3
"""The live scoreboard redraws only when live_frame_key changes."""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from renderer.live_frame import live_frame_key


def team(**overrides):
    values = dict(
        goals=0,
        powerplay=False,
        pp_time_remaining=None,
        num_skaters=5,
        shot_on_goal=0,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def board(away, home, ordinal="1st", clock="12:00", intermission=False):
    return SimpleNamespace(
        away_team=away,
        home_team=home,
        periods=SimpleNamespace(ordinal=ordinal, clock=clock),
        intermission=intermission,
    )


class LiveFrameKey(unittest.TestCase):
    def test_same_stoppage_is_the_same_frame(self):
        away = team(goals=1, shot_on_goal=4)
        home = team(goals=0, shot_on_goal=8)
        first = live_frame_key(board(away, home, clock="5:41"), show_sog=False)
        second = live_frame_key(board(away, home, clock="5:41"), show_sog=False)
        self.assertEqual(first, second)

    def test_clock_score_period_and_power_play_change_the_frame(self):
        away = team(goals=1)
        home = team(goals=0)
        base = live_frame_key(board(away, home), show_sog=False)
        self.assertNotEqual(base, live_frame_key(board(away, home, clock="11:59"), False))
        self.assertNotEqual(base, live_frame_key(board(team(goals=2), home), False))
        self.assertNotEqual(base, live_frame_key(board(away, home, ordinal="2nd"), False))
        self.assertNotEqual(
            base,
            live_frame_key(board(team(goals=1, powerplay=True, pp_time_remaining="1:12", num_skaters=5), team(num_skaters=4)), False),
        )

    def test_shots_matter_only_on_the_shots_page(self):
        away = team(shot_on_goal=3)
        home = team(shot_on_goal=1)
        clock = live_frame_key(board(away, home), show_sog=False)
        clock_again = live_frame_key(board(team(shot_on_goal=9), team(shot_on_goal=9)), show_sog=False)
        shots = live_frame_key(board(away, home), show_sog=True)
        self.assertEqual(clock, clock_again)
        self.assertNotEqual(clock, shots)


if __name__ == "__main__":
    unittest.main()
