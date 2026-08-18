import re
import serial
import matplotlib.pyplot as plt

PORT = "/dev/cu.usbmodem1401"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=2)
f = open("data.csv", "w")
f.write("t_us,volt\n")

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [])
ax.set_xlabel("t (us)")
ax.set_ylabel("V")

t_vals, v_vals = [], []

while True:
    raw = ser.readline().decode(errors="replace").strip()
    m = re.match(r"\(([\d.]+), ([\d.]+)\)", raw)

    if not m:
        if t_vals:
            line.set_data(t_vals, v_vals)
            ax.relim()
            ax.autoscale_view()
            plt.pause(0.01)
        t_vals, v_vals = [], []
        continue

    t, v = (float(m.group(1)), float(m.group(2)))
    t_vals.append(t)
    v_vals.append(v)
    f.write(f"{t},{v}\n")

    plt.plot
