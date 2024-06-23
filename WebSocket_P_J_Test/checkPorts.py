
import serial.tools.list_ports

print("Available ports:")
ports = serial.tools.list_ports.comports()
for port in ports:
    print(port)    