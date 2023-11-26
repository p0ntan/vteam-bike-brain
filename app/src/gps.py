#!/usr/bin/env python
"""
GPS-module
"""
from abc import ABC, abstractmethod
from geopy.distance import lonlat, distance

class GpsBase(ABC):
    """ Abstract class GpsBase.

    A bike will depend on this abstract-class, and can later be replaced with
    any class that is a subclass of GpsBase (like code for an actual GPS).
    """

    @property
    @abstractmethod
    def position(self):
        """ list[float]: position in [latitude, longitude] """

    @property
    @abstractmethod
    def speed(self):
        """ int: speed for the bike in km/h """

class GpsSimulator(GpsBase):
    """" The gps-class used in the simulation

    Args:
        position (list[float]): the position in [latitude, longitude]    
    """

    def __init__(self, position: list):
        self._position = position
        self._speed = 0

    @property
    def position(self):
        """ list[float]: position in [latitude, longitude] """
        return self._position

    @position.setter
    def position(self, new_data: tuple):
        """ new_data includes new position and time
        
        Args:
            new_data (tuple[list, int]): position and elapsed time
        """
        last_pos = tuple(self._position)
        new_pos = tuple(new_data[0])
        distance_from_last_update = distance(lonlat(*last_pos), lonlat(*new_pos)).meters
        meter_pr_second = distance_from_last_update / new_data[1]
        km_pr_hour = meter_pr_second * 3.6

        self._speed = km_pr_hour
        self._position = new_data[0]

    @property
    def speed(self):
        """ int: speed for the bike in km/h """
        return round(self._speed)
