#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Module for testing the simulation.

This is more of an integration test since since the simulation is using
multiple classes to work.
"""

import os
import pytest
from unittest.mock import patch
from src.bike import Bike
from src.battery import BatterySimulator
from src.gps import GpsSimulator
from src.routehandler import RouteHandler


class MockedResponse:
    """ Class used as mocking repsonse from server when using aiohttp. """
    def __init__(self, json_data, status):
        self._json_data = json_data
        self.status = status

    async def json(self):
        return self._json_data

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


@pytest.fixture
def mock_bike_methods():
    with patch.object(Bike, '_update_bike_data') as mock_update_data, \
         patch.object(Bike, '_end_renting') as mock_end_renting:
        yield mock_update_data, mock_end_renting


@pytest.fixture
def bike_setup():
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
async def test_simulation_five(bike_setup, mock_bike_methods):
    """ Test to run the simulation, with five second interval. """
    mock_update_data, mock_end_renting = mock_bike_methods
    bike = bike_setup

    def post_side_effect(*args, **kwargs):
        response = MockedResponse(json_data={'trip_id': 123}, status=200)
        bike.set_status(2)
        return response

    def end_renting_side_effect(*args, **kwargs):
        bike.set_status(1)

    # mock_start_renting.side_effect = start_renting_side_effect
    mock_end_renting.side_effect = end_renting_side_effect

    with patch('aiohttp.ClientSession.post', side_effect=post_side_effect):
        await bike.run_simulation()

    # mock_start_renting.assert_called()
    mock_end_renting.assert_called()

    data_args = mock_update_data.call_args_list
    for arg_tuple in data_args:
        arg, _ = arg_tuple
        speed = arg[0].get('speed')
        assert speed <= 20
    
    assert bike.interval == bike.SLOW_INTERVAL


@pytest.mark.asyncio
async def test_simulation_error_response(bike_setup, mock_bike_methods):
    """ Test to run the simulation, with two different error responses. """
    mock_update_data, mock_end_renting = mock_bike_methods
    bike = bike_setup

    def response_generator():
        yield MockedResponse(json_data={'trip_id': 123}, status = 400)
        yield MockedResponse(json_data={'errors': 'Can\'t rent bike'}, status = 204)

    response_iter = response_generator()

    def post_side_effect(*args, **kwargs):
        response = next(response_iter)

        return response

    with patch('aiohttp.ClientSession.post', side_effect=post_side_effect):
        await bike.run_simulation()

    mock_end_renting.assert_not_called()
    mock_update_data.assert_not_called()

    assert bike.interval == bike.SLOW_INTERVAL


@pytest.mark.asyncio
async def test_sim_one_ok_one_error(bike_setup, mock_bike_methods):
    """ Test to run the simulation, with one ok and one error response. """
    mock_update_data, mock_end_renting = mock_bike_methods
    bike = bike_setup

    def response_generator():
        yield MockedResponse(json_data={'trip_id': 123}, status = 200)
        yield MockedResponse(json_data={'error': 'Något gick fel'}, status = 400)

    response_iter = response_generator()

    def post_side_effect(*args, **kwargs):
        response = next(response_iter)
        if response.status == 200:
            bike.set_status(2)

        return response

    def end_renting_side_effect(*args, **kwargs):
        bike.set_status(1)

    mock_end_renting.side_effect = end_renting_side_effect

    with patch('aiohttp.ClientSession.post', side_effect=post_side_effect):
        await bike.run_simulation()

    mock_end_renting.assert_called_once()

    data_args = mock_update_data.call_args_list
    for arg_tuple in data_args:
        arg, _ = arg_tuple
        speed = arg[0].get('speed')
        assert speed <= 20

    assert bike.interval == bike.SLOW_INTERVAL
