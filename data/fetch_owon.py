"""Pull both channels off the OWON scope over LAN and write them as CSV.

Recovered from the original acquisition session. The scope answers the plain
text command STARTBIN on a TCP socket and streams a binary block: a header,
then 3040 int16 samples for CH1 at byte 81 and the same for CH2 at byte 6220.

Usage:  python3 data/fetch_owon.py [host] [peak_volts]
"""
import socket
import struct
import sys

HOST = (sys.argv[1] if (len(sys.argv) > 1) else "192.168.50.72")
PORT = 3000
PEAK = (float(sys.argv[2]) if (len(sys.argv) > 2) else 3.28)   # cursor reading
N = 3040
OFFSETS = {"ch1": 81, "ch2": 6220}

s = socket.create_connection((HOST, PORT), timeout=5)
s.sendall(b"STARTBIN\n")
s.settimeout(3)
data = b""
try:
    while True:
        chunk = s.recv(65536)
        if (not chunk):
            break
        data += chunk
except socket.timeout:
    pass
s.close()
print("bytes received:", len(data))

# The instrument reports raw ADC codes. Scale against the peak measured with a
# cursor; the largest code in the record is taken as that peak.
for name, off in OFFSETS.items():
    codes = struct.unpack_from(("<%dh" % N), data, off)
    top = max(max(codes), 1)
    volts_per_code = (PEAK / top)
    with open(("data/%s.txt" % name), "w") as f:
        f.write("sample,raw_code,volts\n")
        for k, c in enumerate(codes):
            f.write("%d,%d,%.4f\n" % (k, c, (c * volts_per_code)))
    print(name, ": codes", min(codes), "to", top,
          " scale", round(volts_per_code, 5), "V/code -> data/%s.txt" % name)

# The sample interval is deliberately not written out. The instrument does not
# report it in this block, and the value assumed in the original capture
# (0.4 us) contradicts the 2 kHz square wave. Derive it in the analysis script
# from the measured edge spacing instead.
