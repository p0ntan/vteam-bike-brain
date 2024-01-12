#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Main file for running simulation for all bikes in vteam-project.
"""
import os
import asyncio
import requests

from src.bikefactory import BikeFactory
from src.routehandler import RouteHandler
from src.sselistener import SSEListener


async def main():
    """ Main program to start up all bikes for simulation.

    Gets simulation data from json-files and bike-data from server.
    """
    # Here the interval can be changed for how often bikes should update it's position
    interval_in_seconds = 3

    # API-URL
    base_url = os.environ.get('API_URL', '')

    # API-key
    api_key = os.environ.get('API_KEY', '')

    # Load routes with RouteHandler
    base_dir = os.path.dirname(__file__)
    routes_dir = os.path.join(base_dir, 'routes')
    r_handler = RouteHandler(routes_dir, interval=interval_in_seconds)
    routes = r_handler.routes

    # Get bike_data from server
    headers = {'x-api-key': api_key}
    response = requests.get(f"{base_url}/bikes", headers=headers, timeout=1.5)
    bike_data = response.json()

    # Initialize bikes with BikeFactory
    bike_factory = BikeFactory(bike_data, routes, interval=interval_in_seconds)

    # Start listeners to use for simulation.
    tasks = []
    for bike in bike_factory.bikes.values():
        sse_url = f"{base_url}/bikes/instructions"
        listener = SSEListener(bike, sse_url)
        tasks.append(listener.listen())

    print("Running")

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
