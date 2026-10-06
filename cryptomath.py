# The number theory generate_keys.py needs.
#
# generate_keys.py imported this module and primeNum, and neither existed in
# the repository - the file carried a "# add primeNum implementation" note and
# could not be run at all.


def gcd(a, b):
    """The greatest common divisor of a and b, by Euclid's algorithm.

    math.gcd does this in C and is what real code should call; this is the
    algorithm written out, because that is the lesson.
    """
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def extendedGcd(a, b):
    """Returns (g, x, y) with g = gcd(a, b) and a*x + b*y = g."""
    oldR, r = a, b
    oldS, s = 1, 0
    oldT, t = 0, 1
    while r:
        quotient = oldR // r
        oldR, r = r, oldR - quotient * r
        oldS, s = s, oldS - quotient * s
        oldT, t = t, oldT - quotient * t
    return oldR, oldS, oldT


def findModInverse(a, m):
    """The multiplicative inverse of a modulo m, or None when there is none.

    That is the d with (a * d) % m == 1, which is how RSA turns the public
    exponent into the private one.
    """
    if m <= 1:
        return None
    g, x, _ = extendedGcd(a % m, m)
    if g != 1:
        # No inverse exists unless a and m are coprime. Returning None rather
        # than a wrong number matters here: a silently wrong d produces a key
        # pair that cannot decrypt what it encrypts.
        return None
    return x % m


if __name__ == '__main__':
    print('gcd(252, 105)            =', gcd(252, 105))
    print('extendedGcd(252, 105)    =', extendedGcd(252, 105))
    print('findModInverse(17, 3120) =', findModInverse(17, 3120))
    print('findModInverse(6, 9)     =', findModInverse(6, 9), '(no inverse: gcd is 3)')
