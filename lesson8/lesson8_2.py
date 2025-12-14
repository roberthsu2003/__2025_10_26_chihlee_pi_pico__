from machine import Pin
from time import sleep

btn_pin = 14

button = Pin(btn_pin,Pin.IN,Pin.PULL_UP)

while(True):
    if button.value() == 1:
        print("沒按")
    else:
        print("按下")
    sleep(1)
    
    