import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.widgets import Slider

df = pd.read_csv("data/cleaned.csv")
df = df[:60000] # select a subset from dataframe
x_accel = df.iloc[:, 0].tolist()
y_accel = df.iloc[:, 1].tolist()
z_accel = df.iloc[:, 2].tolist()
time_values = df.iloc[:, 3].tolist() 

fig, (ax_x, ax_y, ax_z) = plt.subplots(3, 1, sharex=True)

line_x, = ax_x.plot(time_values, x_accel, linewidth=0.1)
line_y, = ax_y.plot(time_values, y_accel, linewidth=0.1)
line_z, = ax_z.plot(time_values, z_accel, linewidth=0.1)

ax_x.set_ylabel('X acceleration')
ax_y.set_ylabel('Y acceleration')
ax_z.set_ylabel('Z acceleration')
ax_z.set_xlabel('time (s)')

ax_x.set_ylim(min(x_accel), max(x_accel))
ax_y.set_ylim(min(y_accel), max(y_accel))
ax_z.set_ylim(min(z_accel), max(z_accel))

ax_slider = plt.axes([0.1, 0.02, 0.65, 0.03])
slider = Slider(ax_slider, 'Scroll', 0, len(time_values) - 1, valinit=0, valstep=1)

def update(val):
    index = int(slider.val)
    one_minute = 60
    ax_x.set_xlim(time_values[index], time_values[index] + one_minute)
    ax_y.set_xlim(time_values[index], time_values[index] + one_minute)
    ax_z.set_xlim(time_values[index], time_values[index] + one_minute)
    fig.canvas.draw_idle()

slider.on_changed(update)

plt.tight_layout()
plt.show()


