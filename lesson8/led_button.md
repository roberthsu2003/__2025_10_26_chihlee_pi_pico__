# Raspberry Pi Pico - LED 按鈕切換控制

## 📋 專案說明

本程式實作了一個 **Switch 開關模式** 的 LED 控制器，每按一次按鈕，LED 狀態就會切換（開↔關），並且加入了 **防彈跳（Debounce）機制** 來確保操作的穩定性。

---

## 🔌 硬體接線

| 元件 | GPIO 腳位 | 說明 |
|------|----------|------|
| 按鈕 | GPIO 14 | 使用內部上拉電阻 |
| LED | GPIO 15 | 輸出模式 |

### 接線圖示意

```
Raspberry Pi Pico
    ┌─────────────┐
    │             │
    │  GPIO 14 ───┼──── 按鈕 ──── GND
    │             │
    │  GPIO 15 ───┼──── LED (+) ──── 電阻 ──── GND
    │             │
    └─────────────┘
```

---

## 📝 程式碼

```python
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
```

---

## 🔍 程式碼詳細解說

### 1. 匯入模組

```python
from machine import Pin
from time import sleep_ms
```

- `Pin`：用於控制 GPIO 腳位
- `sleep_ms`：毫秒級延遲函數

### 2. 腳位設定

```python
btn_pin = 14
led_pin = 15

button = Pin(btn_pin, Pin.IN, Pin.PULL_UP)
led = Pin(led_pin, Pin.OUT)
```

| 參數 | 說明 |
|------|------|
| `Pin.IN` | 設定為輸入模式 |
| `Pin.PULL_UP` | 啟用內部上拉電阻，按鈕未按下時為高電位 (1) |
| `Pin.OUT` | 設定為輸出模式 |

### 3. 狀態變數

```python
led_state = False
last_button_state = 1
```

| 變數 | 用途 |
|------|------|
| `led_state` | 記錄 LED 目前狀態（True=亮，False=滅）|
| `last_button_state` | 記錄上一次讀取的按鈕狀態，用於邊緣偵測 |

### 4. 邊緣偵測（Edge Detection）

```python
if last_button_state == 1 and current_button_state == 0:
```

這行程式碼偵測 **下降邊緣（Falling Edge）**，也就是按鈕從「放開」變成「按下」的瞬間。

```
按鈕狀態變化：
       放開          按下          放開
    ────────┐    ┌────────┐    ┌────────
            │    │        │    │
            └────┘        └────┘
         ↑ 下降邊緣    ↑ 上升邊緣
         (我們偵測這個)
```

**為什麼需要邊緣偵測？**
- 如果只判斷 `button.value() == 0`，持續按住按鈕時會不斷觸發
- 使用邊緣偵測，只在按下的「瞬間」觸發一次

### 5. 防彈跳機制（Debounce）

```python
sleep_ms(50)

if button.value() == 0:
    led_state = not led_state
    led.value(led_state)
```

#### 什麼是按鈕彈跳？

機械式按鈕在按下或放開時，金屬接點會產生物理性的彈跳，導致短時間內產生多次開關訊號：

```
理想情況：
HIGH ─────┐
          │
LOW       └─────────────

實際情況（有彈跳）：
HIGH ─────┐ ┌┐ ┌┐
          │ ││ ││
LOW       └─┘└─┘└────────
          ←──────→
          彈跳區間
          (約 10-50 毫秒)
```

#### 防彈跳策略

本程式使用 **延遲確認法**：

1. **偵測到按下** → 等待 50 毫秒
2. **彈跳穩定後** → 再次讀取按鈕值
3. **確認仍為按下** → 才執行 LED 切換

### 6. 狀態切換

```python
led_state = not led_state
led.value(led_state)
```

- `not led_state`：將布林值反轉（True↔False）
- `led.value(led_state)`：將狀態寫入 LED

### 7. 主迴圈延遲

```python
sleep_ms(10)
```

加入小延遲可以：
- 減少 CPU 使用率
- 降低功耗
- 讓程式運作更穩定

---

## 🔄 程式流程圖

```
        開始
          │
          ▼
    ┌───────────────┐
    │ 初始化 GPIO   │
    │ led_state=False│
    └───────────────┘
          │
          ▼
    ┌───────────────┐
    │ 讀取按鈕狀態   │◄──────────────┐
    └───────────────┘               │
          │                         │
          ▼                         │
    ┌───────────────┐               │
    │ 是否為下降邊緣？│               │
    │ (1→0)         │               │
    └───────────────┘               │
          │                         │
     是   │   否                    │
          ▼                         │
    ┌───────────────┐               │
    │ 等待 50ms     │               │
    │ (防彈跳)      │               │
    └───────────────┘               │
          │                         │
          ▼                         │
    ┌───────────────┐               │
    │ 按鈕仍按下？   │               │
    └───────────────┘               │
          │                         │
     是   │   否                    │
          ▼                         │
    ┌───────────────┐               │
    │ 切換 LED 狀態  │               │
    └───────────────┘               │
          │                         │
          ▼                         │
    ┌───────────────┐               │
    │ 更新按鈕狀態   │               │
    │ 延遲 10ms     │───────────────┘
    └───────────────┘
```

---

## 📚 相關知識

### 上拉電阻（Pull-up Resistor）

```
        VCC (3.3V)
          │
          ┴ 內部上拉電阻
          │
GPIO 14 ──┼──── 按鈕 ──── GND
          
按鈕放開：GPIO = HIGH (1)
按鈕按下：GPIO = LOW  (0)
```

### 為什麼使用上拉電阻？

- 確保按鈕未按下時，GPIO 有明確的高電位
- 避免浮動（Floating）狀態造成的不穩定讀值
- Pico 內建上拉電阻，使用 `Pin.PULL_UP` 即可啟用

---

## 🎯 學習重點

1. **Switch vs Momentary**
   - Momentary（瞬時）：按住時觸發，放開時停止
   - Switch（切換）：按一下切換狀態

2. **邊緣偵測**
   - 下降邊緣（Falling Edge）：HIGH → LOW
   - 上升邊緣（Rising Edge）：LOW → HIGH

3. **防彈跳技術**
   - 軟體延遲法（本程式使用）
   - 硬體 RC 濾波
   - 狀態機偵測

4. **狀態變數的重要性**
   - 記錄系統當前狀態
   - 實現狀態切換邏輯

---

## ✅ 測試結果

| 操作 | 預期結果 |
|------|----------|
| 按下按鈕第 1 次 | LED 亮起 |
| 按下按鈕第 2 次 | LED 熄滅 |
| 按下按鈕第 3 次 | LED 亮起 |
| 長按按鈕 | LED 只切換一次 |
| 快速連按 | 每次都正確切換 |

---

## 📅 更新紀錄

- **2025-12-14**：初版完成，實作 Switch 模式與防彈跳機制
