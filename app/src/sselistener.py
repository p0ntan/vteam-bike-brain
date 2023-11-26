#!/usr/bin/env python
"""
SSE listener class
"""
import threading
import json
from sseclient import SSEClient
from src.bike import Bike

class SSEListener:
    """ Class for listening to events, used for each bike.
    The listener is giving instructions to the bike based on events from server.

    Args:
        bike_instance (Bike): the bike to "wrap" the listener around
    """
    URL = "http://express-server:1337/bikes/instructions"

    def __init__(self, bike_instance: Bike):
        self._bike = bike_instance
        self._thread = threading.Thread(target=self.listen)
        self._thread.start()

    def listen(self):
        """ Start listening to events sent from server. """
        try:
            for event in SSEClient(self.URL):
                data = json.loads(event.data)
                self._control_bike(data)
        # Disableing pylint to catch any error, might be a bit to wide but this needs
        # to keep running for all possible errors for now.
        # TODO find out possible errors and handle them accordingly
        # pylint: disable=broad-exception-caught
        except Exception as error:
            print(f"Error in SSE connection: {error}")

    def _control_bike(self, data: dict):
        """ Control the bike with actions setn from server.
        
        Args:
            data (dict): data to decide what to do with bike.
        """
        if 'msg' in data and data['msg'] == 'start_simulation':
            self._bike.stop()
            self._bike.run_simulation()

        if data['id'] == self._bike.id():
            print(self._bike.get_data())
