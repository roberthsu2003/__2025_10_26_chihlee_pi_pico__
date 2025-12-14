# Raspberry Pi Pico - 可變電阻（Potentiometer）使用指南

## 📋 專案說明

本文件介紹如何在 Raspberry Pi Pico 上使用 **可變電阻（Potentiometer）**，包含 ADC（類比數位轉換器）的基本觀念、接線方式與程式範例。

---

## 🔧 什麼是可變電阻？

可變電阻是一種 **可調整阻值** 的電子元件，透過旋轉旋鈕或滑動滑桿來改變電阻值，常用於：

- 音量控制
- 亮度調整
- 馬達速度控制
- 感測器校正

### 可變電阻結構

```
        ┌─────────────────┐
        │    旋轉旋鈕      │
        │       ◯         │
        └────┬──┬──┬──────┘
             │  │  │
            VCC OUT GND
            (1) (2) (3)

腳位說明：
- 腳位 1 (VCC)：接電源正極 (3.3V)
- 腳位 2 (OUT)：輸出訊號（中間抽頭）
- 腳位 3 (GND)：接地
```

---

## ⚡ 核心觀念：ADC（類比數位轉換器）

### 類比 vs 數位訊號

| 訊號類型 | 特性 | 範例 |
|---------|------|------|
| **數位訊號** | 只有 0 和 1 兩種狀態 | 按鈕、LED 開關 |
| **類比訊號** | 連續變化的數值 | 溫度、亮度、可變電阻 |

### Pico 的 ADC 規格

| 項目 | 規格 |
|------|------|
| ADC 解析度 | 12 位元 (0-4095) |
| `read_u16()` 回傳值 | 16 位元 (0-65535) |
| 輸入電壓範圍 | 0V ~ 3.3V |
| 可用 ADC 腳位 | GPIO 26, 27, 28 |
| 內部溫度感測器 | ADC 通道 4 |

### ⚠️ 重要注意事項

> **Pico 的 ADC 最大輸入電壓為 3.3V！**
> 
> 絕對不可以將 5V 訊號直接連接到 ADC 腳位，這會導致 Pico 永久損壞！

---

## 🔌 硬體接線

### 可用的 ADC 腳位

| ADC 通道 | GPIO 腳位 | 說明 |
|----------|----------|------|
| ADC0 | GPIO 26 | 一般用途 |
| ADC1 | GPIO 27 | 一般用途 |
| ADC2 | GPIO 28 | 一般用途 |
| ADC3 | GPIO 29 | 內部用於 VSYS 監測 |
| ADC4 | 內部 | 溫度感測器 |

### 接線圖示意

```
Raspberry Pi Pico
    ┌─────────────────────┐
    │                     │
    │  3.3V ──────────────┼──── 可變電阻 VCC (腳位1)
    │                     │
    │  GPIO 26 (ADC0) ────┼──── 可變電阻 OUT (腳位2)
    │                     │
    │  GND ───────────────┼──── 可變電阻 GND (腳位3)
    │                     │
    └─────────────────────┘
```

### 電路原理（分壓原理）

```
    3.3V
      │
      ┴ R1 (可變部分上半)
      │
      ├──── GPIO 26 (輸出電壓)
      │
      ┴ R2 (可變部分下半)
      │
    GND

輸出電壓 = 3.3V × (R2 / (R1 + R2))

旋轉旋鈕會改變 R1 和 R2 的比例：
- 轉到最左：R1 ≈ 0, R2 = 最大 → 輸出 ≈ 3.3V
- 轉到中間：R1 = R2 → 輸出 ≈ 1.65V
- 轉到最右：R1 = 最大, R2 ≈ 0 → 輸出 ≈ 0V
```

---

## 📝 基本程式碼

### 範例一：讀取可變電阻數值

```python
from machine import ADC, Pin
from time import sleep

# 初始化 ADC（使用 GPIO 26）
potentiometer = ADC(Pin(26))

while True:
    # 讀取 ADC 值（0 ~ 65535）
    raw_value = potentiometer.read_u16()
    
    # 轉換為電壓值（0 ~ 3.3V）
    voltage = raw_value * 3.3 / 65535
    
    # 轉換為百分比（0% ~ 100%）
    percentage = raw_value * 100 / 65535
    
    print(f"原始值: {raw_value}, 電壓: {voltage:.2f}V, 百分比: {percentage:.1f}%")
    
    sleep(0.5)
```

### 範例二：控制 LED 亮度（PWM）

```python
from machine import ADC, Pin, PWM
from time import sleep

# 初始化 ADC 和 PWM
potentiometer = ADC(Pin(26))
led = PWM(Pin(15))
led.freq(1000)  # 設定 PWM 頻率為 1000Hz

while True:
    # 讀取可變電阻值
    adc_value = potentiometer.read_u16()
    
    # 直接將 ADC 值作為 PWM 的 duty cycle
    led.duty_u16(adc_value)
    
    sleep(0.01)
```

---

## 🔍 程式碼詳細解說

### 1. 匯入模組

```python
from machine import ADC, Pin
from time import sleep
```

| 模組 | 說明 |
|------|------|
| `ADC` | 類比數位轉換器類別 |
| `Pin` | GPIO 腳位控制 |
| `sleep` | 延遲函數（秒） |

### 2. 初始化 ADC

```python
potentiometer = ADC(Pin(26))
```

或使用簡化寫法：

```python
potentiometer = ADC(26)
```

### 3. 讀取方法比較

| 方法 | 回傳範圍 | 說明 |
|------|---------|------|
| `read_u16()` | 0 ~ 65535 | 16 位元無符號整數 |

### 4. 數值轉換

#### 轉換為電壓

```python
voltage = raw_value * 3.3 / 65535
```

#### 轉換為百分比

```python
percentage = raw_value * 100 / 65535
```

#### 映射到自訂範圍

```python
def map_value(x, in_min, in_max, out_min, out_max):
    """將數值從一個範圍映射到另一個範圍"""
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# 例如：將 ADC 值映射到 0-180 度（用於伺服馬達）
angle = map_value(raw_value, 0, 65535, 0, 180)
```

---

## ⚠️ 常見問題與注意事項

### 1. 數值不穩定（抖動）

**問題**：讀取的數值持續微幅跳動

**解決方案**：使用平均濾波

```python
def read_average(adc, samples=10):
    """讀取多次取平均值"""
    total = 0
    for _ in range(samples):
        total += adc.read_u16()
    return total // samples

# 使用方式
stable_value = read_average(potentiometer, 10)
```

### 2. 最大值和最小值不正確

**問題**：旋到底卻無法達到 0 或 65535

**可能原因**：
- 可變電阻品質問題
- 接線不良

**解決方案**：進行校正

```python
# 先記錄實際的最小值和最大值
# 假設實際範圍是 300 ~ 65200
ADC_MIN = 300
ADC_MAX = 65200

def calibrated_read(adc):
    raw = adc.read_u16()
    # 限制在校正範圍內
    raw = max(ADC_MIN, min(ADC_MAX, raw))
    # 映射到 0-65535
    return int((raw - ADC_MIN) * 65535 / (ADC_MAX - ADC_MIN))
```

### 3. 電壓超過 3.3V

> ⛔ **絕對禁止！**
> 
> ADC 輸入電壓超過 3.3V 會損壞 Pico！

**如果需要量測 5V 訊號**，請使用分壓電路：

```
5V 訊號
    │
    ┴ R1 = 10kΩ
    │
    ├──── GPIO 26 (最大 3.3V)
    │
    ┴ R2 = 20kΩ
    │
   GND

輸出電壓 = 5V × 20k/(10k+20k) = 3.33V ✓
```

---

## 📊 ADC 精度說明

### 有效位元數（ENOB）

Pico 的 ADC 雖然是 12 位元，但實際有效位元數約為 **9-10 位元**，這意味著：

| 理論解析度 | 實際解析度 |
|-----------|-----------|
| 12 bit (4096 階) | ~9-10 bit (512-1024 階) |
| 0.8mV / 階 | ~3-6mV / 階 |

### 提升精度的方法

1. **過採樣（Oversampling）**：多次讀取後平均
2. **穩定的電源**：使用乾淨的 3.3V 電源
3. **適當的接地**：避免接地迴路
4. **遠離雜訊源**：避免靠近馬達、開關電源

---

## 🎯 實用應用範例

### 範例三：可變電阻控制呼吸燈速度

```python
from machine import ADC, Pin, PWM
from time import sleep
import math

# 初始化
potentiometer = ADC(Pin(26))
led = PWM(Pin(15))
led.freq(1000)

while True:
    # 讀取可變電阻值決定速度
    pot_value = potentiometer.read_u16()
    
    # 映射到 0.5 ~ 5 秒的週期
    period = 0.5 + (pot_value / 65535) * 4.5
    
    # 呼吸效果
    for i in range(100):
        # 使用正弦函數產生平滑的亮度變化
        brightness = int((math.sin(i * math.pi / 50) ** 2) * 65535)
        led.duty_u16(brightness)
        sleep(period / 100)
```

### 範例四：多個可變電阻讀取

```python
from machine import ADC, Pin
from time import sleep

# 初始化多個 ADC
pot1 = ADC(Pin(26))  # ADC0
pot2 = ADC(Pin(27))  # ADC1
pot3 = ADC(Pin(28))  # ADC2

while True:
    value1 = pot1.read_u16()
    value2 = pot2.read_u16()
    value3 = pot3.read_u16()
    
    print(f"Pot1: {value1:5d}, Pot2: {value2:5d}, Pot3: {value3:5d}")
    
    sleep(0.2)
```

---

## 📚 相關知識

### ADC 解析度說明

```
3.3V ──────────────────────── 65535 (最大值)
                              
      ↑ 每一階約 = 3.3V / 65536
      ↓        ≈ 0.00005V (50μV)
                              
0V   ──────────────────────── 0 (最小值)
```

### 常用的類比感測器

| 感測器類型 | 說明 | 輸出範圍 |
|-----------|------|---------|
| 可變電阻 | 阻值變化 | 0 ~ VCC |
| 光敏電阻 | 光線強度 | 0 ~ VCC |
| 溫度感測器 (LM35) | 溫度 | 10mV/°C |
| 麥克風模組 | 聲音大小 | 0 ~ VCC |
| 土壤濕度感測器 | 濕度 | 0 ~ VCC |

---

## 🎓 學習重點

1. **ADC 基本概念**
   - 類比訊號轉數位訊號
   - 解析度與精度的差異

2. **Pico ADC 限制**
   - 最大輸入電壓 3.3V
   - 僅有 GPIO 26, 27, 28 可用

3. **數值處理技巧**
   - 數值映射（map function）
   - 平均濾波減少雜訊
   - 校正補償

4. **實際應用**
   - PWM 控制亮度/速度
   - 感測器數據讀取
   - 使用者輸入介面

---

## ✅ 測試檢查清單

| 測試項目 | 預期結果 |
|---------|---------|
| 旋鈕轉到最左 | 數值接近 0 |
| 旋鈕轉到最右 | 數值接近 65535 |
| 旋鈕轉到中間 | 數值約 32768 |
| 慢慢旋轉 | 數值平滑變化 |
| 固定位置 | 數值穩定（小幅跳動正常）|

---

## 📅 更新紀錄

- **2025-12-14**：初版完成，包含 ADC 觀念、接線說明與多個程式範例
