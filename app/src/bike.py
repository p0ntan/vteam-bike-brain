#!/usr/bin/env python
"""
Bike module
"""
import requests
import time
import threading

class Bike():
    API_URL = 'http://express-server:1337/bikes/'

    """
    Class that represents the bike and it's brain (functionality)
    """
    def __init__(self, data, interval=10):
        """ Constructor """
        self._status = data['status']
        self._id = data['id']
        self._lat = data['lat']
        self._lng = data['lng']
        self._interval = interval
        # self._simulations = data['trips']
        
        # Set up a thread for the bike loop
        self._thread = threading.Thread(target=self._run_bike)
        # Bike needs to be started with metod start()
        self._running = False


    @property
    def id(self):
        return self._id

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval):
        self._interval = interval

    def get_data(self):
        return {
            'id': self.id,
            'status': self._status,
            'lat': self._lat,
            'lng': self._lng
        }

    def _run_bike(self):
        while self._running:
            data = self.get_data()
            self._update_bike_data(data)

            time.sleep(self._interval)

    # def run_simulation(self):
    #     for trip in self._simulations:
    #         for position in trip:
    #             self._lat = position[0]
    #             self._lng = position[1]
    
    #             self._update_bike_data(self.get_data())
    #             time.sleep(2)

    def _update_bike_data(self, data):
        response = requests.post(self.API_URL, json=data)
        if response.status_code == 200:
            data = response.json()
            print(data)
        else:
            print(f"Errorcode: {response.status_code}")

    def start(self):
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join()
