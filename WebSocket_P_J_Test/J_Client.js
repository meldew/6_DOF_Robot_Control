
const WebSocket = require('ws');

const exampleSocket = new WebSocket('ws://127.0.0.1:8765');

exampleSocket.on('open', () => {
    console.log('WebSocket connection opened');

    // Send initial data from JavaScript to Python
    const initialData = { message: 'Initial data from JavaScript' };
    exampleSocket.send(JSON.stringify(initialData));
});

exampleSocket.on('message', (data) => {
    console.log(`WebSocket message received: ${data}`);

    // Process incoming messages from the server

    // Send feedback from angle sensors back to Python
    const sensorData = { angle1: 45, angle2: 30 };
    exampleSocket.send(JSON.stringify(sensorData));
});

exampleSocket.on('close', () => {
    console.log('WebSocket connection closed');
});

exampleSocket.on('error', (error) => {
    console.error('WebSocket error:', error);
});
