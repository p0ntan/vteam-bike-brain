#!/usr/bin/env python
"""
Bike module
"""

import asyncio
import aiohttp
from src.battery import BatteryBase
from src.gps import GpsBase

class Bike:
    """
    Class that represents the bike and it's brain (functionality)

    Args:
        data (dict): data for the bike from the database
        battery (BatteryBase): the battery used in the bike
        gps (GpsBase): the gps for the bike, used for position and speed
        simulation (dict=None): simulation data for bike, default is None
        interval (int=10): interval in seconds for the bike to send data to server, default is 10
    """
    API_URL = 'http://express-server:1337/bikes/'

    def __init__(self, data: dict, battery: BatteryBase, gps: GpsBase, simulation: dict=None, interval: int=10):
        self._status = data['status_id']
        self._city_id = data['city_id']
        self._id = data['id']
        self._gps = gps
        self._battery = battery
        self._interval = interval # interval in seconds when bike is moving
        self._simulation = simulation
        self._slow_interval = 30 # interval in seconds when bike stands still

        # Bike needs to be started with metod start()
        self._running = False
        self._running_simulation = False

    @property
    def id(self):
        """ int: the bikes id """
        return self._id

    @property
    def interval(self):
        """ int: interval for the bike to send data """
        return self._interval

    @interval.setter
    def interval(self, interval):
        self._interval = interval

    def get_data(self):
        """ Get data to send to server
        
        Returns:
            dict: with data needed for the server
        """
        return {
            'id': self.id,
            'status_id': self._status,
            'charge_perc': self._battery.level,
            'coords': self._gps.position,
            'speed': self._gps.speed
        }

    async def _run_bike(self):
        """ The asynchronous loop in the bike when program is running. """
        while self._running:
            if not self._running_simulation:
                data = self.get_data()
                await self._update_bike_data(data)
            await asyncio.sleep(self._slow_interval)

    async def run_simulation(self):
        """ Asynchronous method to run the simulation for a bike. """
        if self._simulation is None:
            return

        self._running_simulation = True

        for trip in self._simulation['trips']:
            for position in trip['coords']:
                self._gps.position = (position, self._interval)
                await self._update_bike_data(self.get_data())
                await asyncio.sleep(self._interval)

    async def _update_bike_data(self, data):
        """ Asynchronous method to send data to server """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.API_URL, json=data, timeout=1.5) as response:
                    if response.status != 200:
                        print(f"Errorcode: {response.status}")
            except asyncio.TimeoutError:
                pass

    def start(self):
        """ Start the bikes program """
        self._running = True
        return self._run_bike()

    def stop(self):
        """ Stop the bikes program """
        self._running = False
