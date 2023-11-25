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
        """ Method to get the position """

    @property
    @abstractmethod
    def speed(self):
        """ Method to set the speed """

class GpsSimulator(GpsBase):
    """" The gps-class used in the simulation

    Args:
        position (list[float]): the position in [latitude, longitude]    
    """

    def __init__(self, position):
        self._position = position
        self._speed = 0

    @property
    def position(self):
        """ Get the position 
        
        Returns:
            list[float]: the position in [latitude, longitude]
        """
        return self._position

    def update_position(self, new_position, time_in_seconds):
        """ Set the position, will also update the speed.
        
        Args:
            new_position (list[float]): the new position
            time_in_seconds (float): the time in seconds
        """
        last_pos = tuple(self._position)
        new_pos = tuple(new_position)
        distance_from_last_update = distance(lonlat(*last_pos), lonlat(*new_pos)).meters
        meter_pr_second = distance_from_last_update / time_in_seconds
        km_pr_hour = round(meter_pr_second * 3.6)

        self._speed = km_pr_hour
        self._position = new_position

    @property
    def speed(self):
        """ Get the speed 
        
        Returns:
            float: the speed in km/h
        """
        return self._speed