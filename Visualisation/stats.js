import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import Stats from 'three/addons/libs/stats.module.js';

// Stats
export const stats = new Stats();
document.body.appendChild(stats.dom);
// Scene and camera

export const scene = new THREE.Scene();
export const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
// Render
export const render = new THREE.WebGLRenderer();
render.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(render.domElement);
//Camera position and axis helper
camera.position.set(0.7, 1, 0.8);
const grid = new THREE.GridHelper(5, 50);
scene.add(grid);
// Light
const directionalLight = new THREE.DirectionalLight(16777215, 1.3);
directionalLight.position.set(15, 10, 2);
scene.add(directionalLight);
// Orbit controls and background color
const orbit = new OrbitControls(camera, render.domElement);
orbit.update();
render.setClearColor(12575709);
