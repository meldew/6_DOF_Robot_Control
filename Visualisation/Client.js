
const WebSocket = require('ws');

const socket = new WebSocket('ws://127.0.0.1:8765');

socket.on('open', () => {
    console.log('WebSocket connection opened');
    const initialData = { message: 'Initial data from JavaScript' };
    socket.send(JSON.stringify(initialData));
});
console.log('WebSocket client created');
socket.on('message', (data) => {
    console.log(`WebSocket message received: ${data}`);
    module.exports = {data};
    const sensorData = { message: 'Not for now data from JavaScript'};
    socket.send(JSON.stringify(sensorData));
    
});
socket.on('close', () => {
    console.log('WebSocket connection closed');
});
socket.on('error', (error) => {
    console.error('WebSocket error:', error);
});

