from machine import Timer

def callback2000(n):    
    global count
    count += 1
    if count == 5:
        n.deinit()
        print("再見")
    else:
        print("Hello! Pico")
       
    
def main():
    timer = Timer(period=2000, callback=callback2000)
    
if __name__ == "__main__":
    count = 0
    main()