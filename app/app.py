#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Main file for running simulation for all bikes in vteam-project.
"""
import requests
import asyncio

from src.bikefactory import BikeFactory
from src.routehandler import RouteHandler
from src.sselistener import SSEListener

async def main():
    """ Main program to start up all bikes for simulation.

    Gets simulation data from json-files and bike-data from server. 
    """
    # Here the interval can be changed for how often bikes should update it's position
    interval_in_seconds = 5
    
    # Load routes with RouteHandler
    r_handler = RouteHandler('./test-routes', interval=interval_in_seconds)
    routes = r_handler.routes

    # Get bike_data from server
    response = requests.get('http://express-server:1337/v1/get')
    bike_data = response.json()

    # Initialize bikes with BikeFactory
    bike_factory = BikeFactory(bike_data, routes, interval=interval_in_seconds)

    # Add SSE-listener to each bike
    listeners = []
    sse_url = "http://express-server:1337/v1/bikes/instructions"
    tasks = []
    for bike in bike_factory.bikes:
        listener = SSEListener(bike, sse_url)
        listeners.append(listener)
        tasks.append(bike.start())

    print("Running.")
    
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
