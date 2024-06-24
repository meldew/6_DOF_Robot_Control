import serial
import time

# Bruk riktig port for Arduino
port_name = '/dev/cu.usbmodem112301'  # Oppdatert med riktig portnavn

try:
    ser = serial.Serial(port_name, 9600)  # Åpne seriel porten
    time.sleep(2)  # Vent til tilkoblingen er etablert

    # JSON-melding å sende
    message = '{"MoveToAngle":1,"Home":0,"MoveJointToLeft":1,"MoveJointToRight":0}\n'

    # Send meldingen
    ser.write(message.encode('utf-8'))
    print("Melding sendt til Arduino:", message)

    # Lukk seriel porten
    ser.close()
except serial.SerialException as e:
    print(f"Feil ved åpning eller bruk av seriel port: {e}")
except Exception as e:
    print(f"En feil oppstod: {e}")