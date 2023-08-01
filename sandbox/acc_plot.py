import time
from itertools import count

import matplotlib.pyplot as plt
import numpy as np


def generate_dummy_accelerometer_data():
    return np.random.rand(3) * 10 - 5 

def plot_3d_accelerometer_data(interval=0.1, duration=10):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_zlim(-5, 5)
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    plt.ion()  

   
    previous_data = generate_dummy_accelerometer_data()
    x,y,z = previous_data
    ax.scatter(x,y,z, c='r', marker='o')

    for i in count():
        data = generate_dummy_accelerometer_data()
        x2,y2,z2 = data
        print(data)
        print(x2,y2,z2)

        ax.plot([previous_data[0], data[0]], [previous_data[1], data[1]], [previous_data[2], data[2]], c='b')
        ax.scatter(data[0], data[1], data[2], c='r', marker='o')
        plt.draw()
        plt.pause(interval)

        previous_data = data

        if i * interval >= duration:
            break

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    plot_3d_accelerometer_data(interval=0.1, duration=5)
