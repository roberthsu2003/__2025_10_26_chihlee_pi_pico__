from machine import Pin
from time import sleep

btn_pin = 14
led_pin = 15

button = Pin(btn_pin,Pin.IN,Pin.PULL_UP)
led = Pin(led_pin, Pin.OUT)

while(True):
    if button.value() == 1:
        led.off()
    else:
        led.on()
    
    