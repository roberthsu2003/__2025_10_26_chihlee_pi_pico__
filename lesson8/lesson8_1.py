from machine import Pin

led_pin = 15

led = Pin(led_pin, Pin.OUT)
led.on()
