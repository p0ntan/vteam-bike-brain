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

# TODO fixa med kommentarer, dela upp i två olika filer för sim och enskild cykel.

async def main():
    """ Main program to start up all bikes for simulation.

    Gets simulation data from json-files and bike-data from server.
    """
    # Here the interval can be changed for how often bikes should update it's position
    interval_in_seconds = 10

    # API-URL
    base_url = os.environ.get('API_URL', '')

    # Load routes with RouteHandler
    base_dir = os.path.dirname(__file__)
    routes_dir = os.path.join(base_dir, 'routes')
    r_handler = RouteHandler(routes_dir, interval=interval_in_seconds)
    routes = r_handler.routes

    # Get bike_data from server
    headers = {'x-api-key': '080d17d62d28f82a97922ce6640a4a03'}
    response = requests.get(f"{base_url}/bikes", headers=headers, timeout=1.5)
    bike_data = response.json()

    # Get zones for bikes in simulation.
    city_zones = {}
    for bike_id in [1, 600, 800]:
        response = requests.get(f"{base_url}/bikes/{bike_id}/zones", headers=headers, timeout=1.5)
        data = response.json()
        city_zones[data.get('city_id')] = data

    # Initialize bikes with BikeFactory
    bike_factory = BikeFactory(bike_data, routes, city_zones, interval=interval_in_seconds)

    # Start bikes and listeners as separate tasks.
    tasks = []
    for bike in bike_factory.bikes.values():
        sse_url = f"{base_url}/bikes/instructions"
        listener = SSEListener(bike, sse_url)
        tasks.append(listener.listen())
        tasks.append(bike.start())

    print("Running")

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
