import numpy as np
import matplotlib.pyplot as plt

R = 10000
C = 4.7e-9
tau = (R * C)
V = 3.3
F = 2000        # pwm
P = (1 / F)
ts = 0.05e-6
D = 0.5

# Count whole samples per period instead of taking t % P: in floating point the
# remainder fails to wrap for a couple of samples and shifts a whole cycle.
n_per = int(round(P / ts))
n = (10 * n_per)
idx = np.arange(n)
t = (idx * ts)                    # absolute time
t_local = ((idx % n_per) * ts)    # time since the start of the current period

v_in = (V * np.where((t_local < ((1 - D) * P)), 0, 1))
vout = np.zeros(n)
a = np.exp(-ts / tau)

for k in range(1, n):
    target = v_in[k - 1]
    vout[k] = (target + ((vout[k - 1] - target) * a))

# Log fit on the discharge half of every period. ln(v) = ln(V0) - t/tau is a
# straight line, so the slope gives tau and the intercept gives V0.
mask = ((v_in == 0) & (vout > (0.05 * V)))
t_fit = t_local[mask]
y = np.log(vout[mask])
m, b = np.polyfit(t_fit, y, 1)
tau_fit = (-1 / m)
res = (y - ((m * t_fit) + b))

print("points used  :", mask.sum())
print("slope m      :", format(m, ".6g"), "1/s")
print("tau_fit      :", round((tau_fit * 1e6), 3), "us   (input", round((tau * 1e6), 2), "us)")
print("V0_fit       :", round(float(np.exp(b)), 4), "V")
print("error        :", round((((tau_fit - tau) / tau) * 100), 4), "%")
print("residual std :", format(res.std(), ".3g"), "(log units)")

plt.figure()
plt.plot((t * 1e6), v_in, label='Vin')
plt.plot((t * 1e6), vout, label='Vout')
plt.xlabel('Time (us)')
plt.ylabel('Voltage (V)')
plt.legend()
plt.grid(alpha=0.3)

plt.figure()
plt.subplot(2, 1, 1)
plt.plot((t_fit * 1e6), y, '.', ms=1, label='ln(v)')
plt.plot((t_fit * 1e6), ((m * t_fit) + b), 'r-', label=('tau = %.3f us' % (tau_fit * 1e6)))
plt.ylabel('ln(v)')
plt.legend()
plt.grid(alpha=0.3)

plt.subplot(2, 1, 2)
plt.plot((t_fit * 1e6), res, '.', ms=1)
plt.axhline(0, color='r')
plt.xlabel('Time since start of discharge (us)')
plt.ylabel('Residual')
plt.grid(alpha=0.3)
plt.savefig('images/logfit_sim.png', dpi=140)

plt.show()
