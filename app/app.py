#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Main file for running simulation for all bikes in vteam-project.
"""
import requests
import asyncio
import threading

from src.bikefactory import BikeFactory
from src.routehandler import RouteHandler
from src.sselistener import SSEListener

def start_sse(bikes, url):
    """ Function to start the SSEListener in an own thread and eventloop.

    Args:
        bikes (list[Bike]): list of all the bikes to give instructions to
        url (str): URL to get events from server
    """
    async def async_start():
        listener = SSEListener(bikes, url)
        await listener.listen()
    
    asyncio.run(async_start())

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

    # Start SSE in it's own thread
    sse_url = "http://express-server:1337/v1/bikes/instructions"
    sse_thread = threading.Thread(target=start_sse, args=(bike_factory.bikes, sse_url))
    sse_thread.start()

    tasks = []
    for bike in bike_factory.bikes.values():
        tasks.append(bike.start())

    print("Running")

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
