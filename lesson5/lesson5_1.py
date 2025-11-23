from machine import Timer

timer = Timer(period=2000, mode=Timer.PERIODIC, callback=lambda t:print('Hello! Pico'))