import asyncio
import websockets
import json
print("Server is running...")
J1 = 0
J2 = 0
J3 = 0
J4 = 0
J5 = 0
J6 = 0
J1direction = 1  
J2direction = 1  
J3direction = 1  
J4direction = 1
async def handle_client(websocket, path):
    global J1, J2, J3, J4, J5, J6, J1direction, J2direction, J3direction, J4direction
    while True:   
        try:
            try:
                incoming_msg = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                print(f"Received message: {incoming_msg}")

            except asyncio.TimeoutError:
                pass

            values = {
                'J1': J1,
                'J2': J2,
                'J3': J3,
                'J4': J4,
                'J5': J5,
                'J6': J6
            }
            values_json = json.dumps(values) 
            await websocket.send(values_json) 
            
            if J1 >= 140:
                J1direction = -1  
            elif J1 <= -140:
                J1direction = 1  

            if J2 >= 100:
                J2direction = -1  
            elif J2 <= -90:
                J2direction = 1  

            if J3 >= 140:
                J3direction = -1  
            elif J3 <= -140:
                J3direction = 1  

            if J4 >= 180:
                J4direction = -1  
            elif J4 <= -180:
                J4direction = 1 

            J1 += J1direction  
            J2 += J2direction
            J3 += J3direction * 3
            J4 += J4direction * 3 
            #await asyncio.sleep(0.02)    
        except Exception as e:
            print(f"An error occurred: {e}")
            break
start_server = websockets.serve(handle_client, '127.0.0.1', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()