import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
import { Angles2Links, options, sendDataIntervalId, sendMoveJointToLeftMessage, sendMoveJointToRightMessage } from './main';

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
export function createPanel() {
    const gui = new GUI();
    const branch_Kinematics = gui.addFolder('Robot Forward Kinematics');
    const branch_Duplex_Com = gui.addFolder('Python Duplex Communication');

    Angles2Links(branch_Kinematics);

    branch_Duplex_Com.add(options, 'TransmitData').name('Send Data to Python').onChange(function (value) {
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
