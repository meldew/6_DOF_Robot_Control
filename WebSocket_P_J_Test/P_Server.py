import asyncio
import websockets
import json  # Import the json module for JSON serialization

J1 = 65
J2 = 30
J3 = 60
J4 = 0
J5 = 0
J6 = 0

async def handle(websocket, path):
    while True:
        # Receive data from JavaScript
        data = await websocket.recv()
        print(f"Received data from JavaScript: {data}")

        # Process the data and send a response back if needed
        response_data = {"J1, J2, J3, J4, J5, J6" : [J1, J2, J3, J4, J5, J6]}

        # Convert the dictionary to a JSON-formatted string
        response_json = json.dumps(response_data)

        # Send the JSON string to the client
        await websocket.send(response_json)

start_server = websockets.serve(handle, '127.0.0.1', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
