from machine import Pin
from time import sleep

led_pin = 15
led = Pin(led_pin, Pin.OUT)

while(True):    
    led.toggle()
    sleep(2)
