#!/usr/bin/env python
"""
SSE listener class
"""
import threading
import json
from sseclient import SSEClient

class SSEListener:
    """
    Class for listening to events
    """
    URL = "http://express-server:1337/bikes/instructions"

    def __init__(self, bike_instance):
        self._bike = bike_instance
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()

    def listen(self):
        try:
            for event in SSEClient(self.URL):
                data = json.loads(event.data)
                
                if 'msg' in data and data['msg'] == 'start_simulation':
                    self._bike.stop()
                    self._bike.run_simulation()
    
                if data['id'] == self._bike.id():
                    print(self._bike.get_data())

        except Exception as e:
            print(f"Error in SSE connection: {e}")
