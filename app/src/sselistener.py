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

                if 'msg' in data and data['msg'] == 'start_simulation':
                    self._bike.stop()
                    self._bike.run_simulation()

                if data['id'] == self._bike.id():
                    print(self._bike.get_data())

        except Exception as error:
            print(f"Error in SSE connection: {error}")
