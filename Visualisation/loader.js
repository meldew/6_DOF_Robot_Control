import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { xAxis, zAxis, yAxis } from './xAxis';
import { scene, shoulder, joint2, joint3, joint4, joint5 } from './main';

const loader = new GLTFLoader();
loader.load('assets/6DOF_gltf_files/base_link.gltf', function (gltf) {
    const base = gltf.scene;
    base.rotateOnAxis(xAxis, -Math.PI / 2);
    scene.add(base);
    shoulder.translateZ(0.004);
    base.add(shoulder);
}, undefined, function (error) { console.error(error); });

loader.load('assets/6DOF_gltf_files/link_1.gltf', function (gltf) {
    const link1 = gltf.scene;
    link1.rotateOnAxis(xAxis, Math.PI);
    shoulder.add(link1);
    link1.add(joint2);
}, undefined, function (error) { console.error(error); });

loader.load('assets/6DOF_gltf_files/link_2.gltf', function (gltf) {
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
}, undefined, function (error) { console.error(error); });

loader.load('assets/6DOF_gltf_files/link_3.gltf', function (gltf) {
    const link3 = gltf.scene;
    scene.add(link3);
    joint3.translateZ(0);
    joint3.rotateOnAxis(zAxis, Math.PI / 2);
    joint3.rotateOnAxis(zAxis, Math.PI / 6);
    joint3.translateX(-0.305);
    link3.rotateOnAxis(zAxis, 5 * Math.PI / 3);
    joint3.add(link3);
    link3.add(joint4);
}, undefined, function (error) { console.error(error); });

loader.load('assets/6DOF_gltf_files/link_4.gltf', function (gltf) {
    const link4 = gltf.scene;
    scene.add(link4);
    link4.rotateOnAxis(yAxis, 3 * Math.PI / 2);
    link4.rotateOnAxis(zAxis, 15.2 * Math.PI / 8);
    joint4.add(link4);
    link4.add(joint5);
}, undefined, function (error) { console.error(error); });

loader.load('assets/6DOF_gltf_files/link_5.gltf', function (gltf) {
    const link5 = gltf.scene;
    scene.add(link5);

    joint5.translateZ(-0.222);

    const link5AxesHelper = new THREE.AxesHelper(0.2);
    joint5.add(link5AxesHelper);
    const link5AxesHelper1 = new THREE.AxesHelper(0.2);
    link5.add(link5AxesHelper1);
    joint5.add(link5);
}, undefined, function (error) { console.error(error); });
