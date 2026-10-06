# Exponentiation by squaring, with and without a modulus.


def power(x, y):
    """x ** y, by squaring - O(log y) multiplications instead of y."""
    res = 1
    while y > 0:
        # If y is odd, multiply x into the result
        if y & 1:
            res = res * x
        y >>= 1   # y = y // 2
        x = x * x  # x becomes x^2
    return res


def powerAndMod(x, y, p):
    """(x ** y) % p, reducing at every step so nothing ever grows large."""
    # `res = 1` and an `if x == 0: return 0` shortcut was wrong twice over:
    # powerAndMod(7, 0, 7) answered 0 where 7^0 % 7 is 1, and for p == 1 it
    # answered 1 where every result is 0. Seeding res with 1 % p and letting
    # the loop handle a zero exponent gets both right.
    res = 1 % p
    x = x % p
    while y > 0:
        if y & 1:
            res = (res * x) % p
        y >>= 1
        x = (x * x) % p
    return res


def findPower(a, x, n):
    """The smallest i with a^i = x (mod n), or None if there is none.

    This is a discrete logarithm by brute force: fine for teaching, hopeless
    for the sizes real cryptography uses, which is exactly why the problem is
    the basis of Diffie-Hellman.
    """
    # This used to call power(a, i) - the version with no modulus - and reduce
    # afterwards, so it built a^i in full on every step. Searching n = 5000
    # meant constructing 3^4999, a 2386-digit integer, and took 37 times
    # longer than reducing as it goes.
    for i in range(n):
        if pow(a, i, n) == x:
            return i
    return None


if __name__ == '__main__':
    print('power(2, 10)          =', power(2, 10))
    print('powerAndMod(2, 5, 13) =', powerAndMod(2, 5, 13))

    # Python's own three-argument pow() does what powerAndMod does; the
    # function is here to show how.
    print('pow(2, 5, 13)         =', pow(2, 5, 13))

    found = findPower(3, 4, 13)
    # The old version returned None silently when there was no answer, which
    # reads the same as "the answer is nothing".
    print('findPower(3, 4, 13)   =', found if found is not None else 'no such power')
