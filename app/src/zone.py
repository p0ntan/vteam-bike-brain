#!/usr/bin/env python
"""
Zone-module
"""

from shapely.geometry import Point, Polygon


class Zone():
    """ Zone-class that will be used as a base for all zones in a city.

    Args:
        data (dict): with data needed for the zone
        speed_limit (int = 20): optional paramater if data doesn't contain a speed limit.
    """

    def __init__(self, data: dict, speed_limit: int = 20):
        """ Constructor """
        coords = data.get('geometry')
        self._coordinates = coords.get('coordinates')[0]
        self._speed_limit = data.get('speed_limit', speed_limit)

    @property
    def speed_limit(self):
        """ int: the speed limit in the zone """
        return self._speed_limit

    def point_in_zone(self, point_coords: list):
        """ See if a point is inside the zone.

        Args:
            point_coords (list[float, float]): list with coordinates [longitude, latitude]

        Returns:
            bool: true if the point is inside the zone
        """
        polygon = Polygon(self._coordinates)
        point = Point(*point_coords)

        return polygon.contains(point)


class CityZone(Zone):
    """ CityZone represents the city. Based on the Zone-class but can also contain other zoners.

    Args:
        data (dict): with data needed for the zone
        speed_limit (int = 20): optional paramater if data doesn't contain a speed limit.
    """

    def __init__(self, data: dict, speed_limit: int = 20):
        """ Constructor """
        super().__init__(data, speed_limit)
        self._zones = []
        self._city_id = data.get('city_id', '')

    @property
    def city_id(self):
        """ str: id of city. """
        return self._city_id

    def add_zone(self, zone: Zone):
        """ Add a zone to city.

        Args:
            zone (Zone): Zone to add
        """
        self._zones.append(zone)

    def add_zones_list(self, zones: list):
        """ Add zones to city.

        Args:
            zones (list): list of zones
        """
        for zone in zones:
            self._zones.append(zone)

    def get_speed_limit(self, point):
        """ Loops through all zones and returns the speed limit.

        Args:
            point (list[float, float]): list with coordinates [longitude, latitude]
        Returns:
            int: speed limit of the current zone.
        """
        # If the point is outside the city.
        if not self.point_in_zone(point):
            return 0

        # If in city, loop through all zones and return speed limit.
        for zone in self._zones:
            if zone.point_in_zone(point):
                return zone.speed_limit

        # And if not in any zone meaning the bike has no restrictions.
        return self.speed_limit
