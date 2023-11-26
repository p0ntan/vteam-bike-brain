#!/usr/bin/env python
"""
Route-handler module
"""
import os
import json
# from geopy.distance import lonlat, distance

class RouteHandler():
    """ A class for handling routes used for simulation
    
    Args:
        directory (str): the directory to load the routes from. Should contain .json-files.
    """
    def __init__(self, directory):
        """ Constructor """
        self._routes = self._load_routes(directory)

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
                bike_id = filename[:-5] # Remove .json
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r', encoding="UTF-8") as file:
                    routes[int(bike_id)] = json.load(file) # Save into dict with filename as key (id)
        return routes

    # def _check_coordinates(self, routes):
    #     for route in routes.values():
    #         for trips in route['trips']:
    #             for i, coord in enumerate(trips):
    #                 if i == 0:
    #                     continue
    #                 last_point = (trips[i-1][0], trips[i-1][1])
    #                 new_point = (coord[0], coord[1])
    #                 coords_distance = distance(lonlat(*last_point), lonlat(*new_point)).meters

    #                 if coords_distance > 300:
    #                     # Use recursion for adding new coordinates
    #                     print(last_point, new_point)
    #                     print(coords_distance)

    #     return routes

    # def _add_coords(self):
    #     """ Add coordinates to trip if distance is too long."""
