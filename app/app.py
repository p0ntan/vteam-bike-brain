#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Main file for running simulation for all bikes in vteam-project.
"""
import requests

from src.bikefactory import BikeFactory
from src.routehandler import RouteHandler
from src.sselistener import SSEListener

def main():
    """ Main program to start up all bikes for simulation.

    Gets simulation data from json-files and bike-data from server. 
    """
    # Here the interval can be changed for how often bikes should update it's position
    interval_in_seconds = 10
    
    # Load routes with RouteHandler
    r_handler = RouteHandler('./routes', interval=interval_in_seconds)
    routes = r_handler.routes

    # Get bike_data from server
    response = requests.get('http://express-server:1337/get')
    bike_data = response.json()

    # Initialize bikes with BikeFactory
    bike_factory = BikeFactory(bike_data, routes, interval=interval_in_seconds)

    # Add SSE-listener to each bike
    listeners = []
    sse_url = "http://express-server:1337/bikes/instructions"
    for bike in bike_factory.bikes:
        listeners.append(SSEListener(bike, sse_url))
        bike.start()

if __name__ == '__main__':
    main()
