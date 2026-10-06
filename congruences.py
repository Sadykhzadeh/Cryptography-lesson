from math import isqrt


def isCongruent(a, b, divisor):
    """Whether a and b leave the same remainder when divided by divisor."""
    # This used to read `a % c == b % c` against a global c, so the function
    # could not be called or tested on its own.
    return a % divisor == b % divisor


def isPrime(n):
    """Whether n is prime."""
    # This was:
    #
    #     for i in range(2, int(a**0.5)+1):
    #         if a % 2 == 0: return False
    #     return True
    #
    # The loop variable was never used - the body tested a % 2 every time -
    # so nothing but even numbers was ever rejected, and 9, 15, 21, 25 and 49
    # were all reported prime. The range also starts at 2, so it is empty for
    # n of 0, 1 and every negative, all of which came back prime too.
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for i in range(3, isqrt(n) + 1, 2):
        if n % i == 0:
            return False
    return True


def askForIntegers(prompt, count):
    """Reads `count` integers from one line, asking again until they parse."""
    while True:
        try:
            values = [int(part) for part in input(prompt).split()]
        except EOFError:
            raise SystemExit('\nNo more input. Exiting...')
        except KeyboardInterrupt:
            raise SystemExit('\nExiting...')
        if len(values) == count:
            return values
        print(f'Please enter exactly {count} integer(s), separated by spaces.')


def main():
    a, b = askForIntegers('Enter two integers: ', 2)

    while True:
        divisor, = askForIntegers('Enter the divisor: ', 1)
        # Dividing by zero used to raise, and the bare `except: pass` around
        # the whole program swallowed it, so the run simply printed nothing.
        if divisor != 0:
            break
        print('The divisor cannot be zero.')

    candidate, = askForIntegers('Enter integer to check whether prime or not: ', 1)

    relation = ' ' if isCongruent(a, b, divisor) else ' not '
    print(f'{a} and {b} are{relation}congruent when divided by {divisor}')

    primality = ' ' if isPrime(candidate) else ' not '
    print(f'{candidate} is{primality}a prime number')


if __name__ == '__main__':
    main()
