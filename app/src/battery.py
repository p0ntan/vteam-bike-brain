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

    @property
    @abstractmethod
    def level(self):
        """ float: the lever for the battery """

class BatterySimulator(BatteryBase):
    """ The battery-class used in the simulation.

    Args:
        level (float): representing battery level in %.
        level_reduction (float): how much to lower level for each update.
    """
    def __init__(self, level=100, level_reduction=0.2):
        self._level = level
        self._level_reduction = level_reduction

    @property
    def level(self):
        """ float: the lever of the battery. Will be lowered in simulation automaticly. """
        old_level = self._level
        self._level -= self._level_reduction
        return round(old_level, 2)
