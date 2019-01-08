import tty
import sys
import termios
import RPi.GPIO as GPIO
import time

def setup_pins(pins):
    for pin in pins:
        GPIO.setup(pin,GPIO.OUT)

def reset_pins(pins):
    for pin in pins:
        GPIO.output(pin, 0)
    
def move_car(pins,duration):
    for pin in pins:
        GPIO.output(pin,1)
    time.sleep(duration)
    for pin in pins:
        GPIO.output(pin,0)
    
# =============================================================================
# Main code

# Terminal setup
    
orig_settings = termios.tcgetattr(sys.stdin)
tty.setraw(sys.stdin)

try:
    GPIO.setmode(GPIO.BOARD)
    pin_revright = 31
    pin_revleft = 33
    pin_left = 35
    pin_right = 37
    PIN_LIST = [pin_left, pin_right, 
        pin_revleft, pin_revright]
    
    setup_pins(PIN_LIST)
    reset_pins(PIN_LIST)
    x = 0
    duration = 1
    
    while x != chr(27): # ESC
        x=sys.stdin.read(1)[0]
        print(x)
        if x == 'a':
            move_car([pin_revleft, pin_right], duration)
        elif x == 'd':
            move_car([pin_left,pin_revright], duration)
        elif x == 'w':
            move_car([pin_left, pin_right], duration)
        elif x == 's':
            move_car([pin_revleft, pin_revright], duration)
finally:        
    # Terminal restore
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)  
    reset_pins(PIN_LIST)
    GPIO.cleanup()
