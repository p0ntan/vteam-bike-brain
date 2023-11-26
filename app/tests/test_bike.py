#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Module for testing the class Bike """

import unittest
from src.bike import Bike
from src.battery import BatterySimulator
from src.gps import GpsSimulator

class TestBike(unittest.TestCase):
    """ Testclass for testing class Bike """

    def test_create_bike(self):
        """ Creating a Bike and checks data """
        bike_data = {
            'id': 1,
            'status': 1,
            'position': [13.508699207322167, 59.38210003526896],
        }

        gps_sim = GpsSimulator(bike_data['position'])
        battery_sim = BatterySimulator()

        bike_instance = Bike(bike_data, battery_sim, gps_sim)
        data_from_bike = bike_instance.get_data()
        self.assertIsInstance(data_from_bike, dict, "Should be a dictionary")
        # Check that data has all the right keys and values
        # id
        self.assertIn('id', data_from_bike, "Should have key id")
        self.assertIsInstance(data_from_bike['id'], int, "Should be an integer")
        # status
        self.assertIn('status', data_from_bike, "Should have key status")
        self.assertIsInstance(data_from_bike['status'], int, "Should be an integer")
        # battery_level
        self.assertIn('battery_level', data_from_bike, "Should have key battery_level")
        self.assertIsInstance(data_from_bike['battery_level'], int, "Should be an integer")
        # position
        self.assertIn('position', data_from_bike, "Should have key position")
        self.assertIsInstance(data_from_bike['position'], list, "Should be a list")
        self.assertIsInstance(data_from_bike['position'][0], float, "Should be a float")
        self.assertIsInstance(data_from_bike['position'][1], float, "Should be a float")
        # speed
        self.assertIn('speed', data_from_bike, "Should have key speed")
        self.assertIsInstance(data_from_bike['speed'], int, "Should be an integer")

    def test_moving_bike(self):
        """ Update position for a bike, see that it sends out speed and new position """
        bike_data = {
            'id': 1,
            'status': 1,
            'position': [13.508699207322167, 59.38210003526896],
        }
        gps_sim = GpsSimulator(bike_data['position'])
        battery_sim = BatterySimulator()
        bike_instance = Bike(bike_data, battery_sim, gps_sim)

        data_from_bike = bike_instance.get_data()
        self.assertEqual(data_from_bike['speed'], 0, "Should be 0")
        self.assertEqual(data_from_bike['position'], bike_data['position'], "Should be an list of coordinates")

        new_position = [13.505173887431198, 59.38216072603788] # 200 meters between this and original position
        interval_in_seconds = 10

        # Forcing new position on private variable, disableing pylint for this action
        # pylint: disable=protected-access
        bike_instance._gps.position = (new_position, interval_in_seconds)
        data_from_bike = bike_instance.get_data()

        self.assertEqual(data_from_bike['speed'], 72, "Should be 72") # 200 meters in 10 sek = 72 km/h
        self.assertEqual(data_from_bike['position'], new_position, "Should be an list of coordinates")
