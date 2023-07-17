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
def calculate_inverse_kinematics(x, y, z, yaw, pitch, roll, Feedback_Joint_angle1, Feedback_Joint_angle2, Feedback_Joint_angle3, Feedback_Joint_angle5):

    # Calculate the Rotation matrix from the base frame to the J3 frame and then take an inverse of it.
    DH = DH_parameters()
    Theta1 = np.deg2rad(Feedback_Joint_angle1)
    Theta2 = np.deg2rad(Feedback_Joint_angle2)
    Theta3 = np.deg2rad(Feedback_Joint_angle3 - 90 )

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

    # Now we find the rotation matrix from the J3 frame to the J6 frame
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
    
    # Now we mathematically connect previously decoupled 0 to 3 rotation matrix to the 3 to 6 rotation matrix
    R_3_6_orientation_matrix = np.dot(R_0_3_Transposed,central_wrist_Rot)

    # Fet J4 to J6 angles from the connected rotation matrix
    J5_pos = np.rad2deg(np.arctan2(np.sqrt(1- np.power(R_3_6_orientation_matrix[2, 2],2)), R_3_6_orientation_matrix[2, 2]))
    J5_neg = np.rad2deg(np.arctan2(-np.sqrt(1- np.power(R_3_6_orientation_matrix[2, 2],2)), R_3_6_orientation_matrix[2, 2]))

    if J5_pos > 0 and Feedback_Joint_angle5 > 0: J5 = J5_pos
    else: J5 = J5_neg

    if R_3_6_orientation_matrix[2, 1] < 0: J6_pos = np.rad2deg(np.arctan2(-R_3_6_orientation_matrix[2, 1], R_3_6_orientation_matrix[2, 0])) - 180
    else: J6_pos = np.rad2deg(np.arctan2(-R_3_6_orientation_matrix[2, 1], R_3_6_orientation_matrix[2, 0])) + 180

    if R_3_6_orientation_matrix[2, 1] < 0: J6_neg = np.rad2deg(np.arctan2(R_3_6_orientation_matrix[2, 1], -R_3_6_orientation_matrix[2, 0])) + 180
    else: J6_neg = np.rad2deg(np.arctan2(R_3_6_orientation_matrix[2, 1], -R_3_6_orientation_matrix[2, 0])) - 180

    if J5 < 0: J6 = J6_neg
    else: J6 = J6_pos

    J4_pos = np.rad2deg(np.arctan2(R_3_6_orientation_matrix[1, 2], R_3_6_orientation_matrix[0, 2]))
    J4_neg = np.rad2deg(np.arctan2(-R_3_6_orientation_matrix[1, 2], -R_3_6_orientation_matrix[0, 2]))

    if J5 > 0: J4 = J4_pos
    else: J4 = J4_neg

    if x > 0 and y > 0: quadrant = 1
    elif x > 0 and y < 0: quadrant = 2 
    elif x < 0 and y < 0: quadrant = 3
    elif x < 0 and y > 0: quadrant = 4

    # Use geometry to find J1, J2, J3 angles
    J1_rad = np.arctan(center_spherical_wrist[1, 3]/center_spherical_wrist[0, 3])
    if quadrant == 1: J1 = np.rad2deg(J1_rad)
    elif quadrant == 2: J1 = np.rad2deg(J1_rad)
    elif quadrant == 3: J1 = np.rad2deg(J1_rad) + (-180)
    elif quadrant == 4: J1 = np.rad2deg(J1_rad) + 180

    pX = np.sqrt(np.power(np.abs(center_spherical_wrist[0, 3]),2)+np.power(np.abs(center_spherical_wrist[1, 3]),2))
    pY = center_spherical_wrist[2, 3] - DH.d1
    pX_a1_FWD = pX - DH.a1
    pX_a1_MID = -pX_a1_FWD
    pa2H_FWD = np.sqrt(np.power(pY,2) + np.power(pX_a1_FWD,2))
    pa2H_MID = np.sqrt(np.power(pY,2) + np.power(pX_a1_MID,2))
    pa3H = np.sqrt(np.power(DH.d4,2) + np.power(DH.a3,2))

    thetaA_FWD = np.rad2deg(np.arctan(pY/pX_a1_FWD))
    thetaA_MID = np.rad2deg(np.arccos((np.power(DH.a2,2)+np.power(pa2H_MID,2)-np.power(np.abs(DH.d4),2))/(2*DH.a2*pa2H_MID)))

    thetaB_FWD = np.rad2deg(np.arccos((np.power(DH.a2,2) + np.power(pa2H_FWD,2) - (np.power(np.abs(pa3H),2))) / (2*DH.a2*pa2H_FWD)))
    thetaB_MID = np.rad2deg(np.arctan(pX_a1_MID/pY))

    thetaD = 90 - (thetaA_MID + thetaB_MID)
    try:
        thetaE = np.rad2deg(np.arctan(np.abs(DH.d4)/DH.a3))
    except:
        thetaE = 90

    thetaC_FWD = 180 - np.rad2deg(np.arccos((np.power(np.abs(pa3H),2)+np.power(DH.a2,2)-np.power(pa2H_FWD,2))/(2*np.abs(pa3H)*DH.a2))) + (90 - thetaE)
    thetaC_MID = 180 - np.rad2deg(np.arccos((np.power(np.abs(pa3H),2)+np.power(DH.a2,2)-np.power(pa2H_MID,2))/(2*np.abs(pa3H)*DH.a2))) + (90 - thetaE)

    J2_FWD = -(thetaA_FWD + thetaB_FWD)
    J2_MID = -180 + thetaD

    J3_FWD = thetaC_FWD
    J3_MID = thetaC_MID

    if pX_a1_FWD < 0: J2 = J2_MID
    else: J2 = J2_FWD

    if pX_a1_FWD < 0: J3 = J3_MID
    else: J3 = J3_FWD

    print(J4_pos, J4_neg, J5_pos, J5_neg, J6_pos, J6_neg)

    return J1, J2, J3, J4, J5, J6