console.log('main.js loaded');
import * as THREE from 'three';
import WebGL from 'three/addons/capabilities/WebGL.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
import Stats from 'three/addons/libs/stats.module.js';

const socket = new WebSocket('ws://127.0.0.1:8765');
const shoulder = new THREE.Object3D();
const joint2 = new THREE.Object3D();
const joint3 = new THREE.Object3D();
const joint4 = new THREE.Object3D();
const joint5 = new THREE.Object3D();

var zAxis = new THREE.Vector3(0, 0, 1);
var yAxis = new THREE.Vector3(0, 1, 0);
var xAxis = new THREE.Vector3(1, 0, 0);

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
    sendHomingRequest: function() {
        const homingMessageOn = { type: 'homing', value: 1 };
        const homingMessageOff = { type: 'homing', value: 0 };
        socket.send(JSON.stringify(homingMessageOn));
        setTimeout(() => {
            socket.send(JSON.stringify(homingMessageOff));
        }, 100); // Adjust the delay as needed
    }
};
// Stats
const stats = new Stats();
document.body.appendChild( stats.dom );

// Scene and camera
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );

// Render
const render = new THREE.WebGLRenderer();
render.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( render.domElement );

//Camera position and axis helper
camera.position.set( 0.7, 1, 0.8 );

const grid = new THREE.GridHelper( 5, 50 );
scene.add( grid );

// Light
const directionalLight = new THREE.DirectionalLight( 0xffffff, 1.3 );
directionalLight.position.set( 15, 10, 2 );
scene.add( directionalLight );

// Orbit controls and background color
const orbit = new OrbitControls( camera, render.domElement )
orbit.update();
render.setClearColor(0xbfe3dd); 

// DAT.GUI Related Stuff
function createPanel() {
    const gui = new GUI();
    const folder1 = gui.addFolder( 'Robot Forward Kinematics' );
    const folder2 = gui.addFolder( 'Python Duplex Communication' );

    folder1.add(options, 'Link1', -180, 180).listen();
    folder1.add(options, 'Link2', -180, 180).listen();
    folder1.add(options, 'Link3', -180, 180).listen();
    folder1.add(options, 'Link4', -180, 180).listen();
    folder1.add(options, 'Link5', -180, 180).listen();
    folder1.add(options, 'Link6', -180, 180).listen();
    folder1.open();
    
    folder2.add(options, 'TransmitData').name('Send Data to Python').onChange(function(value) {
        if (sendDataIntervalId !== null) {
            clearInterval(sendDataIntervalId);
            sendDataIntervalId = null;
        }
        if (value) {
            sendDataIntervalId = setInterval(() => {
                const feedbackValue = options.Link1;
                socket.send(JSON.stringify(feedbackValue));
            }, 100);
        } else {
            if (sendDataIntervalId !== null) {
                clearInterval(sendDataIntervalId);
                sendDataIntervalId = null;
            }
        }
    });
    folder2.add(options, 'sendHomingRequest').name('Home');
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
        //console.log('J1: ', J1);
        //console.log('J2: ', J2);
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