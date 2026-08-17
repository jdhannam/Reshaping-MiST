from time import sleep

_h = 10
_x = 0

def myFunction(num):
    print('i love '+ str(num) +' noodles')

while True:
    _x = _x + 1
    sleep(1)
    print(_x)
    
    if _x == _h:
        print('loop has ended')
        myFunction(_x)
        break
    
print('code after the loop')