#!/usr/bin/env python
"""
Bike module
"""
import os
import asyncio
import aiohttp
from src.battery import BatteryBase
from src.gps import GpsBase
from src.zone import Zone, CityZone


class Bike:
    """
    Class that represents the bike and it's brain (functionality)

    Args:
        data (dict): data for the bike from the database
        battery (BatteryBase): the battery used in the bike
        gps (GpsBase): the gps for the bike, used for position and speed
        simulation (dict=None): simulation data for bike, default is None
        interval (int=10): interval in seconds for the bike to send data to server when moving, default is 10
    """
    API_URL = os.environ.get('API_URL', '')
    SLOW_INTERVAL = 30

    def __init__(self, data: dict, battery: BatteryBase, gps: GpsBase, simulation: dict = None, interval: int = 10):
        self._active = data.get('active', 1) == 1  # True if active is 1
        self._status = data.get('status_id')
        # TODO city_id needed?
        # self._city_id = data.get('city_id')
        self._id = data.get('id')
        self._gps = gps
        self._battery = battery
        self._city_zone = None
        self._speed_limit = 20  # Fallback speed limit, speed limit is set automatically by position
        self._simulation = simulation

        # Intervals in bike, _used_interval is the one that is used in loops
        self._fast_interval = interval  # interval in seconds when bike is moving.
        self._interval = self.SLOW_INTERVAL  # interval that is used in loops, is changing when bike is running.

        # Bike needs to be started by metod start(). When simulation is over the simulation event is set
        self._running = False
        self._simulation_event_off = asyncio.Event()
        self._simulation_event_off.set()  # This sets the event to true

    @property
    def id(self):
        """ int: the bikes id """
        return self._id

    @property
    def interval(self):
        """ int: interval for the bike to send data """
        return self._interval

    # TODO is this needed?
    @interval.setter
    def interval(self, interval):
        self._interval = interval

    @property
    def status(self):
        """ int: statuscode for the bike """
        return self._status

    def add_zones(self, city_zone_data):
        """ Method to add zones to bike. Can also be used to 'recache' zones.

        Args:
            city_zone_data (dict): data needed for setting up zones
        """
        city_zone = CityZone(city_zone_data)
        backup_speed_limit = city_zone.speed_limit  # Used for zones without a speed limit

        zones = []
        for zone in city_zone_data.get('zones'):
            zones.append(Zone(zone, backup_speed_limit))

        city_zone.add_zones_list(zones)
        self._city_zone = city_zone

    def set_status(self, status: int):
        """ Set the status of the bike, set_status is used instead of a setter to access method from SSE-listener.

        Args:
            status (int): new status for the bike
        """
        # Set the interval to the slow interval, default for when status is changed.
        if status == 1 and self._battery.needs_charging():
            # Control to not set the status to 1 when maintenance required (low battery)
            status = 3
            self._interval = self.SLOW_INTERVAL
        elif status == 2:
            # Change to faster interval when bike is rented, status 2
            self._interval = self._fast_interval
        self._status = status

    def lock_bike(self):
        """ Locks the bike by changing active to False and sets speed limit to zero """
        self._speed_limit = 0
        self._active = False

    def unlock_bike(self):
        """ Unlocks the bike by changing active to True """
        self._active = True
        self._update_speed_limit()

    def _update_speed_limit(self):
        """ Updates the speedlimit for the bike. """
        # Only update speedlimit if bike is active/unlocked.
        if self._active and self._city_zone is not None:
            position = self._gps.position
            self._speed_limit = self._city_zone.get_speed_limit(position)

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
        # loop_interval is number of seconds between each loop
        loop_interval = 2
        # count controls each loop iteration. Will be set to same as interval for first loop
        # to send data at first iteration.
        count = self._interval / 2
        while self._running:
            # This is needed to hold loop if a simulation is running.
            await self._simulation_event_off.wait()

            if self._battery.needs_charging():
                self.set_status(3)  # 3 is the status for maintenance required

            # self._update_speed_limit()

            # When count is same as interval, send data to server.
            if count >= self._interval:
                data = self.get_data()
                await self._update_bike_data(data)
                count = 0

            await asyncio.sleep(loop_interval)
            count += loop_interval

    async def run_simulation(self):
        """ Asynchronous method to run the simulation for a bike. """
        if self._simulation is None or not self._simulation_event_off.is_set():
            return

        # Simulation is running/on, setting _simulation_event_off is False
        self._simulation_event_off.clear()

        # Loop through each trip
        for trip in self._simulation['trips']:
            req_url = self.API_URL + f"/user/bikes/rent/{self.id}"
            response_ok = False

            # headers and data is added for both renting and returning bike
            headers = {'x-access-token': trip['user']['token']}
            data = {'userId': trip['user']['id']}

            # Send a post-request to start renting the bike, if ok start simulation.
            # TODO add error handling
            async with aiohttp.ClientSession() as session:
                async with session.post(req_url, json=data, headers=headers, timeout=5) as response:
                    if response.status < 300:
                        response_ok = True
                        response_data = await response.json()
                        trip_id = response_data.get('trip_id')

            if response_ok:
                # Start looping through the actual trip
                for position in trip['coords']:
                    self._gps.position = (position, self._interval)
                    await self._update_bike_data(self.get_data())
                    await asyncio.sleep(self._fast_interval)

                # Change url for returning the bike and then return the bike with
                req_url = self.API_URL + f"/user/bikes/return/{trip_id}"
                async with aiohttp.ClientSession() as session:
                    async with session.put(req_url, json=data, headers=headers, timeout=5) as response:
                        # TODO handle response if needed
                        pass

        # Simulation is over, set _simulation_event_off to True
        self._simulation_event_off.set()

    async def _update_bike_data(self, data: dict):
        """ Asynchronous method to send data to server.

        Args:
            data (dict): data to send to server
        """
        route = f"/bikes/{self.id}"
        req_url = self.API_URL + route
        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(req_url, json=data, timeout=1.5) as response:
                    if response.status > 300:
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
