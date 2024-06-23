console.log('main.js loaded');
import * as THREE from 'three';
import WebGL from 'three/addons/capabilities/WebGL.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { xAxis, zAxis } from './xAxis';
import { createPanel } from './createPanel';
import { stats, render, scene, camera } from './stats';

const socket = new WebSocket('ws://127.0.0.1:8765');
export const shoulder = new THREE.Object3D();
export const joint2 = new THREE.Object3D();
export const joint3 = new THREE.Object3D();
export const joint4 = new THREE.Object3D();
export const joint5 = new THREE.Object3D();
const buttonDelaytime = 200; 

export let sendDataIntervalId = null;

let J1 = 0;
let J2 = 0;
let J3 = 0;
let J4 = 0;
let J5 = 0;
let J6 = 0;

export var options = {
    'Link1': 0,
    'Link2': 0,
    'Link3': 0,
    'Link4': 0,
    'Link5': 0,
    'Link6': 0,
    TransmitData: false,
    sendMoveToAngleRequest: function() {
        if (options.TransmitData) {
            const moveToAngleMessageOn = { type: 'MoveToAngle', value: 1 };
            const moveToAngleMessageOff = { type: 'MoveToAngle', value: 0 };
            socket.send(JSON.stringify(moveToAngleMessageOn));
            setTimeout(() => {
                socket.send(JSON.stringify(moveToAngleMessageOff));
            }, buttonDelaytime);
        } else {
            console.log("TransmitData is disabled, not sending move to angle request");
        }
    },
    sendHomeRequest: function() {
        if (options.TransmitData) {
            const HomeMessageOn = { type: 'Home', value: 1 };
            const HomeMessageOff = { type: 'Home', value: 0 };
            socket.send(JSON.stringify(HomeMessageOn));
            setTimeout(() => {
                socket.send(JSON.stringify(HomeMessageOff));
            }, buttonDelaytime);
        } else {
            console.log("TransmitData is disabled, not sending move to angle request");
        }
    }
};

export function sendMoveJointToLeftMessage(value) {
    if (options.TransmitData) {
        const moveJointToLeftMessage = { type: 'MoveJointToLeft', value: value };
        socket.send(JSON.stringify(moveJointToLeftMessage));
    } else {
        console.log("TransmitData is disabled, not sending move joint to left request");
    }
}

export function sendMoveJointToRightMessage(value) {
    if (options.TransmitData) {
        const moveJointToRightMessage = { type: 'MoveJointToRight', value: value };
        socket.send(JSON.stringify(moveJointToRightMessage));
    } else {
        console.log("TransmitData is disabled, not sending move joint to left request");
    }
}

createPanel();
socket.addEventListener('open', event => {
    console.log('Connected to WebSocket server');
    
});

socket.addEventListener('error', error => {
    console.error('Error connecting to WebSocket server:', error);
});

socket.addEventListener('message', event => {
    try {
        const values = JSON.parse(event.data);
        
        // Access the values
        J1 = values.J1;
        J2 = values.J2;
        J3 = values.J3;
        J4 = values.J4;
        console.log('J1: ', J1);
        console.log('J2: ', J2);
        //console.log('J3: ', J3);
        //console.log('J4: ', J4);
    } catch (error) {
        console.error('Error processing message:', error);
    }
});

export function Angles2Links(branch_Kinematics) {
    branch_Kinematics.add(options, 'Link1', -180, 180).listen();
    branch_Kinematics.add(options, 'Link2', -180, 180).listen();
    branch_Kinematics.add(options, 'Link3', -180, 180).listen();
    branch_Kinematics.add(options, 'Link4', -180, 180).listen();
    branch_Kinematics.add(options, 'Link5', -180, 180).listen();
    branch_Kinematics.add(options, 'Link6', -180, 180).listen();
    branch_Kinematics.open();
}

function animate() {  
    stats.update();

    shoulder.setRotationFromAxisAngle(zAxis, options.Link1 * Math.PI/180);
    joint2.setRotationFromAxisAngle(xAxis, options.Link2 * Math.PI/180);
    joint3.setRotationFromAxisAngle(zAxis, options.Link3 * Math.PI/180);
    joint4.setRotationFromAxisAngle(xAxis, options.Link4 * Math.PI/180);
    joint5.setRotationFromAxisAngle(xAxis, options.Link5 * Math.PI/180);
    
    /*
    shoulder.setRotationFromAxisAngle(zAxis, J1 * Math.PI/180);
    joint2.setRotationFromAxisAngle(xAxis, J2 * Math.PI/180);
    joint3.setRotationFromAxisAngle(zAxis, J3 * Math.PI/180);
    joint4.setRotationFromAxisAngle(xAxis, J4 * Math.PI/180);
    */
	render.render( scene, camera );
}   

if ( WebGL.isWebGLAvailable() ) {
    render.setAnimationLoop( animate );
    console.info('This is an informational message');
} else {
    const warning = WebGL.getWebGLErrorMessage();
	document.getElementById( 'container' ).appendChild( warning );
}

window.addEventListener( 'resize', function () {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	render.setSize( window.innerWidth, window.innerHeight );
});