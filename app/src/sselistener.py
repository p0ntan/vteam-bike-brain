#!/usr/bin/env python
"""
SSE listener class
"""
import asyncio
import json
from aiosseclient import aiosseclient
from src.bike import Bike


class SSEListener:
    """ Class for listening to events, used for each bike.
    The listener is giving instructions to the bike based on events from server.

    Args:
        bike_instance (Bike): the bike to "wrap" the listener around
        api_url (str): url to where the events is sent from server
    """

    def __init__(self, bike_instance: Bike, api_url: str):
        self._bike = bike_instance
        self._api_url = api_url

    async def listen(self):
        """ Start listening to events sent from server. """
        headers = {'bike_id': str(self._bike.id)}
        reconnection_attempts = 0
        while True:
            try:
                async for event in aiosseclient(self._api_url, headers=headers):
                    data = json.loads(event.data)
                    asyncio.create_task(self._control_bike(data))
            # Disableing pylint to catch any error, might be a bit to wide but this needs
            # to keep running for all possible errors for now.
            # TODO find out possible errors and handle them accordingly.
            # Control that running it again is a valid approach.
            # pylint: disable=broad-exception-caught
            except Exception as error:
                print(f"Error in SSE connection: {error}")
                reconnection_attempts += 1
                await asyncio.sleep(reconnection_attempts)

    async def _control_bike(self, data: dict):
        """ Control the bike with actions setn from server.

        Args:
            data (dict): data to decide what to do with bike.
        """
        args = data.get('args', [])

        if 'instruction_all' in data:
            instruction = data.get('instruction_all')
            action = getattr(self._bike, instruction)
            asyncio.create_task(action(*args))

        elif 'bike_id' in data and int(data.get('bike_id')) == self._bike.id:
            instruction = data.get('instruction')
            action = getattr(self._bike, instruction)
            action(*args)
