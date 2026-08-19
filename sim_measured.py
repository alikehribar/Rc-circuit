# Same analysis as sim.py, but fed with the measured oscilloscope trace
# instead of a synthetic waveform. Data file: ch1.txt (time_s, raw_code, volts)
import numpy as np
import matplotlib.pyplot as plt

R = 10000
C = 4.7e-9
tau = (R * C)
V = 3.28
F = 2000
P = (1 / F)

d = np.genfromtxt("ch1.txt", delimiter=",", skip_header=1)
v_meas = d[:, 2]

ts = (P / 491.2)
t_meas = (np.arange(len(v_meas)) * ts)

hi = (v_meas > (0.9 * v_meas.max()))
falls = np.where((hi[:-1] & ~hi[1:]))[0]

taus = []
for k in falls:
    seg = v_meas[(k + 2):(k + 220)]
    if (len(seg) < 50):
        continue
    V0 = seg[0]
    mask = (seg > (0.20 * V0))    
    v_win = seg[mask]                   
    t_local = (np.arange(len(v_win)) * ts)
    y = np.log(v_win)
    m = np.polyfit(t_local, y, 1)[0]
    taus.append((-1 / m))

tau_measured = float(np.median(taus))
print("dt           =", (ts * 1e6), "us")
print("tau (R*C)    =", (tau * 1e6), "us")
print("tau_measured =", (tau_measured * 1e6), "us")
print("error        =", (((tau_measured - tau) / tau) * 100), "%")

t_sim = np.arange(0, (3 * P), ts)
v_in = (V * np.where(((t_sim % P) < (0.5 * P)), 1, 0))
v_sim = np.zeros_like(t_sim)
a = np.exp(-ts / tau)
for i in range(1, len(t_sim)):
    v_sim[i] = (v_in[i - 1] + ((v_sim[i - 1] - v_in[i - 1]) * a))

tm = ((t_meas - (falls[0] * ts)) * 1e6)
tsx = ((t_sim - (0.5 * P)) * 1e6)

plt.figure(figsize=(11, 5))
plt.plot(tm, v_meas, lw=1.1, label='Measured (oscilloscope CH1)')
plt.plot(tsx, v_sim, lw=1.6, ls='--', label='Simulated (R=9730, C=4.9nF)')
plt.plot(tsx, v_in, lw=0.8, alpha=0.4, label='PWM input')
plt.xlim(-100, 900)
plt.xlabel('Time (us)')
plt.ylabel('Voltage (V)')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('compare.png', dpi=140)
plt.show()
