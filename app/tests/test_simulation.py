#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Module for testing the simulation.
"""

import os
import pytest
from unittest.mock import patch
from src.bike import Bike
from src.battery import BatterySimulator
from src.gps import GpsSimulator
from src.routehandler import RouteHandler


@pytest.fixture
def mock_bike_methods():
    with patch.object(Bike, '_start_renting') as mock_start_renting, \
         patch.object(Bike, '_update_bike_data') as mock_update_data, \
         patch.object(Bike, '_end_renting') as mock_end_renting:
        yield mock_start_renting, mock_update_data, mock_end_renting


@pytest.fixture
def bike_setup_five():
    interval = 5
    base_dir = os.path.dirname(__file__)
    test_directory = os.path.join(base_dir, 'test-data')
    bike_data = {
        'id': 1,
        'city_id': "KSD_TEST",
        'status_id': 1,
        'coords': [13.49476285318039, 59.3790176201388]
    }

    r_handler = RouteHandler(test_directory, interval)
    sim_route = r_handler.routes.get(bike_data.get('id'))
    sim_gps = GpsSimulator(bike_data.get('coords'))
    sim_battery = BatterySimulator()
    bike = Bike(bike_data, sim_battery, sim_gps, sim_route, interval)

    return bike


@pytest.mark.asyncio
async def test_simulation_five(bike_setup_five, mock_bike_methods):
    """ Test to run the simulation, with five second interval. """
    mock_start_renting, mock_update_data, mock_end_renting = mock_bike_methods
    bike = bike_setup_five

    # Adding side_effects to change status, this is done from the server
    # through an SSE in the simulation.
    def start_renting_side_effect(*args, **kwargs):
        bike.set_status(2)
        return True, 1

    def end_renting_side_effect(*args, **kwargs):
        bike.set_status(1)

    mock_start_renting.side_effect = start_renting_side_effect
    mock_end_renting.side_effect = end_renting_side_effect

    await bike.run_simulation()

    mock_start_renting.assert_called()
    mock_end_renting.assert_called()

    data_args = mock_update_data.call_args_list
    for arg_tuple in data_args:
        arg, _ = arg_tuple
        speed = arg[0].get('speed')
        assert speed <= 20


@pytest.mark.asyncio
async def test_simulation_error_response(bike_setup_five, mock_bike_methods):
    """ Test to run the simulation, with error from server when starting trip. """
    mock_start_renting, mock_update_data, mock_end_renting = mock_bike_methods
    bike = bike_setup_five

    def start_renting_side_effect(*args, **kwargs):
        return False, None

    mock_start_renting.side_effect = start_renting_side_effect

    await bike.run_simulation()

    mock_start_renting.assert_called()
    mock_end_renting.assert_not_called()
    mock_update_data.assert_not_called()
