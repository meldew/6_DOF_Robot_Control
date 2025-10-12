import asyncio
import websockets
import json
import serial
import serial.tools.list_ports

print("Server is running...")

# ========================
# Globals / State
# ========================
J1 = J2 = J3 = J4 = J5 = J6 = 0.0

button_states = {
    "MoveToAngle": 0,
    "Home": 0,
    "MoveJointToLeft": 0,
    "MoveJointToRight": 0
}

# From UI
checkpoint_enabled = False          # Checkpoint toggle from UI
ui_link1_telemetry_deg = None       # Last Link1Pos the UI sent (telemetry)

# Serial: NON-BLOCKING
arduino = serial.Serial('COM6', 115200, timeout=0)   # timeout=0 -> non-blocking
asyncio_serial_poll_ms = 50                          # poll serial every 50 ms


# ========================
# WebSocket -> Arduino
# ========================
async def recv_ws_and_forward_to_arduino(ws):
    """
    Receives messages from the UI.
    - Updates button_states
    - Tracks Checkpoint and UI Link1Pos telemetry
    - Forwards a merged JSON line to Arduino on EVERY message, including Filler:
        {
          MoveToAngle, Home, MoveJointToLeft, MoveJointToRight,
          Checkpoint: 0/1,
          Link1Pos: <deg>  # UI telemetry if available, else last J1 from Arduino
        }
    """
    global checkpoint_enabled, ui_link1_telemetry_deg, J1

    while True:
        msg = await ws.recv()  # await incoming WS message
        try:
            parsed = json.loads(msg)
        except Exception:
            # Ignore non-JSON noise, but still send current state
            parsed = {}

        t = parsed.get('type')
        v = parsed.get('value')

        # 1) Button-style commands -> stored
        if t in button_states:
            button_states[t] = v

        # 2) Checkpoint toggle -> store
        elif t == "Checkpoint":
            checkpoint_enabled = bool(v)

        # 3) Link1 telemetry from UI -> store (this is what we will forward as Link1Pos)
        elif t == "Link1Pos":
            try:
                ui_link1_telemetry_deg = float(parsed.get('value'))
            except (TypeError, ValueError):
                pass

        # 4) Filler or unknown -> no state change needed

        # ---- Build payload for Arduino and send it ----
        # Prefer UI telemetry for Link1Pos; fallback to last measured J1 from Arduino
        link1_to_send = ui_link1_telemetry_deg if ui_link1_telemetry_deg is not None else J1

        payload_dict = {
            **button_states,
            "Checkpoint": 1 if checkpoint_enabled else 0,
            "Link1Pos": link1_to_send
        }

        line = json.dumps(payload_dict) + '\n'
        try:
            arduino.write(line.encode('utf-8'))
        except Exception as e:
            # If serial write fails, bubble up to disconnect socket cleanly
            raise
        print(line)


# ========================
# Arduino -> WebSocket
# ========================
async def pump_serial_to_ws(ws):
    """
    Non-blocking serial reader:
    - reads whatever is available
    - parses complete lines (newline-terminated)
    - if a line is numeric, treat it as J1 angle (angle-only from Arduino)
    - sends compact JSON to the client once per parsed line
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
                    J1 = float(s)  # prefer Arduino sending only the number
                except ValueError:
                    if s.startswith("J1 Angle:"):
                        try:
                            J1 = float(s.split(":", 1)[1].strip())
                        except Exception:
                            continue
                    else:
                        continue

                # Push latest values to client
                values = {'J1': J1, 'J2': J2, 'J3': J3, 'J4': J4, 'J5': J5, 'J6': J6}
                try:
                    await ws.send(json.dumps(values))
                except Exception:
                    # client disconnected
                    raise


# ========================
# Client handler / server
# ========================
async def handle_client(ws):
    print(f"Client connected: {ws.remote_address}")

    recv_task = asyncio.create_task(recv_ws_and_forward_to_arduino(ws))
    ser_task  = asyncio.create_task(pump_serial_to_ws(ws))

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
    async with websockets.serve(
        handle_client,
        '127.0.0.1',
        8765,
        ping_interval=20,
        ping_timeout=60
    ):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
