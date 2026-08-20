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


plt.plot((t * 1e6), v_in, label='Vin')
plt.plot((t * 1e6), vout, label='Vout')
plt.xlabel('Time (us)')
plt.ylabel('Voltage (V)')
plt.legend()
plt.grid(alpha=0.3)
plt.show()




    