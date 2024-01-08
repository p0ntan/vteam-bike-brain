#!/usr/bin/env python
"""
Class for BikeSimulator
"""

from __future__ import annotations
import os
import asyncio
import aiohttp


class BikeSimulator:
    """
    Class that represents the bikes simulation.

    Args:
        bike (Bike): the Bike to simulate.
        simulation (dict): simulation data needed for simulation.
        interval (int): interval in seconds for the bike to send data to server when moving.
    """
    API_URL = os.environ.get('API_URL', '')
    API_KEY = os.environ.get('API_KEY', '')

    def __init__(self, bike: 'Bike', simulation: dict, interval: int):  # noqa: F821
        self._bike = bike
        self._simulation = simulation
        self._interval = interval

    async def start_simulation(self):
        """ Asynchronous method to start the simulation for a bike. """

        for trip in self._simulation.get('trips', []):
            response_ok, trip_id = await self._start_renting(trip)
            if response_ok:
                self._bike.set_status(2)  # This also is done through SSE, but isn't fast enough for simulation
                await self._simulate_trip(trip, trip_id)

    async def _start_renting(self, trip: dict):
        """ Start renting the bike for a trip.

        Args:
            trip (dict): Data needed for trip with user-jwt and coords.

        Returns:
            tuple:
                - bool: True if the renting process is successful, False otherwise.
                - int or None: The trip ID if the renting process is successful, None otherwise.
        """
        req_url = self.API_URL + f"/user/bikes/rent/{self._bike.id}"
        user = trip.get('user', {})
        headers, data = self._prepare_request(user)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(req_url, json=data, headers=headers, timeout=5) as response:
                    if response.status < 300:
                        response_data = await response.json()
                        return 'errors' not in response_data, response_data.get('trip_id')
                    return False, None
            except asyncio.TimeoutError:
                return False, None

    async def _simulate_trip(self, trip: dict, trip_id: int):
        """ Simulate the trip.

        Args:
            trip (dict): Data needed for trip, user-jwt and coords.
            trip_id (int): Trip ID.
        """
        for position in trip.get('coords', []):
            self._bike.gps.position = (position, self._interval)

            if self._bike.battery.needs_charging():
                self._bike.set_status(5)  # 5 is the status for 'rented maintenance required'

            await self._bike.update_bike_data()
            await asyncio.sleep(self._interval)

            # If a bike is locked by any reason, stop simulation and set speed to 0.
            # And make a last update to server with the newest data.
            if not self._bike.is_unlocked():
                self._bike.gps.speed = 0
                await self._bike.update_bike_data()
                return

        # After each simulatioed trip make sure speed is zero.
        self._bike.gps.speed = 0

        # Ending a trip should only be done when a trip has come to the last coords
        await self._end_renting(trip, trip_id)

    async def _end_renting(self, trip: dict, trip_id: int):
        """ End renting the bike after a trip.

        Args:
            trip (dict): Data needed for trip, user-jwt and coords.
            trip_id (int): Trip ID.
        """
        req_url = self.API_URL + f"/user/bikes/return/{trip_id}"
        headers, user_data = self._prepare_request(trip.get('user', {}))

        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(req_url, json=user_data, headers=headers, timeout=5) as response:
                    if response.status >= 300:
                        print(f"Errorcode: {response.status}")
            except asyncio.TimeoutError:
                pass

    def _prepare_request(self, user: dict):
        """ Prepare headers and data for requests.

        Args:
            user (dict): Userdata with token and id
        Return:
            tuple:
                - dict: headers.
                - dict: data for body.
        """
        headers = {
            'x-access-token': user.get('token', ''),
            'x-api-key': self.API_KEY
        }
        data = {'userId': user.get('id', '')}

        return headers, data
