import serial
import time

# Configure the serial port and baud rate to match the Arduino
arduino = serial.Serial('COM3', 9600, timeout=1) # Change 'COM3' to the appropriate port for your system

time.sleep(2) # Wait for the serial connection to initialize

def send_data(data):
    arduino.write(data.encode()) # Send data to Arduino
    arduino.write(b'\n') # Send a newline character to indicate the end of data

def receive_data():
    data = arduino.readline().decode().strip() # Read data from Arduino
    return data

try:
    while True:
        send_data("Hello from Python!") # Send data to Arduino
        #time.sleep(1) # Wait for a second
        received = receive_data() # Receive data from Arduino
        if received:
            print(received) # Print the received data

except KeyboardInterrupt:
    print("Program terminated")

finally:
    arduino.close() # Close the serial connection
