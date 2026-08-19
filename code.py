import board
import pwmio

SQUARE_HZ = 2000
duty = 0.5

pwm = pwmio.PWMOut(board.GP2, frequency=SQUARE_HZ, duty_cycle=int(duty * 65535))
pwm2 = pwmio.PWMOut(board.GP3, frequency=SQUARE_HZ, duty_cycle=int(duty * 65535))

while True:
    pass
