# Primality testing and prime generation for generate_keys.py.
#
# This module was imported by generate_keys.py but never existed in the
# repository, so the key generator could not run.
#
# Miller-Rabin rather than Fermat: a Carmichael number passes Fermat's test
# for every base coprime to it, as fermat_primality_test.py demonstrates, and
# a composite modulus means an RSA key that leaks. Miller-Rabin has no such
# blind spot - each round rejects a composite with probability at least 3/4,
# independently.

import secrets

# Trial division by these first clears most candidates far more cheaply than
# a Miller-Rabin round would.
SMALL_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
    151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
]

# 40 rounds leaves a false-positive probability below 4^-40, which is far
# under the chance of the hardware getting the arithmetic wrong.
DEFAULT_ROUNDS = 40


def rabinMiller(num, rounds=DEFAULT_ROUNDS):
    """Whether num is probably prime, by the Miller-Rabin test."""
    if num < 2:
        return False
    if num in (2, 3):
        return True
    if num % 2 == 0:
        return False

    # Write num - 1 as d * 2^s with d odd.
    s = 0
    d = num - 1
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(rounds):
        # secrets, not random: a witness drawn from a predictable sequence
        # makes the test predictable too, and this module generates key
        # material.
        a = 2 + secrets.randbelow(num - 3)
        x = pow(a, d, num)
        if x in (1, num - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % num
            if x == num - 1:
                break
        else:
            return False

    return True


def isPrime(num):
    """Whether num is prime: trial division first, then Miller-Rabin."""
    if num < 2:
        return False
    for prime in SMALL_PRIMES:
        if num == prime:
            return True
        if num % prime == 0:
            return False
    return rabinMiller(num)


def generateLargePrime(keysize=1024):
    """A random prime of exactly `keysize` bits."""
    if keysize < 16:
        raise ValueError('keysize must be at least 16 bits')
    while True:
        # secrets.randbits gives cryptographically secure bits. The top bit is
        # forced so the number really is keysize bits wide, and the bottom one
        # so it is odd - half of all candidates are otherwise thrown away by
        # the first trial division.
        candidate = secrets.randbits(keysize) | (1 << (keysize - 1)) | 1
        if isPrime(candidate):
            return candidate


if __name__ == '__main__':
    for n in (1, 2, 97, 561, 1105, 1729, 7919):
        print(f'isPrime({n:5}) -> {isPrime(n)}')
    print('\nA 256-bit prime:', generateLargePrime(256))
