# Fermat's primality test.
#
# (The header here used to read "find the smallest twin in given range",
# which is a different program entirely.)
#
# Fermat's little theorem says that if p is prime then a^(p-1) = 1 mod p for
# every a not divisible by p. The test runs that backwards: pick a few random
# a, and if any of them gives something other than 1, n is definitely
# composite. If they all give 1, n is *probably* prime - and the bottom of
# this file shows how badly "probably" can go.
#
# Link: https://www.geeksforgeeks.org/primality-test-set-2-fermet-method/

import random


def power(a, n, p):
    """(a ** n) % p, by squaring - O(log n) multiplications."""
    # Python's three-argument pow() does exactly this, in C, and is what real
    # code should call. The loop is kept because it is the lesson.
    #
    # The old version also wrote `a = (a ** 2) % p`, which builds the full
    # square of a before reducing it. For a 1024-bit a that is a 2048-bit
    # intermediate on every step; `a = (a * a) % p` is the same arithmetic
    # written so that it is clear only one multiplication happens.
    res = 1 % p
    a = a % p
    while n > 0:
        if n % 2:
            res = (res * a) % p
            n -= 1
        else:
            a = (a * a) % p
            n //= 2
    return res


def isPrime(n, k):
    """Whether n is probably prime, after k rounds of Fermat's test."""
    # `random.randint(2, n - 2)` has an empty range for n below 4, so the old
    # version raised ValueError for 0, for 1 handled separately, and for every
    # negative number rather than simply answering no.
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    for _ in range(k):
        # random is a Mersenne Twister, which is fine for choosing a witness.
        # Key material is a different matter - see generate_keys.py, which
        # uses secrets.
        a = random.randint(2, n - 2)
        if power(a, n - 1, n) != 1:
            return False

    return True


def _demonstrateCarmichaelNumbers(rounds=5, trials=200):
    """Shows the test failing, which is the point worth taking away.

    A Carmichael number is composite but satisfies Fermat's congruence for
    every base coprime to it, so the test can only catch it by stumbling on
    a base that shares a factor. 561 = 3 * 11 * 17 is the smallest.
    """
    print(f'\nFermat with k={rounds}, {trials} runs each:')
    for n, factors in ((561, '3 * 11 * 17'), (1105, '5 * 13 * 17'), (1729, '7 * 13 * 19')):
        called_prime = sum(1 for _ in range(trials) if isPrime(n, rounds))
        print(f'  {n} = {factors:12} called prime {called_prime:3}/{trials} times')
    print('  All three are composite. Miller-Rabin has no such blind spot,')
    print('  which is why primeNum.py uses it to generate RSA primes.')


if __name__ == '__main__':
    k = 3
    for n in (11, 15):
        print(f'isPrime({n}, {k}) -> {isPrime(n, k)}')
    _demonstrateCarmichaelNumbers()
