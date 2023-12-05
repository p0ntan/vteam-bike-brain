#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Module for testing the class GpsSimulator """

import unittest
from src.gps import GpsSimulator


class TestGps(unittest.TestCase):
    """ Testclass for testing class GpsSimulator """

    def test_create_gps(self):
        """ Creating a Gps and get position """
        position = [13.508699207322167, 59.38210003526896]
        gps_sim = GpsSimulator(position)

        self.assertEqual(gps_sim.position, position, "Should be same as input position")

    def test_change_position(self):
        """ Creating a Gps and chaning position to get speed """
        # Distance between positions is 200 meters
        first_position = [13.508699207322167, 59.38210003526896]
        second_position = [13.505173887431198, 59.38216072603788]

        time_in_seconds = 20
        gps_sim = GpsSimulator(first_position)

        gps_sim.position = (second_position, time_in_seconds)
        self.assertEqual(gps_sim.position, second_position, "Should be same as second position")
        self.assertAlmostEqual(gps_sim.speed, 36, "Should be 36")

        gps_sim.position = (second_position, time_in_seconds)
        self.assertAlmostEqual(gps_sim.speed, 0, "Should be 0")

        time_in_seconds = 200
        gps_sim.position = (first_position, time_in_seconds)
        self.assertAlmostEqual(gps_sim.speed, 4, "Should be 4 (3.6 rounded up)")
