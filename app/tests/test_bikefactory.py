#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Module for testing the class BikeFactory """

from unittest.mock import patch
from src.bike import Bike
from src.bikefactory import BikeFactory


def test_bikefactory():
    """ Test init a Bike with the bikefactory. """
    bike_data = [
        {
            'id': 1,
            'city_id': "GBG",
            'status_id': 1,
            'coords': [18.05767, 59.33464]
        }
    ]

    with patch('src.bike.Bike.update_zones') as mock_update_zones:
        b_factory = BikeFactory(bike_data, routes={})
        bikes = b_factory.bikes

        mock_update_zones.assert_called_once()

    assert isinstance(bikes, dict)
    assert isinstance(bikes.get(1), Bike)
