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

#
# TODO kolla igenom kommentarer så de stämmer med vad som görs i kod, lägg till typer
# TODO få bort match/case och använd något mer lämpligt
# TODO va mer?
# TODO se till att programmet inte stoppar när den tappar kontakt med servern.
#


async def main():
    """ Main program to start up all bikes for simulation.

    Gets simulation data from json-files and bike-data from server.
    """
    # Here the interval can be changed for how often bikes should update it's position
    interval_in_seconds = 10

    # API-URL
    base_url = os.environ.get('API_URL', '')

    # Load routes with RouteHandler
    r_handler = RouteHandler('./routes', interval=interval_in_seconds)
    routes = r_handler.routes

    # Get bike_data from server
    response = requests.get(f"{base_url}/bikes", timeout=1.5)
    bike_data = response.json()

    # Initialize bikes with BikeFactory
    bike_factory = BikeFactory(bike_data, routes, interval=interval_in_seconds)

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
