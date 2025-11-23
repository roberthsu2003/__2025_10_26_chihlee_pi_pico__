from machine import Timer,Pin

def callback2000(n):    
    led = Pin("LED",mode=Pin.OUT)
    if led.value() == 0:
        led.on()
    else:
        led.off()
    
       
    
def main():
    timer = Timer(period=2000, callback=callback2000)
    
if __name__ == "__main__":
    main()
