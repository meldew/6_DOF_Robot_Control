# Not in use for now.

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




function createPanel() {
    const gui = new GUI();
    const branch_Kinematics = gui.addFolder( 'Robot Forward Kinematics' );
    const branch_Duplex_Com = gui.addFolder( 'Python Duplex Communication' );

    branch_Kinematics.add(options, 'Link1', -180, 180).listen();
    branch_Kinematics.add(options, 'Link2', -180, 180).listen();
    branch_Kinematics.add(options, 'Link3', -180, 180).listen();
    branch_Kinematics.add(options, 'Link4', -180, 180).listen();
    branch_Kinematics.add(options, 'Link5', -180, 180).listen();
    branch_Kinematics.add(options, 'Link6', -180, 180).listen();
    branch_Kinematics.open();
    
    branch_Duplex_Com.add(options, 'TransmitData').name('Send Data to Python').onChange(function(value) {
        if (sendDataIntervalId !== null) {
            clearInterval(sendDataIntervalId);
            sendDataIntervalId = null;
        }
        if (value) {
            sendDataIntervalId = setInterval(() => {
                const testMessage = { type: 'Home', value: options.Link1 };
                //socket.send(JSON.stringify(testMessage)); // Add data, peew peew peew 
            }, 100);
        } else {
            if (sendDataIntervalId !== null) {
                clearInterval(sendDataIntervalId);
                sendDataIntervalId = null;
            }
        } 
    });

    branch_Duplex_Com.add(options, 'sendMoveToAngleRequest').name('Move to angle');
    branch_Duplex_Com.add(options, 'sendHomeRequest').name('Home');
    
    const folder2Title = branch_Duplex_Com.domElement.querySelector('.title');
    const gui2Title = gui.domElement.querySelector('.title');
    const customContainer = document.createElement('div');

    const moveJointToLeftButton = createButton(
        'Move Joint to Left',
        () => sendMoveJointToLeftMessage(1),
        () => sendMoveJointToLeftMessage(0)
    );
    const moveJointToRightButton = createButton(
        'Move Joint to Right',
        () => sendMoveJointToRightMessage(1),
        () => sendMoveJointToRightMessage(0)
    );
    
    customContainer.appendChild(moveJointToLeftButton);
    customContainer.appendChild(moveJointToRightButton);
    branch_Duplex_Com.domElement.appendChild(customContainer);

    if (folder2Title) {
        folder2Title.addEventListener('click', () => {
            const display1 = customContainer.style.display === 'none' ? 'block' : 'none';
            customContainer.style.display = display1;
        });
    }




import asyncio
import websockets
import json
import time
import serial
import serial.tools.list_ports

print("Server is running...")
ser = None
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

connected_clients = set()

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
    connected_clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")
    
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
                    message2Arduino = json.dumps(button_states)
                    print(f"Sending message to Arduino: {message2Arduino}")
                    ser.write(message2Arduino.encode())
                
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

# Function to check for available ports and connect to COM3
def connect_to_com3():
    global ser
    while ser is None:
        ports = serial.tools.list_ports.comports()
        for port in ports:
            print(f"Checking port: {port}")
            if port.device == 'COM3':
                try:
                    ser = serial.Serial('COM3', 9600, timeout=1)
                    print("Successfully connected to COM3")
                    return "Port_found"
                except serial.SerialException as e:
                    print(f"Could not open port 'COM3': {e}")
        time.sleep(1)  # Wait for 1 second before checking again