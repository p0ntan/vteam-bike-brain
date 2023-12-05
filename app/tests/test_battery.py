#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Module for testing the class BatterySimualtor """

import unittest
from src.battery import BatterySimulator


class TestBattery(unittest.TestCase):
    """ Testclass for testing class BatterySimulator """

    def test_create_without_argument(self):
        """ Creating a Battery and control level """
        battery = BatterySimulator()
        self.assertEqual(battery.level, 1, "Should be 1")
        self.assertLess(battery.level, 1, "Should be less than 1")

    def test_create_with_argument(self):
        """ Creating a Battery with argument and control level """
        level = 98
        level_reduction = 0.5
        battery = BatterySimulator(level, level_reduction)

        self.assertEqual(battery.level, 98, "Should be 98")
        self.assertEqual(
            battery.level, level - level_reduction, "Should be 97.5"
        )
