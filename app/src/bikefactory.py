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
        bike (Bike): the bike class
        gps (GpsSimulator): the GPS-simulator class
        battery (BatterySimulator): the battery simulator class
        bike_data (dict): data used in initialization of the bikes
        routes (dict): route-data used for simulation
    """

    def __init__(
            self,
            bike: Bike,
            gps: GpsSimulator,
            battery: BatterySimulator,
            bike_data: dict,
            routes: dict
        ):
        """ Initialize the bike and inject gps, battery and data """

        self._bikes = []

        for data_item in bike_data:
            bike_id = data_item['id']
            simulation = routes[bike_id]
            gps_sim = gps(data_item['position'])
            battery_sim = battery()
            new_bike = bike(data_item, battery_sim, gps_sim, simulation)

            self._bikes.append(new_bike)

    @property
    def bikes(self):
        """ list[Bike]: list of all created bikes in factory """
        return self._bikes
