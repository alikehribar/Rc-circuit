import numpy as np
import matplotlib.pyplot as plt


d = np.genfromtxt("data/ch1.txt", delimiter=",", skip_header=1)
v_meas = d[:, 2]                                  

F = 2000                                          
P = (1 / F)                                       

smooth = np.convolve(v_meas, (np.ones(9) / 9), mode="same")   
high = (smooth > (0.5 * smooth.max()))
rises = np.where((~high[:-1] & high[1:]))[0]      
ts = (P / np.median(np.diff(rises)))            
t_meas = ((np.arange(len(v_meas)) - rises[0]) * ts) 

R = 10000                                         
C = 4.7e-9                                        
tau = (R * C)                                    
V = 3.3                                          

t_sim = np.arange(0, (3 * P), ts)                
v_in = (V * np.where(((t_sim % P) < (0.5 * P)), 1, 0))
v_sim = np.zeros_like(t_sim)
a = np.exp(-ts / tau)
for i in range(1, len(t_sim)):
    v_sim[i] = (v_in[i - 1] + ((v_sim[i - 1] - v_in[i - 1]) * a))
i_half = np.argmax((v_sim > (0.5 * V)))
t_sim = (t_sim - t_sim[i_half])


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
plt.savefig('compare.png', dpi=140)
plt.show()
