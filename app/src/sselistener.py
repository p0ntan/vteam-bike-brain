#!/usr/bin/env python
"""
SSE listener class
"""
import asyncio
import json
import aiohttp
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
        self._loop = asyncio.get_event_loop()
        self._loop.create_task(self.listen())

    async def listen(self):
        """ Asynchronous method to start listening to events sent from server. """
        async with aiohttp.ClientSession() as session:
            async with session.get(self._api_url) as response:
                async for line in response.content:
                    if line:
                        try:
                            line = line.decode('utf-8').rstrip()
                            json_str = line[6:]
                            data = json.loads(json_str)
                            await self._control_bike(data)
                        except json.JSONDecodeError as error:
                            print(f"Error with JSON-format: {error}")
                        except Exception as error:
                            print(f"Error in SSE connection: {error}")

    async def _control_bike(self, data: dict):
        """ Async control the bike with actions setn from server.
        
        Args:
            data (dict): data to decide what to do with bike.
        """
        if data['msg'] == 'start_simulation':
            await self._bike.run_simulation()
        elif data['id'] == self._bike.id():
            print(await self._bike.get_data())