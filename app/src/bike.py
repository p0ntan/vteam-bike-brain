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

    def __init__(self, data: dict, battery: BatteryBase, gps: GpsBase, simulation: dict=None, interval: int=10):
        self._status = data['status_id']
        self._city_id = data['city_id']
        self._id = data['id'] # TODO ska ändras till bike_id, bevhöer också ändras från server (se rest-arket)
        self._gps = gps
        self._battery = battery
        # self._city_zone = data['city_zone']
        self._interval = interval # interval in seconds when bike is moving
        self._simulation = simulation
        self._slow_interval = 30 # interval in seconds when bike stands still

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

    @status.setter
    def status(self, status):
        """ Set the status of the bike, intened to be used by admin/serviceworker.

        Args:
            status (int): new status for the bike
        """
        self._status = status

    def lock_bike(self):
        """ Locks the bike by changing status to avaliable (1) """
        self._status = 1

    def unlock_bike(self):
        """ Unlocks the bike by changing status to rented (2) """
        self._status = 2

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
                data = self.get_data()
                await self._update_bike_data(data)
            await asyncio.sleep(self._slow_interval)

    async def run_simulation(self):
        """ Asynchronous method to run the simulation for a bike. """
        # TODO lägg till or self._running_simulation = True så man inte kan starta flera simuleringar
        if self._simulation is None:
            return

        self._running_simulation = True

        # Loop through each trip
        for trip in self._simulation['trips']:
            req_url = self.API_URL + f"/bikes/rent/{self.id}"
            response_ok = False

            # headers and data is added for both renting and returning bike
            headers = {'x-access-token': trip ['user']['token']}
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
        """ Start the bikes program """
        self._running = True
        return self._run_bike()

    def stop(self):
        """ Stop the bikes program """
        self._running = False
