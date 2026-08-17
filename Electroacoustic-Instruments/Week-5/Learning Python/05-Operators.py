'''
operator	example		same as
=			x = 5		x = 5	
+=			x += 3		x = x + 3	
-=			x -= 3		x = x - 3	
*=			x *= 3		x = x * 3	
/=			x /= 3		x = x / 3	
%=			x %= 3		x = x % 3	Modulus
//=			x //= 3		x = x // 3	Floor division
**=			x **= 3		x = x ** 3	Exponential


Operator	Name					Example
==			Equal					x == y
!=			Not equal				x != y
>			Greater than			x > y
<			Less than				x < y
>=			Greater than or equal 	x >= y
<=			Less than or equal to	x <= y
in			x in y					boolean
not			x not in y				boolean

'''

a = 10
b = ['hello', 10, 3.5]

if a in b: # booleen, true or false
    print('Yes, a is found in b')
else: print('No, a is not found in b')


if a not in b: # booleen, true or false
    print('Yes, a is not found in b')
else: print('No, a is found in b')


