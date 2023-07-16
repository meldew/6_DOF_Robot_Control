import numpy as np
from forward_kinematics import DH_matrix
from Common import Common_Matrices as CM
from Common import common_DH_parameters as DH_parameters

# Here i am using the Kinematic decoupling where i am separating the first 3 joints from the last 3 joints


def Overall_tool_translation_matrix(x, y, z, yaw, pitch, roll):
    alpha = np.deg2rad(yaw)
    beta = np.deg2rad(pitch)
    gamma = np.deg2rad(roll)

    T_0_T = np.array([[(np.cos(alpha)*np.cos(gamma))-(np.cos(beta)*np.sin(alpha)*np.sin(gamma)), (np.cos(gamma)*np.sin(alpha))+(np.cos(alpha)*np.cos(beta)*np.sin(gamma)), np.sin(beta)*np.sin(gamma), x],
                      [(np.cos(beta)*np.cos(gamma)*np.sin(alpha))+(np.cos(alpha)*np.sin(gamma)), (np.cos(alpha)*np.cos(beta)*np.cos(gamma))-(np.sin(alpha)*np.sin(gamma)), np.cos(gamma)*np.sin(beta), y],
                      [np.sin(alpha)*np.sin(beta), np.cos(alpha)*np.sin(beta), -np.cos(beta), z],
                      [0, 0, 0, 1]]) 
     
    return T_0_T
                       
# Function to calculate inverse kinematics
def calculate_inverse_kinematics(x, y, z, yaw, pitch, roll, Feedback_Joint_angle1, Feedback_Joint_angle2, Feedback_Joint_angle3):

    # Calculate the Rotation matrix from the base frame to the J3 frame and then take an inverse of it.
    DH = DH_parameters()
    Theta1 = np.deg2rad(Feedback_Joint_angle1)
    Theta2 = np.deg2rad(Feedback_Joint_angle2)
    Theta3 = np.deg2rad(Feedback_Joint_angle3)

    J1 = DH_matrix(Theta1, DH.d1, DH.a1, DH.alpha1)   
    J2 = DH_matrix(Theta2, DH.d2, DH.a2, DH.alpha2)
    J3 = DH_matrix(Theta3, DH.d3, DH.a3, DH.alpha3)

    T1 = np.dot(J1, CM.work_frame)
    T2 = np.dot(T1, J2)
    T3 = np.dot(T2, J3)

    R_0_3_rotation_matrix = np.array([[T3[0,0], T3[0,1], T3[0,2]],
                                      [T3[1,0], T3[1,1], T3[1,2]],
                                      [T3[2,0], T3[2,1], T3[2,2]]])
    
    R_0_3_Transposed = np.transpose(R_0_3_rotation_matrix)
    T_0_T_offset = np.dot(Overall_tool_translation_matrix(x, y, z, yaw, pitch, roll), CM.work_frame)
    T_0_T_offset[0,0] = T_0_T_offset[0,0]*-1
    Tool_frame_inverted = np.transpose(CM.tool_frame)
    T_0_6_T = np.dot(T_0_T_offset, Tool_frame_inverted)

    Remove_T_0_6_T = np.array([[np.cos(np.deg2rad(180)), np.sin(np.deg2rad(180)), 0, 0],
                               [-np.sin(np.deg2rad(180))*np.cos(DH.alpha6), np.cos(np.deg2rad(180))*np.cos(DH.alpha6), np.sin(DH.alpha6), 0],
                               [np.sin(np.deg2rad(180))*np.cos(DH.alpha6), -np.cos(np.deg2rad(180))*np.sin(DH.alpha6), np.cos(DH.alpha6), -DH.d6],
                               [0, 0, 0, 1]])
    
    center_spherical_wrist = np.dot(T_0_6_T, Remove_T_0_6_T)

    central_wrist_Rot = np.array([[center_spherical_wrist[0,0], center_spherical_wrist[0,1], center_spherical_wrist[0,2]],
                                    [center_spherical_wrist[1,0], center_spherical_wrist[1,1], center_spherical_wrist[1,2]],
                                    [center_spherical_wrist[2,0], center_spherical_wrist[2,1], center_spherical_wrist[2,2]]])

    R_3_6_O_orientation_matrix = R_0_3_Transposed.dot(central_wrist_Rot)