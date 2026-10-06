# The same check, stopping at the square root.
#
# If n = a * b then one of a and b is at most sqrt(n), so a divisor above the
# square root can only come paired with one below it - which would already
# have been found.


from math import isqrt


def isPrime(n):
    """Whether n is prime, trying divisors up to the square root of n."""
    # Two things the old version got wrong at the edges: `range(2, ... + 1)`
    # is empty for n of 0, 1 and 2, so 0 and 1 were reported prime, and
    # `sqrt(n)` on a negative n raised ValueError: math domain error rather
    # than simply answering no.
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    # math.isqrt is an exact integer square root. int(sqrt(n)) goes through a
    # float, so the loop bound depends on how that rounds.
    for i in range(3, isqrt(n) + 1, 2):
        if n % i == 0:
            return False
    return True


def askForRange():
    while True:
        try:
            parts = input('Enter range: ').split()
            low, high = (int(part) for part in parts)
        except EOFError:
            raise SystemExit('\nNo more input. Exiting...')
        except KeyboardInterrupt:
            raise SystemExit('\nExiting...')
        except ValueError:
            print('Please enter two integers, separated by a space.')
            continue
        if low > high:
            print('The start of the range cannot be above its end.')
            continue
        return low, high


def main():
    low, high = askForRange()
    primes = [n for n in range(low, high + 1) if isPrime(n)]
    print('Primes:', primes)


if __name__ == '__main__':
    main()
