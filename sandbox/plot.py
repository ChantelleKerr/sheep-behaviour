




import matplotlib.pyplot as plt
import pandas as pd


df = pd.read_csv("data/cleaned.csv")  
x_accel = df.iloc[:, 0].tolist()  
y_accel = df.iloc[:, 1].tolist()  
z_accel = df.iloc[:, 2].tolist()  
time_values = df.iloc[:, 3].tolist() 


plt.subplot(3, 1, 1)
plt.plot(time_values, x_accel)
plt.title('X, Y, Z with respect to time')
plt.ylabel('X acceleration')

plt.subplot(3, 1, 2)
plt.plot(time_values, y_accel)
plt.xlabel('time (s)')
plt.ylabel('Y acceleration')

plt.subplot(3, 1, 3)
plt.plot(time_values, z_accel)
plt.xlabel('time (s)')
plt.ylabel('Z acceleration')

plt.tight_layout()
plt.show()

