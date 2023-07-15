import numpy as np
from DH_parameter import common_DH_parameters as DH_parameters

def calculate_forward_kinematics(Joint_angle1, Joint_angle2, Joint_angle3, Joint_angle4, Joint_angle5, Joint_angle6):
    DH = DH_parameters()
    Theta1 = np.deg2rad(Joint_angle1)
    Theta2 = np.deg2rad(Joint_angle2)
    Theta3 = np.deg2rad(Joint_angle3)
    Theta4 = np.deg2rad(Joint_angle4)
    Theta5 = np.deg2rad(Joint_angle5)
    Theta6 = np.deg2rad(Joint_angle6)

    # calculating J1 to J6 _Frame transformation matrices

    work_frame = np.array([[1, 0, 0, 0],
                          [0, 1, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]]) 
    
    tool_frame = np.array([[1, 0, 0, 0],
                          [0, 1, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]])
    
   
    J1 = np.array([[np.cos(Theta1),  -np.sin(Theta1)*np.cos(DH.alpha1), np.sin(Theta1)*np.sin(DH.alpha1), DH.a1*np.cos(Theta1)], 
                    [np.sin(Theta1), np.cos(Theta1)*np.cos(DH.alpha1), -np.cos(Theta1)*np.sin(DH.alpha1), DH.a1*np.sin(Theta1)],
                    [0, np.sin(DH.alpha1), np.cos(DH.alpha1), DH.d1],
                    [0, 0, 0, 1]])
    
    J2 = np.array([[np.cos(Theta2),  -np.sin(Theta2)*np.cos(DH.alpha2), np.sin(Theta2)*np.sin(DH.alpha2), DH.a2*np.cos(Theta2)],
                    [np.sin(Theta2), np.cos(Theta2)*np.cos(DH.alpha2), -np.cos(Theta2)*np.sin(DH.alpha2), DH.a2*np.sin(Theta2)],
                    [0, np.sin(DH.alpha2), np.cos(DH.alpha2), DH.d2],
                    [0, 0, 0, 1]])
    
    J3 = np.array([[np.cos(Theta3),  -np.sin(Theta3)*np.cos(DH.alpha3), np.sin(Theta3)*np.sin(DH.alpha3), DH.a3*np.cos(Theta3)],
                    [np.sin(Theta3), np.cos(Theta3)*np.cos(DH.alpha3), -np.cos(Theta3)*np.sin(DH.alpha3), DH.a3*np.sin(Theta3)],
                    [0, np.sin(DH.alpha3), np.cos(DH.alpha3), DH.d3],
                    [0, 0, 0, 1]])

    J4 = np.array([[np.cos(Theta4),  -np.sin(Theta4)*np.cos(DH.alpha4), np.sin(Theta4)*np.sin(DH.alpha4), DH.a4*np.cos(Theta4)],
                    [np.sin(Theta4), np.cos(Theta4)*np.cos(DH.alpha4), -np.cos(Theta4)*np.sin(DH.alpha4), DH.a4*np.sin(Theta4)],
                    [0, np.sin(DH.alpha4), np.cos(DH.alpha4), DH.d4],
                    [0, 0, 0, 1]])

    J5 = np.array([[np.cos(Theta5),  -np.sin(Theta5)*np.cos(DH.alpha5), np.sin(Theta5)*np.sin(DH.alpha5), DH.a5*np.cos(Theta5)],
                    [np.sin(Theta5), np.cos(Theta5)*np.cos(DH.alpha5), -np.cos(Theta5)*np.sin(DH.alpha5), DH.a5*np.sin(Theta5)],
                    [0, np.sin(DH.alpha5), np.cos(DH.alpha5), DH.d5],
                    [0, 0, 0, 1]])

    J6 = np.array([[np.cos(Theta6),  -np.sin(Theta6)*np.cos(DH.alpha6), np.sin(Theta6)*np.sin(DH.alpha6), DH.a6*np.cos(Theta6)],
                    [np.sin(Theta6), np.cos(Theta6)*np.cos(DH.alpha6), -np.cos(Theta6)*np.sin(DH.alpha6), DH.a6*np.sin(Theta6)],
                    [0, np.sin(DH.alpha6), np.cos(DH.alpha6), DH.d6],
                    [0, 0, 0, 1]])
    
    # calculating T1 to T6 _Frame transformation matrices
    T1 = np.dot(J1, work_frame)
    T2 = np.dot(T1, J2)
    T3 = np.dot(T2, J3)
    T4 = np.dot(T3, J4)
    T5 = np.dot(T4, J5)
    T6 = np.dot(T5, J6)
    T_frame = np.dot(T6, tool_frame)

    x_position = T6[0,3]
    y_position = T6[1,3]
    z_position = T6[2,3]

    pitch = np.arctan2(-T_frame[2, 2], np.sqrt(T_frame[0, 2] ** 2 + T_frame[1, 2] ** 2))
    yaw = np.arctan2(T_frame[2, 1] / np.cos(pitch), T_frame[2, 0] / np.cos(pitch))
    roll = np.arctan2(T_frame[1, 2] / np.cos(pitch), T_frame[0, 2] / np.cos(pitch))

    return x_position, y_position, z_position, roll, pitch, yaw