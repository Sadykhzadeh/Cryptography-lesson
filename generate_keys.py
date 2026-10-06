# RSA public/private key generator.
#
# Based on the generator from Al Sweigart's "Cracking Codes with Python". It
# imported primeNum and cryptomath, neither of which was in the repository -
# the file even carried a "# add primeNum implementation" note - so it could
# not be run. Both modules are here now.

import argparse
import os
import sys

import cryptomath
import primeNum

# 1024-bit RSA has been below recommended strength for years, and the old
# default was worse than it looked: it asked for two 1024-bit primes, which
# makes a 2048-bit modulus, while writing "1024" into the key file as the
# size. Here keySize means the size of the modulus, as it conventionally
# does, and p and q get half of it each.
DEFAULT_KEY_SIZE = 2048

# The conventional public exponent. The old version drew e at random from
# [2^(keySize-1), 2^keySize), which is valid but leaves every encryption and
# every signature verification doing a full-width exponentiation for no gain.
PREFERRED_EXPONENT = 65537


def generateKey(keySize):
    """Creates a public/private key pair with a keySize-bit modulus."""
    if keySize < 32 or keySize % 2:
        raise ValueError('keySize must be an even number of at least 32 bits')

    halfSize = keySize // 2

    # Step 1: Create two prime numbers, p and q. Calculate n = p * q.
    print('Generating p prime...')
    p = primeNum.generateLargePrime(halfSize)
    print('Generating q prime...')
    q = primeNum.generateLargePrime(halfSize)
    while q == p:
        # Nothing checked this before. p == q gives n = p^2, whose factors
        # fall out of a square root, and the key is worthless.
        print('q came out equal to p; drawing another...')
        q = primeNum.generateLargePrime(halfSize)

    n = p * q
    totient = (p - 1) * (q - 1)

    # Step 2: Create a number e that is relatively prime to (p-1)*(q-1).
    print('Choosing e relatively prime to (p-1)*(q-1)...')
    e = PREFERRED_EXPONENT
    if cryptomath.gcd(e, totient) != 1:
        # Vanishingly unlikely, but it costs one line to be right about it.
        print(f'{PREFERRED_EXPONENT} shares a factor with the totient; searching...')
        e = PREFERRED_EXPONENT + 2
        while cryptomath.gcd(e, totient) != 1:
            e += 2

    # Step 3: Calculate d, the mod inverse of e.
    print('Calculating d that is mod inverse of e...')
    d = cryptomath.findModInverse(e, totient)
    if d is None:
        raise RuntimeError('e has no inverse modulo the totient')

    # Cheap proof that the pair actually works, before anything is written to
    # disk: encrypting and decrypting a sample has to come back unchanged.
    sample = 0x1234567890ABCDEF
    if pow(pow(sample, e, n), d, n) != sample:
        raise RuntimeError('the generated key pair does not round-trip')

    publicKey = (n, e)
    privateKey = (n, d)

    print('Public key:', publicKey)
    # The private key used to be printed here as well, which puts it in the
    # terminal scrollback, in the shell history of anything that captured the
    # output, and in any CI log.
    print('Private key: <not shown>')

    return (publicKey, privateKey)


def writeKeyFile(path, keySize, modulus, exponent, private):
    """Writes one key file, keeping a private one readable only by its owner."""
    if private:
        # Created with 0600 from the start rather than written and then
        # chmod-ed: between those two calls the key is world-readable. The
        # old version used a plain open(), so it stayed that way.
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        handle = open(descriptor, 'w', encoding='utf-8')
    else:
        handle = open(path, 'x', encoding='utf-8')
    # A context manager, so the file is closed even if the write raises.
    with handle as fo:
        fo.write('%s,%s,%s' % (keySize, modulus, exponent))


def makeKeyFiles(name, keySize):
    """Creates '<name>_pubkey.txt' and '<name>_privkey.txt'."""
    publicPath = '%s_pubkey.txt' % (name,)
    privatePath = '%s_privkey.txt' % (name,)

    # Our safety check will prevent us from overwriting our old key files:
    if os.path.exists(publicPath) or os.path.exists(privatePath):
        sys.exit(
            'WARNING: The file %s or %s already exists! Use a different name '
            'or delete these files and re-run this program.' % (publicPath, privatePath)
        )

    publicKey, privateKey = generateKey(keySize)

    print()
    print('The modulus is a %s digit number and e is %s.'
          % (len(str(publicKey[0])), publicKey[1]))
    print('Writing public key to file %s...' % (publicPath,))
    writeKeyFile(publicPath, keySize, publicKey[0], publicKey[1], private=False)

    print('Writing private key to file %s (mode 0600)...' % (privatePath,))
    # This line used to report the public key's digit counts for the private
    # key, having copied the line above it.
    writeKeyFile(privatePath, keySize, privateKey[0], privateKey[1], private=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', nargs='?', default='rsa',
                        help='prefix for the key files (default: rsa)')
    parser.add_argument('--key-size', type=int, default=DEFAULT_KEY_SIZE,
                        help=f'size of the modulus in bits (default: {DEFAULT_KEY_SIZE})')
    args = parser.parse_args()

    print('Making key files...')
    makeKeyFiles(args.name, args.key_size)
    print('Key files made.')


# If generate_keys.py is run (instead of imported as a module) call
# the main() function.
if __name__ == '__main__':
    main()
