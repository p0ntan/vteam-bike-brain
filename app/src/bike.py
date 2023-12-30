#!/usr/bin/env python
"""
Bike module
"""
import os
import asyncio
import aiohttp
from src.bikesimulator import BikeSimulator
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
    API_KEY = os.environ.get('API_KEY', '')
    SLOW_INTERVAL = 30

    def __init__(self, data: dict, battery: BatteryBase, gps: GpsBase, simulation: dict = None, interval: int = 10):
        self._status = data.get('status_id')
        self._city_id = data.get('city_id')
        self._id = data.get('id')
        self._gps = gps
        self._battery = battery
        self._city_zone = None
        self._speed_limit = 20  # Fallback speed limit, speed limit is set automatically by position
        self._simulation = simulation

        # Intervals in bike, _used_interval is the one that is used in loops
        self._fast_interval = interval  # interval in seconds when bike is moving.
        self._interval = self.SLOW_INTERVAL  # interval that is used in loops, is changing when bike is running.

        # Bike needs to be started by metod start(). When simulation is over the simulation event is set to True
        self._running = False
        self._simulation_event_off = asyncio.Event()
        self._simulation_event_off.set()  # This sets the event to true, meaning simulation is NOT running

    @property
    def id(self):
        """ int: the bikes id """
        return self._id

    @property
    def status(self):
        """ int: statuscode for the bike """
        return self._status

    @property
    def gps(self):
        """ GpsBase: Returns the GPS-instance for the bike. """
        return self._gps

    @property
    def battery(self):
        """ BatteryBase: Returns the Battery-instance for the bike. """
        return self._battery

    def add_zones(self, city_zone_data: dict):
        """ Method to add zones to bike.

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

    async def update_zones(self):
        """ Method to update zones from server. """
        route = f"/bikes/{self.id}/zones"
        req_url = self.API_URL + route
        headers = {'x-api-key': self.API_KEY}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(req_url, headers=headers, timeout=5) as response:
                    if response.status < 300:
                        city_zone_data = await response.json()
                        self.add_zones(city_zone_data)
                        self._city_id = city_zone_data.get('city_id')
                    else:
                        print(f"Errorcode: {response.status}")
            except asyncio.TimeoutError:
                pass

    def set_status(self, status: int):
        """ Set the status of the bike, set_status is used instead of a setter to access method from SSE-listener.
        Possible statuscodes:
            1	available
            2	rented
            3	in maintenance
            4	maintenance required
            5	rented maintenance required

        Args:
            status (int): new status for the bike
        """
        if status == 1:
            # Control to not set the status to 1 when maintenance required
            status = 4 if self._status in {4, 5} else status
            self._interval = self.SLOW_INTERVAL
        elif status == 2:
            # Change to faster interval when bike is rented, status 2
            self._interval = self._fast_interval
        elif status == 4:
            # If maintenance is required and bike is rented (unlocked), use status 5
            status = 5 if self.is_unlocked() else status
        self._status = status

    def is_unlocked(self):
        """ Method to see if a bike is unlocked to be used by internal parts in bike.

        Ex. for the accelerator to work or a light for showing a user that the bike is unlocked.
        """
        # status 2 and 5 used when bike is rented, is the same as an unlocked bike.
        return self._status in {2, 5}

    def lock_bike(self):
        """ Lock the bike by changing status to 1. """
        # TODO ta bort eller byt sätt att låsa cykel
        self.set_status(1)

    def unlock_bike(self):
        """ Unlock the bike by changing status to 2. """
        # TODO byt ut sätt att låsa upp cykel eller ta bort metoden
        # self.set_status(2)
        pass  # Pass for now, since used when activating a bike.

    def _update_speed_limit(self):
        """ Updates the speedlimit for the bike. """
        # Only update speedlimit if there is a cityzone in bike.
        if self._city_zone is not None:
            position = self._gps.position
            self._speed_limit = self._city_zone.get_speed_limit(position)

    def get_data(self):
        """ Get data to send to server

        Returns:
            dict: with data needed for the server
        """
        return {
            'id': self.id,
            'city_id': self._city_id,
            'status_id': self._status,
            'charge_perc': round(self._battery.level, 2),
            'coords': self._gps.position,
            'speed': self._gps.speed
        }

    async def _run_bike(self):
        """ The asynchronous loop in the bike when program is running. """
        # loop_interval is number of seconds between each loop. Should be a low number for frequent
        # controls of position.
        loop_interval = self._interval  # TODO Change this to wanted loop time in bike

        # count controls each loop iteration. Will be set to same as interval for first loop
        count = self._interval
        while self._running:
            # This is needed to hold loop if a simulation is running.
            await self._simulation_event_off.wait()

            # if self.is_unlocked():
            # #   Whatever a bike should be able to do if a bike is unlocked can be done here.
            # #   Making the accelerator work, a green light showing bike is unlocked etc.
            # #   It's depnding on hardware of a bike and customers needs.

            # # TODO this can be changed (removed), but needs action from the server when battery
            # # is so low that the bike should be locked.
            # if self._bike.battery.low_battery():  # Low is <= 0.03
            #     self._bike.set_status(1)
            #     # self._bike.lock_bike()

            if self._battery.needs_charging():
                # 4 is the status for maintenance required, changes to 5 in method if bike is unlocked
                self.set_status(4)

            self._update_speed_limit()

            # When count is same or bigger as interval, send data to server.
            if count >= self._interval:
                await self.update_bike_data()
                count = 0

            await asyncio.sleep(loop_interval)
            count += loop_interval

    async def run_simulation(self):
        """ Asynchronous method to run the simulation for a bike. """
        if self._simulation is None or not self._simulation_event_off.is_set():
            return

        self._simulation_event_off.clear()

        simulator = BikeSimulator(self, self._simulation, self._fast_interval)
        await simulator.start_simulation()

        self._simulation_event_off.set()

    async def update_bike_data(self):
        """ Asynchronous method to send data to server. """
        route = f"/bikes/{self.id}"
        req_url = self.API_URL + route
        headers = {'x-api-key': self.API_KEY}
        data = self.get_data()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(req_url, json=data, headers=headers, timeout=5) as response:
                    if response.status >= 300:
                        response_data = await response.json()
                        print(f"Updating data, errorcode: {response.status}")
                        print(response_data)
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
