from machine import Pin
from time import sleep_ms

btn_pin = 14
led_pin = 15

button = Pin(btn_pin, Pin.IN, Pin.PULL_UP)
led = Pin(led_pin, Pin.OUT)

# LED 狀態變數
led_state = False
# 記錄上一次按鈕狀態
last_button_state = 1  # PULL_UP，預設為高電位

while True:
    current_button_state = button.value()
    
    # 偵測按鈕從「放開」變成「按下」的瞬間 (下降邊緣)
    if last_button_state == 1 and current_button_state == 0:
        # 防彈跳延遲
        sleep_ms(50)
        
        # 再次確認按鈕確實被按下
        if button.value() == 0:
            # 切換 LED 狀態
            led_state = not led_state
            led.value(led_state)
    
    # 更新按鈕狀態
    last_button_state = current_button_state
    
    # 小延遲減少 CPU 使用
    sleep_ms(10)