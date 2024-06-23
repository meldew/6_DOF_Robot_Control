# Not in use for now.

values = {
    'J1': J1,
    'J2': J2,
    'J3': J3,
    'J4': J4,
    'J5': J5,
    'J6': J6
}
values_json = json.dumps(values) 
await websocket.send(values_json) 

if J1 >= 140:
    J1direction = -1  
elif J1 <= -140:
    J1direction = 1  

if J2 >= 100:
    J2direction = -1  
elif J2 <= -90:
    J2direction = 1  

if J3 >= 140:
    J3direction = -1  
elif J3 <= -140:
    J3direction = 1  

if J4 >= 180:
    J4direction = -1  
elif J4 <= -180:
    J4direction = 1 

J1 += J1direction  
J2 += J2direction
J3 += J3direction * 3
J4 += J4direction * 3 




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
