import asyncio
import websockets
import json
import time
import serial
import serial.tools.list_ports

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

connected_clients = set()

button_states = {
    "MoveToAngle": 0,
    "Home": 0,
    "MoveJointToLeft": 0,
    "MoveJointToRight": 0
}


arduino = serial.Serial('COM3', 115200, timeout=1)
time.sleep(3)

async def handle_client(websocket, path):
    connected_clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")
    
    global J1, J2, J3, J4, J5, J6, J1direction, J2direction, J3direction, J4direction, ser

    while True:   
        try:
            try:
                incoming_msg = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                parsed_msg = json.loads(incoming_msg)
                message_type = parsed_msg.get('type')
                value = parsed_msg.get('value') 

                if message_type in button_states:
                    button_states[message_type] = value
                
                json_data = json.dumps(button_states) + '\n'
                arduino.write(json_data.encode('utf-8'))
                
                

                data = arduino.readline().decode().strip()
                if data: 
                    print(f"Received from Arduino: {data}")
                    if data.startswith("J1 Angle:"):
                        J1 = float(data.split(":")[1])
                
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
                        
            except asyncio.TimeoutError:
                continue  
        
            #await asyncio.sleep(0.02)    
        except Exception as e:
            print(f"An error occurred: {e}")
            break
start_server = websockets.serve(handle_client, '127.0.0.1', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()