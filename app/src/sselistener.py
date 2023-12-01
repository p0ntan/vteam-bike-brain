#!/usr/bin/env python
"""
SSE listener class
"""
import asyncio
import json
from aiosseclient import aiosseclient
from src.bike import Bike
# TODO kolla upp https://github.com/JelleZijlstra/aiohttp-sse-client2

class SSEListener:
    """ Class for listening to events sent from server. Can control one or more bikes.
    The listener is giving instructions to the bike based on events from server.

    Args:
        bikes (dict[Bike]): dict of all the bikes
        api_url (str): url to where the events is sent from server
    """

    def __init__(self, bikes: dict[Bike], api_url: str):
        self._bikes = bikes
        self._api_url = api_url

    async def listen(self):
        """ Start listening to events sent from server. """
        try:
            async for event in aiosseclient(self._api_url):
                data = json.loads(event.data)
                asyncio.create_task(self._control_bike(data))
        # Disableing pylint to catch any error, might be a bit to wide but this needs
        # to keep running for all possible errors for now.
        # TODO find out possible errors and handle them accordingly. Control that running it again is a valid approach.
        # pylint: disable=broad-exception-caught
        except Exception as error:
            print(f"Error in SSE connection: {error}")

    async def _control_bike(self, data: dict):
        """ Control the bike with actions setn from server.
        
        Args:
            data (dict): data to decide what to do with bike.
        """
        if 'instruction_all' in data:
            instruction = data['instruction_all']

            match instruction:
                case 'run_simulation':
                    for bike in self._bikes.values():
                        asyncio.create_task(bike.run_simulation())
        elif 'bike_id' in data:
            instruction = data['instruction']
            bike_id = int(data['bike_id'])
            bike = self._bikes[bike_id]

            match instruction:
                case 'unlock_bike':
                    bike.unlock_bike()
                case 'lock_bike':
                    bike.lock_bike()

            # TODO ändra till något liknande
            # method_name = 'lock_bike'
            # method = getattr(bike, method_name, None)
            # if method:
            # method()
