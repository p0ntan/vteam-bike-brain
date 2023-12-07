# #!/usr/bin/env python3
# # -*- coding: UTF-8 -*-
# """ Module for testing the class SSEListener """

# import pytest
# from src.sselistener import SSEListener

# def test_sselistener():
#     pass

# @pytest.mark.asyncio
# async def test_sse_listener():
#     # Mock the Bike instance
#     mock_bike = MagicMock()
#     mock_bike.id = 123

#     # Create an instance of SSEListener
#     listener = SSEListener(mock_bike, "http://example.com")

#     # Mock the aiosseclient to simulate SSE events
#     mock_sse_client = AsyncMock()
#     mock_sse_client.return_value.__aiter__.return_value = [
#         MagicMock(data=json.dumps({'instruction': 'start'})),
#         # Add more mocked events as needed
#     ]

#     with patch('src.sselistener.aiosseclient', mock_sse_client):
#         # Test the listen method
#         await listener.listen()

#         # Add assertions to check if the Bike methods were called correctly
#         # e.g., mock_bike.start.assert_called_once()
