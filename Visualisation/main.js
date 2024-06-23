console.log('main.js loaded');
import * as THREE from 'three';
import WebGL from 'three/addons/capabilities/WebGL.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
import { xAxis, zAxis, yAxis } from './xAxis';
import { scene, stats, render, camera } from './scene';

const socket = new WebSocket('ws://127.0.0.1:8765');
const shoulder = new THREE.Object3D();
const joint2 = new THREE.Object3D();
const joint3 = new THREE.Object3D();
const joint4 = new THREE.Object3D();
const joint5 = new THREE.Object3D();
const buttonDelaytime = 200; 
// tes
let sendDataIntervalId = null;

let J1 = 0;
let J2 = 0;
let J3 = 0;
let J4 = 0;
let J5 = 0;
let J6 = 0;

var options = {
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

function sendMoveJointToLeftMessage(value) {
    if (options.TransmitData) {
        const moveJointToLeftMessage = { type: 'MoveJointToLeft', value: value };
        socket.send(JSON.stringify(moveJointToLeftMessage));
    } else {
        console.log("TransmitData is disabled, not sending move joint to left request");
    }
}

function sendMoveJointToRightMessage(value) {
    if (options.TransmitData) {
        const moveJointToRightMessage = { type: 'MoveJointToRight', value: value };
        socket.send(JSON.stringify(moveJointToRightMessage));
    } else {
        console.log("TransmitData is disabled, not sending move joint to left request");
    }
}
function createButton(name, onMouseDown, onMouseUp) {
    const button = document.createElement('button');
    button.innerHTML = name;
    button.style.position = 'relative';
    button.style.right = '-5px';
    button.style.top = '-4px';
    button.style.width = '96%';
    button.style.marginTop = '4px';
    button.addEventListener('mousedown', onMouseDown);
    button.addEventListener('mouseup', onMouseUp);
    return button;
}

// DAT.GUI Related Stuff
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
}
const loader = new GLTFLoader();
createPanel();

loader.load( 'assets/6DOF_gltf_files/base_link.gltf', function ( gltf ) {
    const base = gltf.scene;
    base.rotateOnAxis(xAxis, -Math.PI/2);
    scene.add(base);
    shoulder.translateZ(0.004);
    base.add( shoulder ); 
},  undefined, function ( error ) {console.error( error );});

loader.load('assets/6DOF_gltf_files/link_1.gltf', function ( gltf ) {
    const link1 = gltf.scene;
    link1.rotateOnAxis(xAxis,  Math.PI);
    shoulder.add( link1 );
    link1.add( joint2 );
},  undefined, function ( error ) {console.error( error );});

loader.load('assets/6DOF_gltf_files/link_2.gltf', function ( gltf ) {
    const link2 = gltf.scene;
    scene.add(link2);
    joint2.translateZ(-0.165);
    joint2.translateY(0.065);
    joint2.rotateOnAxis(zAxis,  Math.PI/2);
    link2.rotateOnAxis(yAxis,  Math.PI/2);
    link2.rotateOnAxis(xAxis,  Math.PI);
    joint2.rotateOnAxis(xAxis,  Math.PI/2);
    link2.rotateOnAxis(zAxis,  Math.PI/3);
    joint2.add( link2 );
    link2.add( joint3 );
},  undefined, function ( error ) {console.error( error );});

loader.load('assets/6DOF_gltf_files/link_3.gltf', function ( gltf ) {
    const link3 = gltf.scene;  
    scene.add(link3);
    joint3.translateZ(0);
    joint3.rotateOnAxis(zAxis,  Math.PI/2);
    joint3.rotateOnAxis(zAxis,  Math.PI/6);
    joint3.translateX(-0.305);
    link3.rotateOnAxis(zAxis,  5*Math.PI/3);
    joint3.add( link3 );
    link3.add( joint4 );
},  undefined, function ( error ) {console.error( error );});

loader.load('assets/6DOF_gltf_files/link_4.gltf', function ( gltf ) {
    const link4 = gltf.scene;
    scene.add(link4);
    link4.rotateOnAxis(yAxis,  3*Math.PI/2);
    link4.rotateOnAxis(zAxis,  15.2*Math.PI/8);
    joint4.add( link4 );
    link4.add( joint5 );
},  undefined, function ( error ) {console.error( error );});

loader.load('assets/6DOF_gltf_files/link_5.gltf', function ( gltf ) {
    const link5 = gltf.scene;
    scene.add( link5 );
    
    joint5.translateZ(-0.222);
    
    const link5AxesHelper = new THREE.AxesHelper(0.2);
    joint5.add(link5AxesHelper);
    const link5AxesHelper1 = new THREE.AxesHelper(0.2);
    link5.add(link5AxesHelper1);
    joint5.add( link5 );
    
     
},  undefined, function ( error ) {console.error( error );});

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