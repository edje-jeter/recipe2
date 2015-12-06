#!/usr/bin/env python

print "The computer will output the fizz-buzz sequence"
print "from 1 through an integer you enter.\n"

terminal = int(raw_input("Please enter your number: "))

output = []
for x in range(1, terminal):

    result = x
    if x % 15 == 0:
        result = "Fizz Buzz"

    elif x % 5 == 0:
        result = "Buzz"

    elif x % 3 == 0:
        result = "Fizz"
    output.append(str(result))

print ', '.join(output)
