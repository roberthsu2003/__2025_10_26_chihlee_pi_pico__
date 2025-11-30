from machine import Pin
import time

# 初始化內建 LED
# 對於 Raspberry Pi Pico W，使用 "LED"
# 對於原始 Raspberry Pi Pico，通常使用 25
try:
    led = Pin("LED", Pin.OUT)
except:
    led = Pin(25, Pin.OUT)

def main():
    print("Pico is running!")
    
    while True:
        # 切換 LED 狀態
        led.toggle()
        
        # 顯示當前狀態
        if led.value():
            print("LED ON")
        else:
            print("LED OFF")
            
        # 等待 1 秒
        time.sleep(1)

if __name__ == "__main__":
    main()