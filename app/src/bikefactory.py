#!/usr/bin/env python
"""
Bikefactory module, used for creating each bike with injections
"""

import os
import json
import random
from src.bike import Bike
from src.battery import BatterySimulator
from src.gps import GpsSimulator


class BikeFactory:
    """ Class for creating a bike, aka bike-factory.

    Args:
        bike_data (list): list with data used for initialization of the bikes
        routes (dict): route-data used for simulation
        interval (int=10): interval in seconds for simulation (in movement)
    """

    def __init__(
            self,
            bike_data: list,
            routes: dict,
            interval: int = 10
            ):
        """ Initialize the bike and inject gps, battery and data """

        self._bikes = {}

        good_routes = self._load_good_routes()

        for data_item in bike_data:
            bike_id = data_item.get('id')
            status_id = data_item.get('status_id')
            simulation = routes[bike_id] if bike_id in routes else None
            battery_level, level_reduction = self._decide_battery_level(bike_id, good_routes, status_id)
            gps_sim = GpsSimulator(data_item.get('coords'))
            battery_sim = BatterySimulator(battery_level, level_reduction)
            new_bike = Bike(data_item, battery_sim, gps_sim, simulation, interval)
            new_bike.update_zones()
            self._bikes[bike_id] = new_bike

    def _load_good_routes(self):
        """ This loads the good routes bike id for simulation.

        Returns:
            set: with id of bikes with good routes
        """
        good_routes = set()
        directory = 'to_simulation'
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding="UTF-8") as file:
                for bike in json.load(file):
                    good_routes.add(bike['bike_id'])

        return good_routes

    def _decide_battery_level(self, bike_id: int, good_routes: set, status_id: int):
        """ Sets random batterylevels depending on id of bike.

        Args:
            bike_id (int): id for the bike
            good_routes (set): set with bike ids
            status_id (int): status for the bike

        Returns:
            tuple:
                - float: battery level to use
                - float: level reduction
        """
        level_reduction = 0.001
        battery_level = round(random.uniform(0.15, 0.7), 2)

        if bike_id in good_routes or bike_id <= 206:
            battery_level = round(random.uniform(0.7, 1), 2)
        elif bike_id > 1057 and status_id == 3:
            battery_level = round(random.uniform(0.1, 0.5), 2)
            level_reduction = -0.01  # Simulate charging battery

        return battery_level, level_reduction

    @property
    def bikes(self):
        """ dict[Bike]: dict of all created bikes in factory """
        return self._bikes
