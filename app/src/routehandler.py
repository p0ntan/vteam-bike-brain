#!/usr/bin/env python
"""
Route-handler module
"""
import os
import json
import math
from geopy.distance import lonlat, distance

class RouteHandler():
    """ A class for handling routes used for simulation
    
    Args:
        directory (str): the directory to load the routes from. Should contain .json-files.
        interval (int): the number of seconds each interval will be, decides max-length for coords-distance
    """
    def __init__(self, directory, interval=10):
        """ Constructor """
        self._routes = self._load_routes(directory)
        self._routes = self.check_distance(interval)

    @property
    def routes(self):
        """ dict[mixed]: mixed data for simulation routes with points and customer etc. """
        return self._routes

    def _load_routes(self, directory):
        """ Method to load routes from the directory. Can be used to add extra controls. 
        
        Args:
            directory (str): the directory to load the routes from. Should contain .json-files.
        
        Returns:
            dict[mixed]: data to use for simulations.
        """
        routes = {}
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                bike_id = int(filename[:-5]) # Remove .json
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r', encoding="UTF-8") as file:
                    routes[bike_id] = json.load(file) # Save into dict with filename as key (id)
        return routes

    def check_distance(self, interval):
        """ Checks distance between coordiantes and adds more if needed
        
        Args:
            interval (int): what interval to use for simulation in seconds    
        """
        max_speed_m_in_seconds = 5.5 # just under 20 km/h (19.8)
        max_length = max_speed_m_in_seconds * interval # max length between coordinates

        new_routes = self._routes.copy()
        for bike_id in new_routes.keys():
            for i, trip in enumerate(new_routes[bike_id]['trips']):
                updated_cords = []
                for j, coords in enumerate(trip['coords']):
                    try:
                        updated_cords.append(coords)
                        next_point = [trip['coords'][j+1][0], trip['coords'][j+1][1]]
                        coords_distance = distance(lonlat(*coords), lonlat(*next_point)).meters
                        extra_points_needed = coords_distance / max_length # If more than 1 distance is too long
                        if extra_points_needed > 1:
                            split_by = math.ceil(extra_points_needed)
                            lat_distance = (trip['coords'][j+1][0] - coords[0]) / split_by
                            lng_distance = (trip['coords'][j+1][1] - coords[1]) / split_by

                            for multiply_by in range(1, split_by):
                                new_lat = round(coords[0] + lat_distance * multiply_by, 6)
                                new_lng = round(coords[1] + lng_distance * multiply_by, 6)
                                updated_cords.append([new_lat, new_lng])

                    except IndexError:
                        # Last point in array
                        pass
                new_routes[bike_id]['trips'][i]['coords'] = updated_cords

        return new_routes

    # def _add_coords(self):
    #     """ Add coordinates to trip if distance is too long."""