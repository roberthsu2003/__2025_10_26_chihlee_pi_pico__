import random

def play_game():
    min = 1
    max = 100
    count = 0
    target = random.randint(min, max)
    print(target)
    print("===============猜數字遊戲=================:\n")
    while(True):
        count += 1
        keyin = int(input(f"猜數字範圍{min}~{max}: "))
        if(keyin >=min and keyin <= max):
            if(keyin == target):
                print(f"賓果!猜對了, 答案是:{target}")
                print(f"您猜了{count}次")
                break
            elif (keyin > target):
                max = keyin - 1
                print("再小一點")
            elif (keyin < target):
                min = keyin + 1
                print("再大一點")
            print("您已經猜了",count,"次\n")
        else:
            print("請輸入提示範圍內的數字")
            
    
    
def main():    
    while(True):
        play_game()
        play_again = input("您還要玩嗎?(y,n)")
        if play_again == "n":
            break    
    print("Game Over")
    

if __name__ == "__main__":
    n = 0
    main()

