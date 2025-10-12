import asyncio
import websockets
import json
import time
import serial
import serial.tools.list_ports

import asyncio
import json
import serial

print("Server is running...")

# ---- Globals you had ----
J1 = J2 = J3 = J4 = J5 = J6 = 0.0
button_states = {
    "MoveToAngle": 0,
    "Home": 0,
    "MoveJointToLeft": 0,
    "MoveJointToRight": 0
}

# Make serial NON-BLOCKING
arduino = serial.Serial('COM6', 115200, timeout=0)   # <-- timeout=0
asyncio_serial_poll_ms = 50                          # poll serial every 50ms

async def recv_ws_and_forward_to_arduino(ws):
    """Receive UI commands over WS and forward the button_states JSON to Arduino."""
    while True:
        msg = await ws.recv()   # awaits, yields to event loop (pings are handled)
        parsed = json.loads(msg)
        t = parsed.get('type')
        v = parsed.get('value')
        if t in button_states:
            button_states[t] = v

        # forward current button state to Arduino
        payload = json.dumps(button_states) + '\n'
        try:
            arduino.write(payload.encode('utf-8'))
        except Exception as e:
            # If serial write fails, raise to disconnect the client cleanly
            raise

async def pump_serial_to_ws(ws):
    """
    Non-blocking serial reader:
    - reads whatever is available
    - parses complete lines
    - if a line is numeric, treat it as J1 angle (angle-only from Arduino)
    - sends a compact JSON to the client at most once per line
    """
    buf = b""
    global J1, J2, J3, J4, J5, J6

    while True:
        await asyncio.sleep(asyncio_serial_poll_ms / 1000.0)

        try:
            n = arduino.in_waiting
        except Exception:
            n = 0

        if n:
            chunk = arduino.read(n)
            if not chunk:
                continue
            buf += chunk

            while b'\n' in buf:
                line, buf = buf.split(b'\n', 1)
                s = line.decode('utf-8', errors='ignore').strip()
                if not s:
                    continue

                # Accept angle-only lines; ignore anything else
                try:
                    J1 = float(s)  # angle-only from Arduino (recommended)
                except ValueError:
                    # If your Arduino still prints "J1 Angle:xx.xx", allow this fallback:
                    if s.startswith("J1 Angle:"):
                        try:
                            J1 = float(s.split(":", 1)[1].strip())
                        except Exception:
                            continue
                    else:
                        # ignore any non-numeric chatter
                        continue

                # Send latest values to client
                values = {'J1': J1, 'J2': J2, 'J3': J3, 'J4': J4, 'J5': J5, 'J6': J6}
                try:
                    await ws.send(json.dumps(values))
                except Exception:
                    # client disconnected
                    raise

async def handle_client(ws):
    print(f"Client connected: {ws.remote_address}")
    # Two tasks: one for inbound WS->serial, one for serial->WS
    recv_task = asyncio.create_task(recv_ws_and_forward_to_arduino(ws))
    ser_task  = asyncio.create_task(pump_serial_to_ws(ws))

    # If either task errors, cancel the other and exit
    done, pending = await asyncio.wait(
        {recv_task, ser_task}, return_when=asyncio.FIRST_EXCEPTION
    )
    for t in pending:
        t.cancel()
    for t in done:
        exc = t.exception()
        if exc:
            print(f"Task ended with error: {exc}")

async def main():
    # Increase ping timeout so transient delays don’t kill the socket
    async with websockets.serve(
        handle_client,
        '127.0.0.1',
        8765,
        ping_interval=20,   # seconds between pings
        ping_timeout=60     # wait up to 60s for pong
    ):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
