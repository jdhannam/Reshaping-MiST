# Lists

'''
append()	Adds an element at the end of the list
clear()		Removes all the elements from the list
copy()		Returns a copy of the list
count()		Returns the number of elements with the specified value
len()		Returns length of list
extend()	Add the elements of a list (or any iterable), to the end of the current list
index()		Returns the index of the first element with the specified value
insert()	Adds an element at the specified position
pop()		Removes the element at the specified position
remove()	Removes the item with the specified value
reverse()	Reverses the order of the list
sort()		Sorts the list
shuffle()	randomises values
'''

a = [1,2,3,4,5,6,7,8,9]
print('original:', a)

a.reverse()
print('reversed: ', a)

a.insert(10,0) # index position, value to insert
print('insert: ', a)

b = len(a)
print('length: ', b)

a.sort()
print('ascending: ', a)

from random import shuffle # import library
shuffle(a)
print('random order: ', a)

