#!/usr/bin/env python


# def is_integer(x):
#     if


def data_input():
    print "\nYou will enter two integers."
    print "The program will then perform some calculations.\n"

    print "Enter the first integer and press 'return'."
    a = raw_input()

    print "\nEnter the second integer and press 'return'."
    b = raw_input()

    print "\nThe two integers you entered are:"
    print "a = %s" % a
    print "b = %s\n" % b

    return (int(a), int(b))


def addition(a, b):
    c = a + b
    return "Their sum is:\n%s + %s = %s\n" % (
        "{:,}".format(a),
        "{:,}".format(b),
        "{:,}".format(c)
        )


def subtraction(a, b):
    c = a - b
    return "Their difference is:\n%s - %s = %s\n" % (
        "{:,}".format(a),
        "{:,}".format(b),
        "{:,}".format(c)
        )


def multiplication(a, b):
    c = a * b
    return "Their product is:\n%s x %s = %s\n" % (
        "{:,}".format(a),
        "{:,}".format(b),
        "{:,}".format(c)
        )


def division(a, b):
    c = a / b
    d = a % b
    return "Their quotient and remainder are:\n%s / %s = %s r %s\n" % (
        "{:,}".format(a),
        "{:,}".format(b),
        "{:,}".format(c),
        "{:,}".format(d)
        )


a, b = data_input()
print addition(a, b)
print subtraction(a, b)
print multiplication(a, b)
print division(a, b)
