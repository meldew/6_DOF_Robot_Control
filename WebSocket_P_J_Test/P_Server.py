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
messages = []

button_states = {
    "MoveToAngle": 0,
    "Home": 0,
    "MoveJointToLeft": 0,
    "MoveJointToRight": 0
}

def handle_move_to_angle(message):
    print("Handling MoveToAngle message:", message)

def handle_home(message):
    print("Handling Home message:", message)

def handle_move_joint_to_left(message):
    print("Handling MoveJointToLeft message:", message)

def handle_move_joint_to_right(message):
    print("Handling MoveJointToRight message:", message)

async def handle_client(websocket, path):
    global J1, J2, J3, J4, J5, J6, J1direction, J2direction, J3direction, J4direction
    while True:   
        try:
            try:
                incoming_msg = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                parsed_msg = json.loads(incoming_msg)
                message_type = parsed_msg.get('type')
                value = parsed_msg.get('value')
  
                if message_type in button_states:
                    button_states[message_type] = value
                
                messages.append(parsed_msg)
                print(button_states)
                    
            except asyncio.TimeoutError:
                pass
        
            #await asyncio.sleep(0.02)    
        except Exception as e:
            print(f"An error occurred: {e}")
            break
start_server = websockets.serve(handle_client, '127.0.0.1', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

