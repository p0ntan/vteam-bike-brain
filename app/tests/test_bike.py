#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Module for testing the class Bike """

import unittest
from src.bike import Bike
from src.battery import BatterySimulator
from src.gps import GpsSimulator


class TestBike(unittest.TestCase):
    """ Testclass for testing class Bike """
    BIKE_DATA = {
        'id': 1,
        'city_id': 'STHLM',
        'status_id': 1,
        'coords': [13.508699207322167, 59.38210003526896],
    }

    def test_create_bike(self):
        """ Creating a Bike and checks data """
        gps_sim = GpsSimulator(self.BIKE_DATA['coords'])
        battery_sim = BatterySimulator()

        bike_instance = Bike(self.BIKE_DATA, battery_sim, gps_sim)
        data_from_bike = bike_instance.get_data()
        self.assertIsInstance(data_from_bike, dict, "Should be a dictionary")
        # Check that data has all the right keys and values
        # id
        self.assertIn('id', data_from_bike, "Should have key id")
        self.assertIsInstance(data_from_bike['id'], int, "Should be an integer")
        # status_id
        self.assertIn('status_id', data_from_bike, "Should have key status")
        self.assertIsInstance(data_from_bike['status_id'], int, "Should be an integer")
        # charge_perc
        self.assertIn('charge_perc', data_from_bike, "Should have key charge_perc")
        self.assertIsInstance(data_from_bike['charge_perc'], float, "Should be a float")
        # coords
        self.assertIn('coords', data_from_bike, "Should have key coords")
        self.assertIsInstance(data_from_bike['coords'], list, "Should be a list")
        self.assertIsInstance(data_from_bike['coords'][0], float, "Should be a float")
        self.assertIsInstance(data_from_bike['coords'][1], float, "Should be a float")
        # speed
        self.assertIn('speed', data_from_bike, "Should have key speed")
        self.assertIsInstance(data_from_bike['speed'], int, "Should be an integer")

    def test_moving_bike(self):
        """ Update position for a bike, see that it sends out speed and new position """
        gps_sim = GpsSimulator(self.BIKE_DATA['coords'])
        battery_sim = BatterySimulator()
        bike_instance = Bike(self.BIKE_DATA, battery_sim, gps_sim)

        data_from_bike = bike_instance.get_data()
        self.assertEqual(data_from_bike['speed'], 0, "Should be 0")
        self.assertEqual(data_from_bike['coords'], self.BIKE_DATA['coords'], "Should be an list of coordinates")

        new_position = [13.505173887431198, 59.38216072603788]  # 200 meters between this and original position
        interval_in_seconds = 10

        # Forcing new position on private variable, disableing pylint for this action
        # pylint: disable=protected-access
        bike_instance._gps.position = (new_position, interval_in_seconds)
        data_from_bike = bike_instance.get_data()

        self.assertEqual(data_from_bike['speed'], 72, "Should be 72")  # 200 meters in 10 sek = 72 km/h
        self.assertEqual(data_from_bike['coords'], new_position, "Should be an list of coordinates")
