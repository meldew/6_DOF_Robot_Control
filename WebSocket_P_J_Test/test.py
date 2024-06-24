import serial
import time
import json

# Open the serial connection
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize

button_states = {
    "MoveToAngle": 1,
    "Home": 0,
    "MoveJointToLeft": 1,
    "MoveJointToRight": 0
}

while True:
    # Convert the dictionary to a JSON string and add a newline character
    json_data = json.dumps(button_states) + '\n'
    arduino.write(json_data.encode('utf-8'))  # Send data to Arduino

    data = arduino.readline().decode().strip()  # Read data from Arduino
    if data:
        print(data)  # Print the received data