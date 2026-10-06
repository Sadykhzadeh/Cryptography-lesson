# The sieve of Eratosthenes: cross out the multiples of each prime in turn,
# and whatever is left standing is prime. Finding every prime up to n this way
# costs far less than testing each number on its own.


from math import isqrt


def eratosthenes(limit):
    """Returns a list where index i is True when i is prime."""
    # The old version built `list(range(n + 1))` and then wrote `sieve[1] = 0`
    # unconditionally, so a limit of 0 raised IndexError before any sieving
    # happened. It also iterated the list by value while zeroing entries of
    # it, which happens to work but reads as though it does not.
    if limit < 2:
        return [False] * max(limit + 1, 1)

    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False

    # Crossing out can start at i*i: any smaller multiple of i has a factor
    # below i and was crossed out already.
    for i in range(2, isqrt(limit) + 1):
        if sieve[i]:
            for multiple in range(i * i, limit + 1, i):
                sieve[multiple] = False

    return sieve


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
    sieve = eratosthenes(max(high, 0))
    # A negative low used to index the list from the end.
    primes = [n for n in range(max(low, 0), high + 1) if n < len(sieve) and sieve[n]]
    print('Primes:', primes)


if __name__ == '__main__':
    main()
