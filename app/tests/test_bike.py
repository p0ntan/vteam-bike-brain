#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Module for testing the class Bike """

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.bike import Bike
from src.battery import BatterySimulator
from src.gps import GpsSimulator

bike_data = {
    'id': 1,
    'city_id': 'STHLM',
    'status_id': 1,
    'coords': [13.508699207322167, 59.38210003526896],
}

def test_create_bike():
    """ Creating a Bike and checks data """
    gps_sim = GpsSimulator(bike_data['coords'])  # Could be mocked, but it takes away the purpose of the test
    battery_sim = BatterySimulator()  # Could/should be mocked, but then takes away the purpose of the test

    bike_instance = Bike(bike_data, battery_sim, gps_sim)
    data_from_bike = bike_instance.get_data()
    assert isinstance(data_from_bike, dict)

    # Check that data has all the right keys and values
    # id
    assert 'id' in data_from_bike
    assert isinstance(data_from_bike.get('id'), int)
    # status_id
    assert 'status_id' in data_from_bike
    assert isinstance(data_from_bike.get('status_id'), int)
    # charge_perc
    assert 'charge_perc' in data_from_bike
    assert isinstance(data_from_bike.get('charge_perc'), float)
    # coords
    assert 'coords' in data_from_bike
    assert isinstance(data_from_bike.get('coords'), list)
    assert isinstance(data_from_bike.get('coords')[0], float)
    assert isinstance(data_from_bike.get('coords')[1], float)
    # speed
    assert 'speed' in data_from_bike
    assert isinstance(data_from_bike.get('speed'), int)

def test_moving_bike():
    """ Update position for a bike, see that it sends out speed and new position """
    gps_sim = GpsSimulator(bike_data['coords'])  # Could be mocked, but it takes away the purpose of the test
    battery_sim = MagicMock()
    bike_instance = Bike(bike_data, battery_sim, gps_sim)

    data_from_bike = bike_instance.get_data()
    assert data_from_bike.get('speed') == 0
    assert data_from_bike.get('coords') == bike_data.get('coords')

    new_position = [13.505173887431198, 59.38216072603788]  # 200 meters between this and original position
    interval_in_seconds = 10

    # Forcing new position on private variable, disableing pylint for this action
    # pylint: disable=protected-access
    bike_instance._gps.position = (new_position, interval_in_seconds)
    data_from_bike = bike_instance.get_data()

    assert data_from_bike.get('speed') == 72  # 200 meters in 10 sek = 72 km/h
    assert data_from_bike.get('coords') == new_position

@pytest.mark.asyncio
async def test_start_bike_low_battery():
    """ Test to see if status changes if battery gets to low """
    gps_sim = MagicMock()
    battery_sim = MagicMock()
    battery_sim.needs_charging = MagicMock(side_effect=[False, False, True, True])

    bike = Bike(bike_data, battery_sim, gps_sim)

    # Mock methods to isolate test
    # pylint: disable=protected-access
    bike._update_bike_data = AsyncMock()
    bike._used_interval = 2
    bike._running = True
    bike._running_simulation = False

    async def stop_bike_after_5_seconds():
        await asyncio.sleep(5)
        # pylint: disable=protected-access
        bike._running = False
    
    # Check that status is 1 when starting bike
    assert bike.status == 1

    # Run bike.start() and stop after 5 seconds
    await asyncio.gather(
        bike.start(),
        stop_bike_after_5_seconds()
    )

    # Control that needs_charging has run three times and status has changed
    assert bike._battery.needs_charging.call_count == 3
    assert bike.status == 3

def test_change_status_when_low_battery():
    """ Trying to change status when battery i low. """
    gps_sim = MagicMock()
    battery_sim = MagicMock()
    battery_sim.needs_charging = MagicMock(return_value=True)

    bike = Bike(bike_data, battery_sim, gps_sim)
    assert bike.status == 1

    bike.set_status(3)
    assert bike.status == 3

    bike.set_status(1)  # Should stay at 3 since low battery
    assert bike.status == 3
