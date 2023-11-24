#!/usr/bin/env python
"""
Battery module
"""

from abc import ABC, abstractmethod

class BatteryBase(ABC):
    """
    Abstract class BatteryBase.

    A bike will depend on this abstract-class, and can later be replaced with
    any class that is a subclass of BatteryBase (like code for an actual battery).
    """

    @abstractmethod
    def get_level(self):
        """ Abstract method """


class BatterySimulator(BatteryBase):
    """
    The battery-class used in the simulation.
    """
    def __init__(self, level=100, level_reduction=0.2):
        """
        Constructor for the BatterySimulator

        Parameter:
            level (float): representing battery level in %
            level_reduction (float): how much to lower level for each update
        """
        self._level = level
        self._level_reduction = level_reduction
    
    def get_level(self):
        """
        Gets the battery level, then lower it by the given level class attribute

        Returns:
            float: The battery level
        """
        old_level = self._level
        self._level -= self._level_reduction
        return old_level
