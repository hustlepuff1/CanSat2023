import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 상수 설정
R_EARTH = 6371  # 지구 반지름 (km)
SATELLITE_ALTITUDE = 35786  # 고정 위성의 고도 (km)
R_SATELLITE = R_EARTH + SATELLITE_ALTITUDE  # 지구 중심으로부터의 위성의 거리

# 그래프 설정
fig, ax = plt.subplots()
ax.set_xlim(-R_SATELLITE * 1.5, R_SATELLITE * 1.5)
ax.set_ylim(-R_SATELLITE * 1.5, R_SATELLITE * 1.5)
ax.set_aspect('equal', 'box')
ax.set_title("Satellite Orbiting Earth")

# 지구 그리기
earth = plt.Circle((0, 0), R_EARTH, color='blue', label="Earth")
ax.add_patch(earth)

# 위성 초기 위치
satellite, = ax.plot([], [], 'ro', label="Satellite")

def init():
    satellite.set_data([], [])
    return satellite,

def update(frame):
    x = R_SATELLITE * np.cos(np.radians(frame))
    y = R_SATELLITE * np.sin(np.radians(frame))
    satellite.set_data(x, y)
    return satellite,

ani = FuncAnimation(fig, update, frames=np.linspace(0, 360, 360), init_func=init, blit=True,interval=50)

plt.legend()
plt.show()