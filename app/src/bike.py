#!/usr/bin/env python
"""
Bike module
"""

import time
import threading
import requests
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
        interval (int=10): interval for the bike to send data to server, default is 10
    """
    API_URL = 'http://express-server:1337/bikes/'

    def __init__(self, data: dict, battery: BatteryBase, gps: GpsBase, simulation: dict=None, interval: int=10):
        self._status = data['status_id']
        self._city_id = data['city_id']
        self._id = data['id']
        self._gps = gps
        self._battery = battery
        self._interval = interval
        self._simulation = simulation

        # Set up a thread for the bike loop
        self._thread = threading.Thread(target=self._run_bike)
        # Bike needs to be started with metod start()
        self._running = False

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
            'status': self._status,
            'battery_level': self._battery.level,
            'position': self._gps.position,
            'speed': self._gps.speed
        }

    def _run_bike(self):
        """ The loop in the bike when program is running. """
        while self._running:
            data = self.get_data()
            self._update_bike_data(data)

            time.sleep(self._interval)

    def run_simulation(self):
        """ Method to run the simulation for a bike. """
        for trip in self._simulation['trips']:
            for position in trip['coords']:
                new_position = position
                self._gps.position = (new_position, self._interval)

                self._update_bike_data(self.get_data())
                time.sleep(self._interval)

    def _update_bike_data(self, data):
        """ Method do send data to server """
        response = requests.post(self.API_URL, json=data, timeout=1.5)
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Errorcode: {response.status_code}")

    def start(self):
        """ Start the bikes program """
        self._running = True
        self._thread.start()

    def stop(self):
        """ Stop the bikes program """
        self._running = False
        self._thread.join()
