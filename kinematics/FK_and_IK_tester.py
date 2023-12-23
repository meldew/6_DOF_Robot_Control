import forward_kinematics as FK
import inverse_kinematics as IK

J1 = 0.01
J2 = -90
J3 = 90
J4 = 0.01
J5 = 0.01
J6 = 0.01


Xpos, Ypos, Zpos, roll, pitch, yaw = FK.calculate_forward_kinematics(J1, J2, J3, J4, J5, J6)
J1new, J2new, J3new, J4new, J5new, J6new = IK.calculate_inverse_kinematics(Xpos, Ypos, Zpos, yaw, pitch, roll, J1, J2, J3, J5)
print("............................................")
print("Xpos: ", Xpos)
print("Ypos: ", Ypos)
print("Zpos: ", Zpos)
print("roll: ", roll)
print("pitch: ", pitch)
print("yaw: ", yaw)
print("............................................")
print("J1new: ", J1new)
print("J2new: ", J2new)
print("J3new: ", J3new)
print("J4new: ", J4new)
print("J5new: ", J5new)
print("J6new: ", J6new)
print("............................................")