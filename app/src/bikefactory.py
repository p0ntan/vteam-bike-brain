#!/usr/bin/env python
"""
Bikefactory module, used for creating each bike with injections
"""
from src.bike import Bike
from src.battery import BatterySimulator
from src.gps import GpsSimulator


class BikeFactory:
    """ Class for creating a bike, aka bike-factory.

    Args:
        bike_data (list): list with data used for initialization of the bikes
        routes (dict): route-data used for simulation
        zones (dict): zones for adding to the bike (city and restricted)
        interval (int=10): interval in seconds for simulation (in movement)
    """

    def __init__(
            self,
            bike_data: list,
            routes: dict,
            zones: dict,
            interval: int = 10
            ):
        """ Initialize the bike and inject gps, battery and data """

        self._bikes = {}

        for data_item in bike_data:
            bike_id = data_item.get('id')
            city_id = data_item.get('city_id')
            simulation = None

            if bike_id in routes:
                simulation = routes[bike_id]

            gps_sim = GpsSimulator(data_item.get('coords'))
            battery_sim = BatterySimulator()
            new_bike = Bike(data_item, battery_sim, gps_sim, simulation, interval)
            new_bike.add_zones(zones.get(city_id))

            self._bikes[bike_id] = new_bike

    @property
    def bikes(self):
        """ dict[Bike]: dict of all created bikes in factory """
        return self._bikes
