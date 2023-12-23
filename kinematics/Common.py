import math
import numpy as np
class common_DH_parameters: 
    
    a1 = 64.2
    a2 = 305
    a3, a4, a5, a6 = 0, 0, 0, 0

    d1 = 169.77
    d2, d3, d5 = 0, 0, 0
    d4 = -222.63
    d6 = -36.25

    alpha1 = np.deg2rad(-90)
    alpha2 = np.deg2rad(0)
    alpha3 = np.deg2rad(90)
    alpha4 = np.deg2rad(-90)
    alpha5 = np.deg2rad(90)
    alpha6 = np.deg2rad(0)

class Common_Matrices: 
    work_frame = np.array([[1, 0, 0, 0],
                          [0, 1, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]])  
    tool_frame = np.array([[1, 0, 0, 0],
                          [0, 1, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]])