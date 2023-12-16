# #!/usr/bin/env python3
# # -*- coding: UTF-8 -*-
""" Module for testing the class SSEListener """

import pytest
import json
import asyncio
from unittest.mock import MagicMock, patch
from src.sselistener import SSEListener


class MockEvent:
    """ Mocking the event that is returned for the MockAsyncIter. """
    def __init__(self, data):
        self.data = json.dumps(data)


class MockAsyncIter:
    """ Iteration class needed for mocking aiosseclient """
    def __init__(self, events):
        self.events = events

    async def __aiter__(self):
        for event in self.events:
            yield MockEvent(event)
        # After iteration, force the iteration to stop.
        raise StopAsyncIteration


@pytest.mark.asyncio
async def test_run_simulation():
    """ Test to run the simulation for a bike, triggered through an SSE. """
    mock_bike = MagicMock()
    mock_bike.id = 123
    mock_bike.api_key = "test_key"
    listener = SSEListener(mock_bike, "http://justatest.bikes")
    instruction = {'instruction_all': 'run_simulation'}

    with patch('src.sselistener.aiosseclient', return_value=MockAsyncIter([instruction])):
        listen_task = asyncio.create_task(listener.listen())
        await asyncio.sleep(0.2)
        listener.stop_listener()
        await listen_task

    mock_bike.run_simulation.assert_called()


@pytest.mark.asyncio
async def test_lock_bike():
    """ Test to lock the bike with id. """
    mock_bike = MagicMock()
    mock_bike.id = 123
    mock_bike.api_key = "test_key"
    listener = SSEListener(mock_bike, "http://justatest.bikes")
    instruction = {
        'bike_id': 123,
        'instruction': 'lock_bike'
    }

    with patch('src.sselistener.aiosseclient', return_value=MockAsyncIter([instruction])):
        listen_task = asyncio.create_task(listener.listen())
        await asyncio.sleep(0.2)
        listener.stop_listener()
        await listen_task

    mock_bike.lock_bike.assert_called()


@pytest.mark.asyncio
async def test_lock_bike_wrong_id():
    """ Test to lock bike with wrong id, not expecting the method to be called. """
    mock_bike = MagicMock()
    mock_bike.id = 123
    mock_bike.api_key = "test_key"
    listener = SSEListener(mock_bike, "http://justatest.bikes")
    instruction = {
        'bike_id': 321,
        'instruction': 'lock_bike'
    }

    with patch('src.sselistener.aiosseclient', return_value=MockAsyncIter([instruction])):
        listen_task = asyncio.create_task(listener.listen())
        await asyncio.sleep(0.2)
        listener.stop_listener()
        await listen_task

    mock_bike.lock_bike.assert_not_called()


@pytest.mark.asyncio
async def test_change_status():
    """ Test to change status on a bike. """
    mock_bike = MagicMock()
    mock_bike.id = 123
    mock_bike.api_key = "test_key"
    listener = SSEListener(mock_bike, "http://justatest.bikes")
    instruction = {
        'bike_id': 123,
        'instruction': 'set_status',
        'args': [2]
    }

    with patch('src.sselistener.aiosseclient', return_value=MockAsyncIter([instruction])):
        listen_task = asyncio.create_task(listener.listen())
        await asyncio.sleep(0.2)
        listener.stop_listener()
        await listen_task

    mock_bike.set_status.assert_called_with(2)
