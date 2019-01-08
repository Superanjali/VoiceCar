import tty
import sys
import termios
import RPi.GPIO as GPIO
import time

def reset_pins():
    GPIO.output(pin_left, 0)
    GPIO.output(pin_right, 0)
    GPIO.output(pin_up, 0)
    GPIO.output(pin_down, 0)

def move_car(pin,duration):
    GPIO.output(pin,1)
    time.sleep(duration)
    GPIO.output(pin,0)
    
# =============================================================================
# Main code

# Terminal setup
orig_settings = termios.tcgetattr(sys.stdin)
tty.setraw(sys.stdin)

GPIO.setmode(GPIO.BOARD)
pin_left = 31
pin_up = 33
pin_down = 35
pin_right = 37

GPIO.setup(pin_left,GPIO.OUT)
GPIO.setup(pin_right,GPIO.OUT)
GPIO.setup(pin_up,GPIO.OUT)
GPIO.setup(pin_down,GPIO.OUT)


x = 0
reset_pins()
duration = 1

while x != chr(27): # ESC
    x=sys.stdin.read(1)[0]
    #print("You pressed", x)
    if x == 'a':
        move_car(pin_left, duration)
    elif x == 'd':
        move_car(pin_right, duration)
    elif x == 'w':
        move_car(pin_up, duration)
    elif x == 's':
        move_car(pin_down, duration)
        

# Terminal restore
termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)  
