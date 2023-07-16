import numpy as np
import math as m
from Common import common_DH_parameters as DH_parameters
from Common import Common_Matrices

# Function to calculate DH matrix
# Input: theta, d, a, alpha
# Output: DH matrix
def DH_matrix(theta, d, a, alpha):
    J = np.array([[np.cos(theta),  -np.sin(theta) * np.cos(alpha), np.sin(theta) * np.sin(alpha), a * np.cos(theta)], 
                  [np.sin(theta), np.cos(theta) * np.cos(alpha), -np.cos(theta) * np.sin(alpha), a * np.sin(theta)],
                  [0, np.sin(alpha), np.cos(alpha), d],
                  [0, 0, 0, 1]])  
    return J
    
# Function to calculate forward kinematics
# Input: Joint angles in degrees    
# Output: x, y, z position and roll, pitch, yaw angles in radians
def calculate_forward_kinematics(Joint_angle1, Joint_angle2, Joint_angle3, Joint_angle4, Joint_angle5, Joint_angle6):
    DH = DH_parameters()
    Theta1 = np.deg2rad(Joint_angle1)
    Theta2 = np.deg2rad(Joint_angle2)
    Theta3 = np.deg2rad((Joint_angle3) - 90)
    Theta4 = np.deg2rad(Joint_angle4)
    Theta5 = np.deg2rad(Joint_angle5)
    Theta6 = np.deg2rad((Joint_angle6) + 180)

    # calculating J1 to J6 _Frame transformation matrices
    J1 = DH_matrix(Theta1, DH.d1, DH.a1, DH.alpha1)   
    J2 = DH_matrix(Theta2, DH.d2, DH.a2, DH.alpha2)
    J3 = DH_matrix(Theta3, DH.d3, DH.a3, DH.alpha3)
    J4 = DH_matrix(Theta4, DH.d4, DH.a4, DH.alpha4)
    J5 = DH_matrix(Theta5, DH.d5, DH.a5, DH.alpha5)
    J6 = DH_matrix(Theta6, DH.d6, DH.a6, DH.alpha6)

    # calculating T1 to T6 _Frame transformation matrices
    T1 = np.dot(J1, Common_Matrices.work_frame)
    T2 = np.dot(T1, J2)
    T3 = np.dot(T2, J3)
    T4 = np.dot(T3, J4)
    T5 = np.dot(T4, J5)
    T6 = np.dot(T5, J6)
    T_frame = np.dot(T6, Common_Matrices.tool_frame)

    x_position = T6[0,3]
    y_position = T6[1,3]
    z_position = T6[2,3]
    
    pitch = m.atan2(np.sqrt((m.pow(T_frame[0, 2],2)) + (m.pow(T_frame[1, 2],2))), -T_frame[2, 2])
    yaw = m.atan2(T_frame[2, 0] / pitch, T_frame[2, 1] / pitch)
    roll = m.atan2(T_frame[0, 2] / pitch, T_frame[1, 2] / pitch)
    
    return x_position, y_position, z_position, np.rad2deg(roll), np.rad2deg(pitch), np.rad2deg(yaw)