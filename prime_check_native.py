# The direct way: try every divisor from 2 up to n - 1.
#
# See prime_check_smart.py for the version that stops at the square root, and
# eratosthenes_sieve.py for the one that finds a whole range at once.


def isPrime(n):
    """Whether n is prime, by trying every candidate divisor."""
    # `for i in range(2, n)` is empty for n of 2 and below, so 1, 0 and every
    # negative number used to come back as prime.
    if n < 2:
        return False
    for i in range(2, n):
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
            # Bad input used to end in a traceback.
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
