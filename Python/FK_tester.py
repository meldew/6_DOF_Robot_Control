import forward_kinematics as FK

Xpos , Ypos, Zpos, roll, pitch, yaw = FK.calculate_forward_kinematics(0.01,10,70,-60,60,-10)

print("..................................")
print("Xpos = ", Xpos)
print("Ypos = ", Ypos)
print("Zpos = ", Zpos)
print("roll = ", roll)
print("pitch = ", pitch)
print("yow = ", yaw)
print("..................................")