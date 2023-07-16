import forward_kinematics as FK
import numpy as np
import math as m
Xpos , Ypos, Zpos, roll, pitch, yaw = FK.calculate_forward_kinematics(60,60,60,60,60,60)

#print("..................................")
#print("Xpos = ", Xpos)
#print("Ypos = ", Ypos)
#rint("Zpos = ", Zpos)
#print("roll = ", roll)
#print("pitch = ", pitch)
#print("yow = ", yaw)
#print("..................................")

def Overall_tool_translation_matrix(x, y, z, yaw, pitch, roll):
    alpha = np.deg2rad(yaw)
    beta = np.deg2rad(pitch)
    gamma = np.deg2rad(roll)

    T_0_T = np.array([[(np.cos(alpha)*np.cos(gamma))-(np.cos(beta)*np.sin(alpha)*np.sin(gamma)), (np.cos(gamma)*np.sin(alpha))+(np.cos(alpha)*np.cos(beta)*np.sin(gamma)), np.sin(beta)*np.sin(gamma), x],
                      [(np.cos(beta)*np.cos(gamma)*np.sin(alpha))+(np.cos(alpha)*np.sin(gamma)), (np.cos(alpha)*np.cos(beta)*np.cos(gamma))-(np.sin(alpha)*np.sin(gamma)), np.cos(gamma)*np.sin(beta), y],
                      [np.sin(alpha)*np.sin(beta), np.cos(alpha)*np.sin(beta), -np.cos(beta), z],
                        [0, 0, 0, 1]])
    value = np.cos(gamma)*np.sin(beta)
   
   
    
    return T_0_T

print(Overall_tool_translation_matrix(64.9094406653893, 58.0514491233303, -295.019339020579, 176.329503491685, 102.503916617342, -20.1944289077349))
T_0_T = Overall_tool_translation_matrix(64.9094406653893, 58.0514491233303, -295.019339020579, 176.329503491685, 102.503916617342, -20.1944289077349)
work_frame = np.array([[1, 0, 0, 0],
                       [0, 1, 0, 0],
                       [0, 0, 1, 0],
                       [0, 0, 0, 1]])

T_0_T_offset = np.dot(T_0_T, work_frame)
T_0_T_offset[0,0] = T_0_T_offset[0,0]*-1
print(T_0_T_offset)