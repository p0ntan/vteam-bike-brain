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
    # Load routes with RouteHandler
    r_handler = RouteHandler('./test-routes')
    routes = r_handler.routes

    # Get bike_data from server
    response = requests.get('http://express-server:1337/get')
    bike_data = response.json()

    # Initialize bikes with BikeFactory
    bike_factory = BikeFactory(bike_data, routes)

    # Add SSE-listener to each bike
    listeners = []
    sse_url = "http://express-server:1337/bikes/instructions"
    for bike in bike_factory.bikes:
        listeners.append(SSEListener(bike, sse_url))
        bike.start()

if __name__ == '__main__':
    main()
