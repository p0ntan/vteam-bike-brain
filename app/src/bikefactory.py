#!/usr/bin/env python
"""
Bikefactory module, used for creating each bike with injections
"""

from src.bike import Bike
from src.battery import BatterySimulator
from src.gps import GpsSimulator
from src.sselistener import SSElistener

class BikeFactory:
    """ Class for creating a bike, aka bike-factory.
    
    Args:
        bike (Bike): the bike itself
        gps (GpsSimulator): the GPS-simulator
        battery (BatterySimulator): the battery simulator
        bike_data (dict): data used in initialization of the bikes
    
    Returns:
        Bike: an initialized bike with gps and battery simulator
    """

    def __init__(
            self,
            bike: Bike,
            gps: GpsSimulator,
            battery: BatterySimulator,
            sse_listener: SSEListener,
            bike_data: dict,
            routes: dict
        ):
        """ Initialize the bike and inject gps, battery and data """
        gps_sim = gps(bike_data['position'])
        battery_sim = battery()
        self._bike = bike(bike_data, gps_sim, battery_sim)

    def __new__(cls):
        """ When creating """
        return self._bike
