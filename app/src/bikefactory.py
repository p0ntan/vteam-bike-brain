#!/usr/bin/env python
"""
Bikefactory module, used for creating each bike with injections
"""

import os
import json
import random
import asyncio
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
            simulation = routes[bike_id] if bike_id in routes else None
            battery_level = self._decide_battery_level(bike_id, good_routes)
            gps_sim = GpsSimulator(data_item.get('coords'))
            battery_sim = BatterySimulator(battery_level)
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

    def _decide_battery_level(self, id, good_routes):
        """ Sets random batterylevels depending on id of bike.
        
        Args:
            id (int): id for the bike
            good_routes (set): set with bike ids
        
        Returns:
            float: battery level to use
        """
        battery_level = round(random.uniform(0.15, 0.7),2)

        if id in good_routes:
            battery_level = round(random.uniform(0.7, 1),2)
        elif id > 1057:
            battery_level = round(random.uniform(0.1, 0.5),2)

        return battery_level

    @property
    def bikes(self):
        """ dict[Bike]: dict of all created bikes in factory """
        return self._bikes
