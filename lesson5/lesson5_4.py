from machine import Timer, Pin
import time

# 全域變數，避免每次 callback 都創建新的 Pin 物件
led = Pin("LED", mode=Pin.OUT)

def callback5000(n):    
    """每 5 秒觸發一次，讓 LED 閃爍 2 次"""
    for i in range(2):  # 閃爍 2 次
        led.on()  # 打開 LED
        time.sleep_ms(100)  # 亮 100 毫秒
        led.off()  # 關閉 LED
        if i < 1:  # 最後一次閃爍後不需要等待
            time.sleep_ms(100)  # 兩次閃爍之間的間隔
    
def main():
    timer = Timer(period=5000, callback=callback5000)
    
if __name__ == "__main__":
    main()
