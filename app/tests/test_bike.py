#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Module for testing the class Bike """

import unittest
from src.bike import Bike

class TestBike(unittest.TestCase):
    """ Testclass for testing class Bike """
    
    def test_create_bike(self):
        """ Creating a Bike and checks id """
        bike_data = {
            'id': 1,
            'status': 0,
            'lat': 18.10668,
            'lng': 59.33628
        }

        my_bike = Bike(bike_data)
        self.assertEqual(my_bike.id, 1, "Should be 1")

if __name__ == "__main__":
    print(__name__)
