import serial
import time

arduino_port = 'COM3'  # Update this to your correct COM port
baud_rate = 115000

# Initialize the serial connection
arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
time.sleep(2)  # Allow time for Arduino to initialize

try:
    while True:
        # Send data to Arduino
        message = 'Hello, Arduino!'
        arduino.write((message + '\n').encode())  # Append newline character
        print(f"Sent: {message}")

        # Read response from Arduino
        response = arduino.readline().decode().strip()
        if response:
            print(f"Received: {response}")

        time.sleep(1)  # Adjust the sleep time as needed
except KeyboardInterrupt:
    print("Interrupted by user. Closing the connection.")
finally:
    arduino.close()
    print("Connection closed.")