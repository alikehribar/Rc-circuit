import re
import serial
import matplotlib.pyplot as plt

PORT = "/dev/cu.usbmodem1401"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=2)
f = open("data.csv", "w")
f.write("t_us,volt\n")

plt.ion()

t_vals, v_vals = [], []

try:
    while True:
        raw = ser.readline().decode(errors="replace").strip()
        m = re.match(r"\(([\d.]+), ([\d.]+)\)", raw)

        if not m:
            t_vals, v_vals = [], []
            continue

        t, v = (float(m.group(1)), float(m.group(2)))
        t_vals.append(t)
        v_vals.append(v)
        f.write(f"{t},{v}\n")

        if len(t_vals) % 50 == 0:
            plt.clf()
            plt.plot(t_vals, v_vals, marker=".", markersize=3, linewidth=1)
            plt.xlabel("t (us)")
            plt.ylabel("V")
            plt.title(f"{len(t_vals)} samples")
            plt.ylim(0, 3.3)
            plt.grid(alpha=0.3)
            plt.pause(0.001)

except KeyboardInterrupt:
    print("Stopped, final plot stays open for inspection.")
    plt.show(block=True)
