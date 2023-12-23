import asyncio
import websockets
import json  # Import the json module for JSON serialization

async def handle(websocket, path):
    while True:
        # Receive data from JavaScript
        data = await websocket.recv()
        print(f"Received data from JavaScript: {data}")

        # Process the data and send a response back if needed
        response_data = {"message": "Data received in Python"}

        # Convert the dictionary to a JSON-formatted string
        response_json = json.dumps(response_data)

        # Send the JSON string to the client
        await websocket.send(response_json)

start_server = websockets.serve(handle, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
