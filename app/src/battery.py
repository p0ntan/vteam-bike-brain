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

    @abstractmethod
    def needs_charging(self):
        """
        Returns:
            boolean: if battery is low and needs charging
        """

    @abstractmethod
    def low_battery(self):
        """
        Returns:
            boolean: if battery is too low for keep renting
        """


class BatterySimulator(BatteryBase):
    """ The battery-class used in the simulation.

    Args:
        level (float): representing battery level (1 = 100 %).
        level_reduction (float): how much to lower level for each update.
    """
    def __init__(self, level: float = 1.00, level_reduction: float = 0.001):
        self._level = level
        self._level_reduction = level_reduction

    @property
    def level(self):
        """ float: the lever of the battery. Will be lowered in simulation automaticly. """
        old_level = self._level

        # Make sure the battery stops at 0
        self._level -= self._level_reduction
        self._level = 0 if self._level < 0 else self._level

        return old_level

    def needs_charging(self):
        """ Tells if battery needs charging.

        Returns:
            boolean: if battery is low and needs charging
        """
        return self._level <= 0.15

    def low_battery(self):
        """ Tells if battery needs is too low for keep renting.

        Returns:
            boolean: if battery is too
        """
        return self._level <= 0.03
