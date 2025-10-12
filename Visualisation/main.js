console.log('main.js loaded');
import * as THREE from 'three';
import WebGL from 'three/addons/capabilities/WebGL.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
import Stats from 'three/addons/libs/stats.module.js';

const socket = new WebSocket('ws://127.0.0.1:8765');

// ---- Scene graph nodes ----
const shoulder = new THREE.Object3D();
const joint2   = new THREE.Object3D();
const joint3   = new THREE.Object3D();
const joint4   = new THREE.Object3D();
const joint5   = new THREE.Object3D();

// ---- Axes ----
const zAxis = new THREE.Vector3(0, 0, 1);
const yAxis = new THREE.Vector3(0, 1, 0);
const xAxis = new THREE.Vector3(1, 0, 0);

// ---- Config / telemetry smoothing ----
const LINK1_DEADBAND_DEG = 0.8;  // ignore <= this delta (helps kill jitter)
const LINK1_QUANT_STEP   = 0.5;  // snap to nearest step (stabilizes stream)

// ---- Buttons ----
const buttonDelaytime = 50;

// ---- Runtime state ----
let J1 = 0, J2 = 0, J3 = 0, J4 = 0, J5 = 0, J6 = 0;

// Interval/timers
let checkpointTimerId = null;     // drives filler + optional Link1 telemetry
let lastSentLink1 = null;         // last sent (after quantization)

// ---- GUI options ----
const options = {
  Link1: 0, Link2: 0, Link3: 0, Link4: 0, Link5: 0, Link6: 0,

  // NEW: telemetry checkpoint toggle + rate (Hz)
  Checkpoint: false,
  CheckpointHz: 60, // GUI-adjustable; 10 Hz default

  // Keep your existing flag for enabling socket traffic
  TransmitData: false,

  // Your existing momentary commands
  sendMoveToAngleRequest() {
    if (!options.TransmitData) return console.log('TransmitData disabled');
    const on  = { type: 'MoveToAngle', value: 1 };
    const off = { type: 'MoveToAngle', value: 0 };
    socket.send(JSON.stringify(on));
    setTimeout(() => socket.send(JSON.stringify(off)), buttonDelaytime);
  },
  sendHomeRequest() {
    if (!options.TransmitData) return console.log('TransmitData disabled');
    const on  = { type: 'Home', value: 1 };
    const off = { type: 'Home', value: 0 };
    socket.send(JSON.stringify(on));
    setTimeout(() => socket.send(JSON.stringify(off)), buttonDelaytime);
  }
};

// ---- Helpers to send ----
function sendMoveJointToLeftMessage(value) {
  if (!options.TransmitData) return console.log('TransmitData disabled');
  socket.send(JSON.stringify({ type: 'MoveJointToLeft', value }));
}
function sendMoveJointToRightMessage(value) {
  if (!options.TransmitData) return console.log('TransmitData disabled');
  socket.send(JSON.stringify({ type: 'MoveJointToRight', value }));
}

// NEW: send checkpoint state 1/0 immediately when toggled
function sendCheckpointState() {
  if (!options.TransmitData) return;
  const payload = { type: 'Checkpoint', value: options.Checkpoint ? 1 : 0 };
  try {
    socket.send(JSON.stringify(payload));
    console.log('Sent Checkpoint:', payload.value);
  } catch (e) {
    console.warn('Failed to send Checkpoint:', e);
  }
}

// NEW: quantize + deadband Link1, then send as telemetry
function sendLink1Telemetry() {
  const rawDeg = Number.isFinite(options.Link1) ? options.Link1 : 0;

  // quantize + deadband (optional, keep if you liked the anti-jitter)
  const quantized = Math.round(rawDeg / LINK1_QUANT_STEP) * LINK1_QUANT_STEP;
  if (lastSentLink1 !== null && Math.abs(quantized - lastSentLink1) < LINK1_DEADBAND_DEG) return;

  const payload = { type: 'Link1Pos', role: 'telemetry', value: quantized };
  try {
    socket.send(JSON.stringify(payload));
    lastSentLink1 = quantized;
  } catch (e) {
    console.warn('Failed to send Link1Pos:', e);
  }
}

// NEW: single place to (re)start/stop the periodic sender
function restartCheckpointTimer() {
  if (checkpointTimerId) {
    clearInterval(checkpointTimerId);
    checkpointTimerId = null;
  }
  if (!options.TransmitData) return;

  const hz = Math.max(1, Math.min(100, Math.round(options.CheckpointHz))); // clamp 1..100 Hz
  const periodMs = Math.max(5, Math.round(1000 / hz));

  checkpointTimerId = setInterval(() => {
    // keep pipe alive regardless of checkpoint state (you had a "filler" before)
    try { socket.send(JSON.stringify({ type: 'Filler' })); } catch {}

    // When checkpoint is ON, stream Link1 as telemetry
    if (options.Checkpoint) sendLink1Telemetry();
  }, periodMs);
}

// ---- Stats / renderer / scene ----
const stats = new Stats();
document.body.appendChild(stats.dom);

const scene  = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

const render = new THREE.WebGLRenderer();
render.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(render.domElement);

// Camera + helpers
camera.position.set(0.7, 1, 0.8);
scene.add(new THREE.GridHelper(5, 50));

const light = new THREE.DirectionalLight(0xffffff, 1.3);
light.position.set(15, 10, 2);
scene.add(light);

const orbit = new OrbitControls(camera, render.domElement);
orbit.update();
render.setClearColor(0xbfe3dd);

// ---- UI helpers ----
function createButton(name, onMouseDown, onMouseUp) {
  const button = document.createElement('button');
  button.innerHTML = name;
  button.style.position = 'relative';
  button.style.right = '-13px';
  button.style.top = '-4px';
  button.style.width = '93%';
  button.style.marginTop = '4px';
  button.addEventListener('mousedown', onMouseDown);
  button.addEventListener('mouseup', onMouseUp);
  button.addEventListener('touchstart', (e) => { e.preventDefault(); onMouseDown(e); });
  button.addEventListener('touchend',   (e) => { e.preventDefault(); onMouseUp(e);   });
  return button;
}

// ---- GUI ----
function createPanel() {
  const gui = new GUI();
  const branch_Kinematics  = gui.addFolder('Robot Forward Kinematics');
  const branch_Duplex_Com  = gui.addFolder('Python Duplex Communication');
  const duplex_folder      = branch_Duplex_Com.addFolder('J1');

  const link1Ctrl = branch_Kinematics.add(options, 'Link1', -180, 180).listen();
    link1Ctrl.onChange(() => {
        if (options.TransmitData && options.Checkpoint) {
            lastSentLink1 = null;   // reset deadband so every slider move goes out
            sendLink1Telemetry();   // send to WebSocket immediately
        }
    });
  branch_Kinematics.add(options, 'Link2', -180, 180).listen();
  branch_Kinematics.add(options, 'Link3', -180, 180).listen();
  branch_Kinematics.add(options, 'Link4', -180, 180).listen();
  branch_Kinematics.add(options, 'Link5', -180, 180).listen();
  branch_Kinematics.add(options, 'Link6', -180, 180).listen();
  branch_Kinematics.open();

  // NEW: Checkpoint toggle + Hz control
  branch_Duplex_Com.add(options, 'Checkpoint').name('Checkpoint (send Link1)')
    .onChange(() => {
      sendCheckpointState();   // send 1/0 immediately on toggle
      lastSentLink1 = null;    // reset deadband memory
      restartCheckpointTimer();
    });

  branch_Duplex_Com.add(options, 'CheckpointHz', 1, 100, 1).name('Checkpoint Hz')
    .onChange(() => {
      restartCheckpointTimer();
    });

  // TransmitData now controls the periodic sender
  branch_Duplex_Com.add(options, 'TransmitData').name('Send Data to Python')
    .onChange(() => {
      // when enabling, also report current checkpoint state once
      if (options.TransmitData) sendCheckpointState();
      restartCheckpointTimer();
    });

  duplex_folder.add(options, 'sendMoveToAngleRequest').name('Home');
  duplex_folder.add(options, 'sendHomeRequest').name('Calibrate');

  // Custom buttons row
  const customContainer = document.createElement('div');
  customContainer.style.display = 'flex';
  customContainer.style.justifyContent = 'space-between';
  customContainer.style.gap = '3px';
  customContainer.style.width = 'calc(100% - 17px)';
  customContainer.style.marginLeft = '0px';
  customContainer.style.marginTop  = '3px';

  const moveLeftBtn  = createButton('Move Joint to Left',
    () => sendMoveJointToLeftMessage(1),
    () => sendMoveJointToLeftMessage(0)
  );
  const moveRightBtn = createButton('Move Joint to Right',
    () => sendMoveJointToRightMessage(1),
    () => sendMoveJointToRightMessage(0)
  );

  moveLeftBtn.style.flex  = '1';
  moveRightBtn.style.flex = '1';
  moveLeftBtn.style.boxSizing  = 'border-box';
  moveRightBtn.style.boxSizing = 'border-box';
  moveLeftBtn.style.width  = 'auto';
  moveRightBtn.style.width = 'auto';

  customContainer.appendChild(moveLeftBtn);
  customContainer.appendChild(moveRightBtn);
  duplex_folder.domElement.appendChild(customContainer);

  const folder2Title = duplex_folder.domElement.querySelector('.title');
  if (folder2Title) {
    folder2Title.addEventListener('click', () => {
      customContainer.style.display = (customContainer.style.display === 'none' ? 'flex' : 'none');
    });
  }
}

const loader = new GLTFLoader();
createPanel();

// ---- Load GLTF parts ----
loader.load('assets/6DOF_gltf_files/base_link.gltf', (gltf) => {
  const base = gltf.scene;
  base.rotateOnAxis(xAxis, -Math.PI / 2);
  scene.add(base);
  shoulder.translateZ(0.004);
  base.add(shoulder);
}, undefined, (error) => console.error(error));

loader.load('assets/6DOF_gltf_files/link_1.gltf', (gltf) => {
  const link1 = gltf.scene;
  link1.rotateOnAxis(xAxis, Math.PI);
  shoulder.add(link1);
  link1.add(joint2);
}, undefined, (error) => console.error(error));

loader.load('assets/6DOF_gltf_files/link_2.gltf', (gltf) => {
  const link2 = gltf.scene;
  scene.add(link2);
  joint2.translateZ(-0.165);
  joint2.translateY(0.065);
  joint2.rotateOnAxis(zAxis, Math.PI / 2);
  link2.rotateOnAxis(yAxis, Math.PI / 2);
  link2.rotateOnAxis(xAxis, Math.PI);
  joint2.rotateOnAxis(xAxis, Math.PI / 2);
  link2.rotateOnAxis(zAxis, Math.PI / 3);
  joint2.add(link2);
  link2.add(joint3);
}, undefined, (error) => console.error(error));

loader.load('assets/6DOF_gltf_files/link_3.gltf', (gltf) => {
  const link3 = gltf.scene;
  scene.add(link3);
  joint3.translateZ(0);
  joint3.rotateOnAxis(zAxis, Math.PI / 2);
  joint3.rotateOnAxis(zAxis, Math.PI / 6);
  joint3.translateX(-0.305);
  link3.rotateOnAxis(zAxis, 5 * Math.PI / 3);
  joint3.add(link3);
  link3.add(joint4);
}, undefined, (error) => console.error(error));

loader.load('assets/6DOF_gltf_files/link_4.gltf', (gltf) => {
  const link4 = gltf.scene;
  scene.add(link4);
  link4.rotateOnAxis(yAxis, 3 * Math.PI / 2);
  link4.rotateOnAxis(zAxis, 15.2 * Math.PI / 8);
  joint4.add(link4);
  link4.add(joint5);
}, undefined, (error) => console.error(error));

loader.load('assets/6DOF_gltf_files/link_5.gltf', (gltf) => {
  const link5 = gltf.scene;
  scene.add(link5);
  joint5.translateZ(-0.222);
  const link5AxesHelper  = new THREE.AxesHelper(0.2);
  const link5AxesHelper1 = new THREE.AxesHelper(0.2);
  joint5.add(link5AxesHelper);
  link5.add(link5AxesHelper1);
  joint5.add(link5);
}, undefined, (error) => console.error(error));

// ---- WebSocket events ----
socket.addEventListener('open', () => {
  console.log('Connected to WebSocket server');
});
socket.addEventListener('error', (error) => {
  console.error('Error connecting to WebSocket server:', error);
});
socket.addEventListener('message', (event) => {
  try {
    const values = JSON.parse(event.data);

    // Expecting feedback like {J1:.., J2:..}
    if (typeof values.J1 === 'number') J1 = values.J1;
    if (typeof values.J2 === 'number') J2 = values.J2;
    if (typeof values.J3 === 'number') J3 = values.J3;
    if (typeof values.J4 === 'number') J4 = values.J4;

    // Optional: if server signals homing active, pause checkpoint streaming
    if (values.HomingActive === true && options.Checkpoint) {
      options.Checkpoint = false;
      sendCheckpointState();
      lastSentLink1 = null;
      restartCheckpointTimer();
      console.log('Homing active → Checkpoint telemetry paused');
    }

    // console.log('J1:', J1);
  } catch (error) {
    console.error('Error processing message:', error);
  }
});

// ---- Render loop ----
function animate() {
  stats.update();

  // Drive model with feedback (J1..J4 in degrees)
  shoulder.setRotationFromAxisAngle(zAxis, J1 * Math.PI / 180);
  joint2.setRotationFromAxisAngle(xAxis,  J2 * Math.PI / 180);
  joint3.setRotationFromAxisAngle(zAxis,  J3 * Math.PI / 180);
  joint4.setRotationFromAxisAngle(xAxis,  J4 * Math.PI / 180);

  render.render(scene, camera);
}

if (WebGL.isWebGLAvailable()) {
  render.setAnimationLoop(animate);
  console.info('This is an informational message');
} else {
  const warning = WebGL.getWebGLErrorMessage();
  document.getElementById('container').appendChild(warning);
}

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  render.setSize(window.innerWidth, window.innerHeight);
});
