import array
import board
import analogbufio
import pwmio

SAMPLE_RATE = 500000      
SQUARE_HZ = 2000 
SAMPLE_COUNT = 20000 
VREF = 3.3                
duty = 0.5
pwm = pwmio.PWMOut(board.GP2 , frequency= SQUARE_HZ , duty_cycle = int(duty * 65535))
buf = array.array('H', ([0]) * SAMPLE_COUNT)
adc = analogbufio.BufferedIn(board.A0, sample_rate=SAMPLE_RATE)
dt = 1/SAMPLE_RATE

while True:

 adc.readinto(buf)
 print('tus', 'volt')
 for i in range(SAMPLE_COUNT):
    tus = (i * dt * 1e6)
    volt = ((buf[i]) / 65535.0 * VREF)
    print((tus, volt))