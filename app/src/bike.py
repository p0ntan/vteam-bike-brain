#!/usr/bin/env python
"""
Bike module
"""
import os
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
    API_URL = os.environ['API_URL']
    SLOW_INTERVAL = 30

    def __init__(self, data: dict, battery: BatteryBase, gps: GpsBase, simulation: dict = None, interval: int = 10):
        self._active = True if data.get('active', 1) == 1 else False
        self._status = data.get('status_id')
        self._city_id = data.get('city_id')
        self._id = data.get('id')
        self._gps = gps
        self._battery = battery
        self._city_zone = data.get('city_zone', {})
        self._speed_limit = 20  # TODO change into something more useful
        self._simulation = simulation

        # Intervals in bike, _used_interval is the one that is used in loops
        self._used_interval = self.SLOW_INTERVAL  # interval that is used in loops, is changing when bike is running.
        self._interval = interval  # interval in seconds when bike is moving

        # Bike needs to be started with method start()
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

    @property
    def status(self):
        """ int: statuscode for the bike """
        return self._status

    def set_status(self, status: int):
        """ Set the status of the bike, set_status is used instead of a setter to access method from SSE-listener.

        Args:
            status (int): new status for the bike
        """
        # self._used_interval = self.SLOW_INTERVAL
        if status == 1 and self._battery.needs_charging():  # Control to not set the status to 1
            status = 3  # 3 is the status for maintenance required
        elif status == 2:
            self._used_interval = self._interval
        self._status = status

    def lock_bike(self):
        """ Locks the bike by changing active to False and sets speed limit to zero """
        self._speed_limit = 0
        self._active = False

    def unlock_bike(self):
        """ Unlocks the bike by changing active to True """
        self._active = True

    def set_speed_limit(self):
        """ Sets the speedlimit for the bike, based on position. """
        self._speed_limit = 20  # TODO add logic for speedlimit

    def get_data(self):
        """ Get data to send to server

        Returns:
            dict: with data needed for the server
        """
        return {
            'id': self.id,
            'status_id': self._status,
            'charge_perc': round(self._battery.level, 2),
            'coords': self._gps.position,
            'speed': self._gps.speed
        }

    async def _run_bike(self):
        """ The asynchronous loop in the bike when program is running. """
        while self._running:
            if not self._running_simulation:
                if self._battery.needs_charging():
                    self.set_status(3)  # 3 is the status for maintenance required
                data = self.get_data()

                await self._update_bike_data(data)
            await asyncio.sleep(self._used_interval)

    async def run_simulation(self):
        """ Asynchronous method to run the simulation for a bike. """
        if self._simulation is None or self._running_simulation:
            return

        self._running_simulation = True

        # Loop through each trip
        for trip in self._simulation['trips']:
            req_url = self.API_URL + f"/bikes/rent/{self.id}"
            response_ok = False

            # headers and data is added for both renting and returning bike
            headers = {'x-access-token': trip['user']['token']}
            data = {'id': trip['user']['id'], 'bike_id': self.id}

            # Send a post-request to start renting the bike, if ok start simulation.
            # TODO add error handling
            async with aiohttp.ClientSession() as session:
                async with session.post(req_url, json=data, headers=headers, timeout=5) as response:
                    if response.status == 200:
                        response_ok = True
                        response_data = await response.json()
                        trip_id = response_data['trip_id']

            if response_ok:
                # Start looping through the actual trip
                for position in trip['coords']:
                    self._gps.position = (position, self._interval)
                    await self._update_bike_data(self.get_data())
                    await asyncio.sleep(self._interval)

                # Change url for returning the bike and then return the bike with
                req_url = self.API_URL + f"/bikes/return/{trip_id}"
                async with aiohttp.ClientSession() as session:
                    async with session.put(req_url, json=data, headers=headers, timeout=5) as response:
                        # TODO handle response if needed
                        pass

        self._running_simulation = False

    async def _update_bike_data(self, data):
        """ Asynchronous method to send data to server """
        route = f"/bikes/{self.id}"
        req_url = self.API_URL + route
        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(req_url, json=data, timeout=1.5) as response:
                    if response.status != 200:
                        print(f"Errorcode: {response.status}")
            except asyncio.TimeoutError:
                pass

    def start(self):
        """ Start the bikes program
        
        Returns:
            self._run_bike(): Task to run by the SSE-listener
        """
        self._running = True
        return self._run_bike()

    def stop(self):
        """ Stop the bikes program """
        self._running = False
