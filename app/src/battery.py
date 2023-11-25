#!/usr/bin/env python
"""
Battery module
"""

from abc import ABC, abstractmethod

class BatteryBase(ABC):
    """ Abstract class BatteryBase.

    A bike will depend on this abstract-class, and can later be replaced with
    any class that is a subclass of BatteryBase (like code for an actual battery).
    """

    @abstractmethod
    def get_level(self):
        """ Method to get the batterylevel """

    @abstractmethod
    def set_level(self, level):
        """ Method to set the batterylevel """

class BatterySimulator(BatteryBase):
    """ The battery-class used in the simulation.
    
    Args:
        level (float): representing battery level in %.
        level_reduction (float): how much to lower level for each update.
    """
    def __init__(self, level=100, level_reduction=0.2):
        self._level = level
        self._level_reduction = level_reduction

    def get_level(self):
        """ Gets the battery level, then lower it by the given level class attribute

        Returns:
            float: The battery level
        """
        old_level = self._level
        self._level -= self._level_reduction
        return old_level

    def set_level(self, level):
        """ Sets the battery level, if needed.

        Parameter:
            level (float): the battery level to set
        """
        self._level = level
