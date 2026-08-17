# while and for loops
from time import sleep # import time library

'''
# turn a fan on low or high depending on the temperature
while True:
    temp = int(input('input a temperature '))
    
    if temp > 0 and temp <= 80:
        print('fan is on low')
    elif temp > 80 and temp <= 100:
        print('fan is on high')
    else:
        print('the temperature is outside the acceptable range')
        break
'''

'''
# counting while if loop
i = 1
while i < 6:
    print(i)
    sleep(1)
    i += 1
'''

'''
# counting while if loop with break
i = 1
while i < 6:
    print(i)
    sleep(1)
    if i == 3:
        break
    i += 1
'''

'''
# counting while if loop with select
myArray = ['sleep', 'snotty', 'farts', 'snooty', 'tooty', 'blooty']
i = 1
while i < 6:
    print(myArray[i])
    if i == 6:
        break
    sleep(1)
    i += 1
'''

'''
# for looping strings, where x is the index value
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    print(x)
    if x == "banana":
        break
'''


# for looping numbers, use range(), and where x is the index value
for x in range(100):
    y = x * 2
    print(y)
    if x == 90:
        break

