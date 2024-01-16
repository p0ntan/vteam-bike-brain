#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# pylint: disable=protected-access

""" Module for testing the class Bike """

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from src.bike import Bike
from src.battery import BatterySimulator
from src.gps import GpsSimulator
from src.zone import CityZone, Zone

bike_data = {
    'id': 1,
    'status_id': 1,
    'coords': [13.508699207322167, 59.38210003526896],
}

# Structure for the zone_data
zone_data = {
    'city_id': 'TEST',
    'geometry': {
        'coordinates': [
            []
        ]
    },
    'speed_limit': 20,
    'zones': [
        {
            'zone_id': 3,
            'geometry': {
                'coordinates': [
                    []
                ]
            },
            'speed_limit': 0,
        },
        {
            'zone_id': 3,
            'geometry': {
                'coordinates': [
                    []
                ]
            }
        }
    ]
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
    # city_id, should be empty string when no zone has been added/updated
    assert 'city_id' in data_from_bike
    assert isinstance(data_from_bike.get('city_id'), str)
    assert data_from_bike.get('city_id') == ''
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
    gps_sim = GpsSimulator(bike_data.get('coords'))  # Could be mocked, but it takes away the purpose of the test
    battery_sim = MagicMock()
    bike_instance = Bike(bike_data, battery_sim, gps_sim)

    data_from_bike = bike_instance.get_data()
    assert data_from_bike.get('speed') == 0
    assert data_from_bike.get('coords') == bike_data.get('coords')

    new_position = [13.505173887431198, 59.38216072603788]  # 200 meters between this and original position
    interval_in_seconds = 10

    # Forcing new position on private variable, disableing pylint for this action
    bike_instance._gps.position = (new_position, interval_in_seconds)
    data_from_bike = bike_instance.get_data()

    assert data_from_bike.get('speed') == 72  # 200 meters in 10 sek = 72 km/h
    assert data_from_bike.get('coords') == new_position


@pytest.mark.asyncio
async def test_start_low_battery_locked():
    """ Test to see if status changes if battery gets to low, bike standing still. """
    gps_sim = MagicMock()
    battery_sim = MagicMock()
    battery_sim.needs_charging = MagicMock(side_effect=[False, False, True, True, True, True])

    bike = Bike(bike_data, battery_sim, gps_sim)

    # Mock methods to isolate test
    bike.update_bike_data = AsyncMock()
    bike._running = True

    async def stop_bike_after_5_seconds():
        await asyncio.sleep(5)

        bike._running = False

    # Check that status is 1 when starting bike
    assert bike.status == 1

    # Run bike.start() and stop after 5 seconds
    await asyncio.gather(
        bike.start(),
        stop_bike_after_5_seconds()
    )

    # Control that needs_charging has run three times and status has changed
    assert bike._battery.needs_charging.call_count == 5
    assert bike.status == 4


@pytest.mark.asyncio
async def test_start_low_battery_unlocked():
    """ Test to see if status changes if battery gets to low, while rented. """
    gps_sim = MagicMock()
    battery_sim = MagicMock()
    battery_sim.needs_charging = MagicMock(side_effect=[False, False, True, True, True, True])

    bike = Bike(bike_data, battery_sim, gps_sim)

    # Mock methods to isolate test
    bike.update_bike_data = AsyncMock()
    bike._running = True

    async def stop_bike_after_5_seconds():
        await asyncio.sleep(5)

        bike._running = False

    # Check that status is 1 when starting bike
    bike._status = 2  # Status 2 for rented
    assert bike.status == 2

    # Run bike.start() and stop after 5 seconds
    await asyncio.gather(
        bike.start(),
        stop_bike_after_5_seconds()
    )

    # Control that needs_charging has run three times and status has changed
    assert bike._battery.needs_charging.call_count == 5
    assert bike.status == 5


def test_change_status_low_battery():
    """ Trying to change status when battery i low and bike is rented. """
    gps_sim = MagicMock()
    battery_sim = MagicMock()

    bike = Bike(bike_data, battery_sim, gps_sim)
    bike._status = 2  # Status 2 for rented
    assert bike.status == 2

    bike.set_status(5)  # Status 5 for rented maintenance required
    assert bike.status == 5

    bike.set_status(1)  # Should stay at 4 since low battery
    assert bike.status == 4


def test_deact_act_rented_bike():
    """ Trying to deactivate a rented bike, then activate it. """
    gps_sim = MagicMock()
    battery_sim = MagicMock()
    bike = Bike(bike_data, battery_sim, gps_sim)

    assert bike.is_unlocked() is False

    bike._status = 2  # Bike is rented with status 2

    assert bike.is_unlocked() is True

    bike.lock_bike()

    assert bike.is_unlocked() is False
    assert bike.status == 1


def test_deact_rented_maintenance():
    """ Trying to deactivate a rented bike needing maintenance. """
    gps_sim = MagicMock()
    battery_sim = MagicMock()
    bike = Bike(bike_data, battery_sim, gps_sim)
    assert bike.is_unlocked() is False

    bike.set_status(5)  # Bike is rented with status 5 maintenance required

    assert bike.is_unlocked() is True

    bike.lock_bike()

    assert bike.is_unlocked() is False
    assert bike.status == 4  # Maintenance required


def test_no_city_zone():
    """ Test if there is no city zone """
    gps_sim = MagicMock()
    battery_sim = MagicMock()
    bike = Bike(bike_data, battery_sim, gps_sim)

    bike._update_speed_limit()
    assert bike._speed_limit == 20


def test_load_zone_data():
    """ Test to load the zone data correctly """
    gps_sim = MagicMock()
    battery_sim = MagicMock()
    bike = Bike(bike_data, battery_sim, gps_sim)

    with patch('src.bike.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = zone_data  # Data at the top of file
        bike.update_zones()

    city_zone = bike._city_zone
    forbidden_zone = city_zone._zones[0]
    zone_without_limit = city_zone._zones[1]

    assert isinstance(city_zone, CityZone)
    assert city_zone.speed_limit == 20
    assert isinstance(forbidden_zone, Zone)
    assert forbidden_zone.speed_limit == 0
    assert isinstance(zone_without_limit, Zone)
    assert zone_without_limit.speed_limit == 20
    assert city_zone.city_id == "TEST"
