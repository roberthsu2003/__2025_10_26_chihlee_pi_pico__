from machine import ADC, Pin
from time import sleep

# 初始化 ADC（使用 GPIO 26）
potentiometer = ADC(Pin(28))

while True:
    # 讀取 ADC 值（0 ~ 65535）
    raw_value = potentiometer.read_u16()
    
    # 轉換為電壓值（0 ~ 3.3V）
    voltage = raw_value * 3.3 / 65535
    
    # 轉換為百分比（0% ~ 100%）
    percentage = raw_value * 100 / 65535
    
    print(f"原始值: {raw_value}, 電壓: {voltage:.2f}V, 百分比: {percentage:.1f}%")
    
    sleep(0.5)