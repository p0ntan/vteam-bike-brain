#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Module for testing the class BatterySimualtor """

import unittest
from src.battery import BatterySimulator


class TestBatterySimulator(unittest.TestCase):
    """ Testclass for testing class BatterySimulator """

    def test_create_without_argument(self):
        """ Creating a Battery and control level """
        battery = BatterySimulator()
        self.assertEqual(battery.level, 1, "Should be 1")
        self.assertLess(battery.level, 1, "Should be less than 1")

    def test_create_with_argument(self):
        """ Creating a Battery with argument and control level """
        level = 0.98
        level_reduction = 0.005
        battery = BatterySimulator(level, level_reduction)

        self.assertEqual(battery.level, 0.98, "Should be 0.98")
        self.assertEqual(
            battery.level, level - level_reduction, "Should be 0.975"
        )

    def test_needs_charging(self):
        """ Creating a Battery and checks if it needs charging """
        battery = BatterySimulator(0.16)
        self.assertFalse(battery.needs_charging(), "Should be False")

        battery_too_low = BatterySimulator(0.14)
        self.assertTrue(battery_too_low.needs_charging(), "Should be True")

    def test_stop_at_zero(self):
        """ Check that battery stops at 0 """
        level = 0.01
        level_reduction = 0.05
        battery = BatterySimulator(level, level_reduction)

        self.assertEqual(battery.level, 0.01, "Should be 0.98")
        self.assertEqual(
            battery.level, 0, "Should be 0"
        )
        self.assertEqual(
            battery.level, 0, "Should be 0"
        )

    def test_stop_at_one(self):
        """ Check that battery stops at 1 """
        level = 0.95
        level_reduction = -0.1
        battery = BatterySimulator(level, level_reduction)

        self.assertEqual(battery.level, 0.95, "Should be 0.95")
        self.assertEqual(
            battery.level, 1, "Should be 1"
        )
        self.assertEqual(
            battery.level, 1, "Should be 1"
        )
