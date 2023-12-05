#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Main file for running simulation for all bikes in vteam-project.
"""
import os
import threading
import asyncio
import requests

from src.bikefactory import BikeFactory
from src.routehandler import RouteHandler
from src.sselistener import SSEListener

#
# TODO kolla igenom kommentarer så de stämmer med vad som görs i kod
# TODO få bort match/case och använd något mer lämpligt
# TODO va mer?
# TODO se till att programmet inte stoppar när den tappar kontakt med servern.
#


def start_sse(bikes, url):
    """ Function to start the SSEListener in an own thread and eventloop.

    Args:
        bikes (dict[Bike]): dict of all the bikes to give instructions to
        url (str): URL to get events from server
    """
    async def async_start():
        tasks = []
        for bike in bikes.values():
            listener = SSEListener(bike, url)
            tasks.append(listener.listen())

        await asyncio.gather(*tasks)

    asyncio.run(async_start())


async def main():
    """ Main program to start up all bikes for simulation.

    Gets simulation data from json-files and bike-data from server.
    """
    # Here the interval can be changed for how often bikes should update it's position
    interval_in_seconds = 10

    # API-URL
    base_url = os.environ['API_URL']

    # Load routes with RouteHandler
    r_handler = RouteHandler('./routes', interval=interval_in_seconds)
    routes = r_handler.routes

    # Get bike_data from server
    response = requests.get(f"{base_url}/get", timeout=1.5)
    bike_data = response.json()

    # Initialize bikes with BikeFactory
    bike_factory = BikeFactory(bike_data, routes, interval=interval_in_seconds)

    # Start bikes
    tasks = []
    for bike in bike_factory.bikes.values():
        tasks.append(bike.start())

    # Start SSE:s in it's own thread
    sse_url = f"{base_url}/bikes/instructions"
    sse_thread = threading.Thread(target=start_sse, args=(bike_factory.bikes, sse_url))
    sse_thread.start()

    print("Running")

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
