#!/usr/bin/env python3
"""Model detection and matrix timing for the original Pi Zero / Pi 1."""

import argparse
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pi_hardware import is_pi_zero_v1, resolve_matrix_timing


def matrix_args(**overrides):
    values = dict(
        led_pwm_bits=None,
        led_pwm_lsb_nanoseconds=None,
        led_slowdown_gpio=None,
        led_limit_refresh=0,
        led_no_pi_tune=False,
        led_rows=32,
        led_cols=64,
        led_chain=1,
    )
    values.update(overrides)
    return argparse.Namespace(**values)


class PiZeroDetection(unittest.TestCase):
    def test_zero_w_rev_1_1(self):
        self.assertTrue(is_pi_zero_v1("Raspberry Pi Zero W Rev 1.1"))

    def test_zero_family_and_pi_1(self):
        self.assertTrue(is_pi_zero_v1("Raspberry Pi Zero Rev 1.3"))
        self.assertTrue(is_pi_zero_v1("Raspberry Pi Zero WH Rev 1.1"))
        self.assertTrue(is_pi_zero_v1("Raspberry Pi Model B Plus Rev 1.2"))
        self.assertTrue(is_pi_zero_v1("Raspberry Pi Compute Module Rev 1.0"))

    def test_later_boards_are_left_alone(self):
        self.assertFalse(is_pi_zero_v1("Raspberry Pi Zero 2 W Rev 1.0"))
        self.assertFalse(is_pi_zero_v1("Raspberry Pi 3 Model B Rev 1.2"))
        self.assertFalse(is_pi_zero_v1("Raspberry Pi 4 Model B Rev 1.1"))
        self.assertFalse(is_pi_zero_v1("Raspberry Pi 5 Model B Rev 1.0"))
        self.assertFalse(is_pi_zero_v1(""))


class PiZeroMatrixTiming(unittest.TestCase):
    def test_defaults_drop_the_refresh_load(self):
        timing = resolve_matrix_timing(matrix_args(), "Raspberry Pi Zero W Rev 1.1")
        self.assertEqual(timing["pwm_bits"], 7)
        self.assertEqual(timing["pwm_lsb_nanoseconds"], 300)
        self.assertEqual(timing["gpio_slowdown"], 0)
        self.assertEqual(timing["limit_refresh_hz"], 100)
        self.assertIn("Raspberry Pi Zero W Rev 1.1", timing["note"])

    def test_explicit_flags_win(self):
        timing = resolve_matrix_timing(
            matrix_args(led_pwm_bits=11, led_slowdown_gpio=2, led_limit_refresh=60),
            "Raspberry Pi Zero W Rev 1.1",
        )
        self.assertEqual(timing["pwm_bits"], 11)
        self.assertEqual(timing["gpio_slowdown"], 2)
        self.assertEqual(timing["limit_refresh_hz"], 60)

    def test_no_pi_tune_keeps_stock_timing(self):
        timing = resolve_matrix_timing(
            matrix_args(led_no_pi_tune=True),
            "Raspberry Pi Zero W Rev 1.1",
        )
        self.assertEqual(timing["pwm_bits"], 11)
        self.assertEqual(timing["pwm_lsb_nanoseconds"], 130)
        self.assertIsNone(timing["gpio_slowdown"])
        self.assertEqual(timing["limit_refresh_hz"], 0)
        self.assertIsNone(timing["note"])

    def test_pi_4_keeps_stock_timing(self):
        timing = resolve_matrix_timing(matrix_args(), "Raspberry Pi 4 Model B Rev 1.1")
        self.assertEqual(timing["pwm_bits"], 11)
        self.assertEqual(timing["pwm_lsb_nanoseconds"], 130)
        self.assertIsNone(timing["gpio_slowdown"])
        self.assertEqual(timing["limit_refresh_hz"], 0)
        self.assertIsNone(timing["note"])

    def test_large_panel_is_called_out(self):
        timing = resolve_matrix_timing(
            matrix_args(led_rows=64, led_cols=128),
            "Raspberry Pi Zero W Rev 1.1",
        )
        self.assertIn("128x64", timing["note"])
        self.assertIn("64x32", timing["note"])


if __name__ == "__main__":
    unittest.main()
