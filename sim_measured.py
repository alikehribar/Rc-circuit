import numpy as np
import matplotlib.pyplot as plt


d = np.genfromtxt("data/ch1.txt", delimiter=",", skip_header=1)
v_meas = d[:, 2]                                  

F = 2000                                          
P = (1 / F)                                       

smooth = np.convolve(v_meas, (np.ones(9) / 9), mode="same")   
high = (smooth > (0.5 * smooth.max()))
rise_samples = np.where((~high[:-1] & high[1:]))[0]
samples_per_cycle = int(np.median(np.diff(rise_samples)))
ts = (P / samples_per_cycle)          # sample interval, seconds
t_meas = ((np.arange(len(v_meas)) - rise_samples[0]) * ts) 

R = 10000                                         
C = 4.7e-9                                        
tau = (R * C)                                    
V = 3.3                                          

t_sim = np.arange(0, (3 * P), ts)                
v_in = (V * np.where(((t_sim % P) < (0.5 * P)), 1, 0))
v_sim = np.zeros_like(t_sim)

a = np.exp(-ts / tau)
for k in range(1, len(t_sim)):
    v_sim[k] = (v_in[k - 1] + ((v_sim[k - 1] - v_in[k - 1]) * a))
idx_half = np.argmax((v_sim > (0.5 * V)))
t_sim = (t_sim - t_sim[idx_half])



sample_no = np.arange(len(v_meas))


sample_in_cycle = ((sample_no - rise_samples[0]) % samples_per_cycle)


average_cycle = (np.bincount(sample_in_cycle, weights=smooth)
                 / np.bincount(sample_in_cycle))
discharge_start = int(np.where((average_cycle >= (0.98 * average_cycle.max())))[0].max())


t_since_discharge = (((sample_in_cycle - discharge_start) % samples_per_cycle) * ts)


mask = ((t_since_discharge < (0.5 * P)) & (v_meas > (0.10 * v_meas.max())))
t_fit = t_since_discharge[mask]
v_fit = v_meas[mask]
m, b = np.polyfit(t_fit, np.log(v_fit), 1)
tau_meas = (-1 / m)
res = (np.log(v_fit) - ((m * t_fit) + b))

print("points used  :", mask.sum())
print("tau_measured :", round((tau_meas * 1e6), 2), "us  (theory",
      round((tau * 1e6), 2), "us,", round((((tau_meas - tau) / tau) * 100), 2), "%)")
print("V0_fit       :", round(float(np.exp(b)), 2), "V   (cursor peak 3.28 V)")
print("residual std :", format(res.std(), ".3g"), "(log units)")


plt.figure()
plt.subplot(2, 1, 1)
plt.plot((t_fit * 1e6), np.log(v_fit), '.', ms=3, label='ln(v)')
plt.plot((t_fit * 1e6), ((m * t_fit) + b), 'r-', label=('tau = %.2f us' % (tau_meas * 1e6)))
plt.ylabel('ln(v)')
plt.legend()
plt.grid(alpha=0.3)

plt.subplot(2, 1, 2)
plt.plot((t_fit * 1e6), res, '.', ms=3)
plt.axhline(0, color='r')
plt.xlabel('Time since start of discharge (us)')
plt.ylabel('Residual')
plt.grid(alpha=0.3)
plt.savefig('images/logfit_measured.png', dpi=140)


plt.figure(figsize=(11, 5))
plt.plot((t_meas * 1e6), v_meas, lw=1.0, label='Measured (oscilloscope CH1)')
plt.plot((t_sim * 1e6), v_sim, lw=1.6, ls='--', label='Ideal simulation (10 kohm, 4.7 nF)')
plt.plot((t_sim * 1e6), v_in, lw=0.8, alpha=0.4, label='3.3 V PWM input')
plt.xlim(-50, 1000)
plt.xlabel('Time (us)')
plt.ylabel('Voltage (V)')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('images/measured_vs_sim.png', dpi=140)
plt.show()
