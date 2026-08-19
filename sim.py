import numpy as np
import matplotlib.pyplot as plt

R = 10000
C =4.7e-9
tau = R * C
V=3.3
F =2000 #pwm
P = 1/F     
ts = 0.05e-6
t = np.arange(0, 10*P, ts)

D = 0.5
a = np.exp(-ts/tau)
vout  =np.zeros_like(t)
v_in = V * np.where(((t % P) < (1-D)*P), 0, 1)

for i in range(1, len(t)):
    target = v_in[i - 1]
    vout[i] = (target + (vout[i-1] - target) * a)


# edges = np.where(np.diff(v_in) < 0)[0]
# k = edges[0]
# V0 = vout[k]

# print("edge index k =", k)
# print("V0 =", V0)

# start = (k + 1)
# seg = vout[start:(start + 2000)]
# mask = (seg > (0.05 * V0))
# v_win = seg[mask]
# t_local = (np.arange(len(v_win)) * ts)

# y = np.log(v_win / V0)
# m, b = np.polyfit(t_local, y, 1)
# tau_measured = -1 / m

# print("tau (R*C)   =", tau * 1e6, "us")
# print("tau_measured =", tau_measured * 1e6, "us")
# print("error =", ((tau_measured - tau) / tau) * 100, "%")

plt.plot((t * 1e6), v_in, label='Vin')
plt.plot((t * 1e6), vout, label='Vout')
plt.xlabel('Time (us)')
plt.ylabel('Voltage (V)')
plt.legend()
plt.grid(alpha=0.3)
plt.show()




    