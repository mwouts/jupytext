import math


# # A recursive implementation of the factorial

def factorial(n):
    if n <= 1:
        return n
    return n * factorial(n - 1)


factorial(5)

factorial(12)

# Python has great support for large integers:

factorial(120)

# We run into troubles with large recursions!

factorial(5000)


# # Stirling's approximation of n!

def stirling_formula(x):
    return math.sqrt(2.0 * math.pi * x) * math.pow(x / math.e, x)


# Not so bad in practice:

factorial(120) / stirling_formula(120)
