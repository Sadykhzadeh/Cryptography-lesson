"""Tests for the lesson code. Standard library only: python -m unittest -v

Several of these exist because the function they cover used to get the answer
wrong, not because the answer was ever in doubt.
"""

import contextlib
import io
import math
import os
import subprocess
import sys
import tempfile
import unittest
from math import isqrt

import congruences
import cryptomath
import eratosthenes_sieve
import fermat_primality_test
import generate_keys
import modular_exponentiation
import primeNum
import prime_check_native
import prime_check_smart

HERE = os.path.dirname(os.path.abspath(__file__))
LIMIT = 2000

# Carmichael numbers: composite, but they satisfy Fermat's congruence for
# every base coprime to them.
CARMICHAEL = (561, 1105, 1729, 2465, 2821, 6601, 8911)


def referenceIsPrime(n):
    """Deliberately dull, so it can be trusted."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    return all(n % i for i in range(3, isqrt(n) + 1, 2))


class PrimalityTests(unittest.TestCase):
    def test_every_implementation_agrees_with_the_reference(self):
        implementations = {
            'prime_check_native': prime_check_native.isPrime,
            'prime_check_smart': prime_check_smart.isPrime,
            'congruences': congruences.isPrime,
            'primeNum': primeNum.isPrime,
        }
        for name, isPrime in implementations.items():
            with self.subTest(implementation=name):
                for n in range(-20, LIMIT):
                    self.assertEqual(
                        isPrime(n), referenceIsPrime(n),
                        f'{name}.isPrime({n}) disagrees',
                    )

    def test_the_numbers_congruences_used_to_call_prime(self):
        # The loop variable was unused and the body tested `a % 2`, so every
        # odd composite came back prime.
        for n in (9, 15, 21, 25, 49, 121, 169):
            self.assertFalse(congruences.isPrime(n), f'{n} is not prime')

    def test_nothing_below_two_is_prime(self):
        for isPrime in (prime_check_native.isPrime, prime_check_smart.isPrime,
                        congruences.isPrime, primeNum.isPrime):
            for n in (-7, -1, 0, 1):
                self.assertFalse(isPrime(n), f'{isPrime.__module__}({n})')

    def test_a_negative_does_not_raise(self):
        # prime_check_smart used to call sqrt() on it: ValueError, math
        # domain error.
        for n in (-1, -5, -10 ** 6):
            self.assertFalse(prime_check_smart.isPrime(n))

    def test_miller_rabin_rejects_carmichael_numbers(self):
        for n in CARMICHAEL:
            self.assertFalse(primeNum.isPrime(n), f'{n} is composite')

    def test_fermat_handles_small_and_negative_input(self):
        # random.randint(2, n - 2) had an empty range below n = 4.
        for n in (-7, -1, 0, 1, 4):
            self.assertFalse(fermat_primality_test.isPrime(n, 5))
        for n in (2, 3, 5, 7, 11):
            self.assertTrue(fermat_primality_test.isPrime(n, 5))

    def test_fermat_never_rejects_an_actual_prime(self):
        # One direction of the test is exact: a prime always passes.
        for n in range(2, 500):
            if referenceIsPrime(n):
                self.assertTrue(fermat_primality_test.isPrime(n, 10), n)


class SieveTests(unittest.TestCase):
    def test_it_matches_the_reference(self):
        for limit in list(range(0, 60)) + [LIMIT]:
            with self.subTest(limit=limit):
                sieve = eratosthenes_sieve.eratosthenes(limit)
                for n in range(limit + 1):
                    self.assertEqual(sieve[n], referenceIsPrime(n), f'{n} of {limit}')

    def test_a_limit_below_two_does_not_raise(self):
        # `sieve[1] = 0` was unconditional: IndexError for a limit of 0.
        for limit in (0, 1):
            self.assertNotIn(True, eratosthenes_sieve.eratosthenes(limit))


class ModularArithmeticTests(unittest.TestCase):
    def test_power_matches_the_operator(self):
        for x in range(-5, 6):
            for y in range(0, 12):
                self.assertEqual(modular_exponentiation.power(x, y), x ** y)

    def test_power_and_mod_matches_pow(self):
        for x in range(1, 40):
            for y in range(0, 25):
                for p in (1, 2, 7, 13, 97):
                    self.assertEqual(
                        modular_exponentiation.powerAndMod(x, y, p),
                        pow(x, y, p),
                    )

    def test_fermat_power_matches_pow(self):
        for a in range(1, 30):
            for n in range(0, 20):
                for p in (1, 3, 11, 101):
                    self.assertEqual(fermat_primality_test.power(a, n, p), pow(a, n, p))

    def test_find_power_finds_the_smallest_exponent(self):
        for a, n in ((3, 13), (2, 11), (5, 23)):
            for i in range(n):
                target = pow(a, i, n)
                found = modular_exponentiation.findPower(a, target, n)
                self.assertIsNotNone(found)
                self.assertEqual(pow(a, found, n), target)
                self.assertLessEqual(found, i)

    def test_find_power_says_so_when_there_is_none(self):
        self.assertIsNone(modular_exponentiation.findPower(3, 4, 13))


class CryptomathTests(unittest.TestCase):
    def test_gcd_matches_math_gcd(self):
        for a in range(-30, 31):
            for b in range(-30, 31):
                self.assertEqual(cryptomath.gcd(a, b), math.gcd(a, b), f'{a},{b}')

    def test_extended_gcd_satisfies_bezout(self):
        for a in range(1, 60):
            for b in range(1, 60):
                g, x, y = cryptomath.extendedGcd(a, b)
                self.assertEqual(g, math.gcd(a, b))
                self.assertEqual(a * x + b * y, g, f'{a},{b}')

    def test_mod_inverse_is_an_inverse(self):
        for m in range(2, 60):
            for a in range(1, m):
                inverse = cryptomath.findModInverse(a, m)
                if math.gcd(a, m) == 1:
                    self.assertIsNotNone(inverse, f'{a} mod {m}')
                    self.assertEqual((a * inverse) % m, 1, f'{a} mod {m}')
                else:
                    # Returning a wrong d here would produce a key pair that
                    # cannot decrypt what it encrypts.
                    self.assertIsNone(inverse, f'{a} mod {m} should have none')


class PrimeGenerationTests(unittest.TestCase):
    def test_generated_primes_have_the_requested_width(self):
        for keysize in (16, 32, 64, 128):
            prime = primeNum.generateLargePrime(keysize)
            self.assertEqual(prime.bit_length(), keysize)
            self.assertTrue(referenceIsPrime(prime) if prime < 10 ** 7 else primeNum.isPrime(prime))

    def test_a_tiny_keysize_is_refused(self):
        with self.assertRaises(ValueError):
            primeNum.generateLargePrime(8)

    def test_generated_primes_differ(self):
        primes = {primeNum.generateLargePrime(64) for _ in range(8)}
        self.assertGreater(len(primes), 1)


class KeyGenerationTests(unittest.TestCase):
    """generateKey prints its progress, which is the lesson's point but makes
    for noisy test output, so it is captured."""

    @staticmethod
    @contextlib.contextmanager
    def quiet():
        with contextlib.redirect_stdout(io.StringIO()):
            yield
    def test_the_key_pair_round_trips(self):
        # 64 bits is far too small to be secure and plenty to be correct.
        with self.quiet():
            (n, e), (modulus, d) = generate_keys.generateKey(64)
        self.assertEqual(n, modulus)
        for message in (0, 1, 2, 42, 1234567, n - 1):
            self.assertEqual(pow(pow(message, e, n), d, n), message % n)

    def test_an_odd_or_tiny_keysize_is_refused(self):
        for keysize in (31, 16, 0):
            with self.assertRaises(ValueError), self.quiet():
                generate_keys.generateKey(keysize)

    def test_the_private_key_file_is_not_world_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            name = os.path.join(directory, 'sample')
            with self.quiet():
                generate_keys.makeKeyFiles(name, 64)
            private = f'{name}_privkey.txt'
            self.assertTrue(os.path.exists(private))
            if os.name != 'nt':
                # Windows does not carry POSIX mode bits.
                mode = os.stat(private).st_mode & 0o777
                self.assertEqual(mode, 0o600, f'mode was {oct(mode)}')

    def test_it_refuses_to_overwrite_existing_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            name = os.path.join(directory, 'sample')
            with self.quiet():
                generate_keys.makeKeyFiles(name, 64)
            with self.assertRaises(SystemExit), self.quiet():
                generate_keys.makeKeyFiles(name, 64)

    def test_the_private_key_is_not_printed(self):
        with open(os.path.join(HERE, 'generate_keys.py'), encoding='utf-8') as handle:
            source = handle.read()
        self.assertNotIn("print('Private key:', privateKey)", source)


class ScriptTests(unittest.TestCase):
    """The interactive scripts, driven through stdin."""

    def run_script(self, script, stdin):
        return subprocess.run(
            [sys.executable, os.path.join(HERE, script)],
            input=stdin, capture_output=True, text=True, timeout=120, cwd=HERE,
        )

    def test_the_prime_range_scripts_agree(self):
        expected = [n for n in range(1, 51) if referenceIsPrime(n)]
        for script in ('prime_check_native.py', 'prime_check_smart.py',
                       'eratosthenes_sieve.py'):
            with self.subTest(script=script):
                result = self.run_script(script, '1 50\n')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f'Primes: {expected}', result.stdout)

    def test_the_prime_range_scripts_survive_an_empty_range(self):
        for script in ('prime_check_native.py', 'prime_check_smart.py',
                       'eratosthenes_sieve.py'):
            with self.subTest(script=script):
                result = self.run_script(script, '0 0\n')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('Primes: []', result.stdout)

    def test_the_prime_range_scripts_ask_again_on_bad_input(self):
        for script in ('prime_check_native.py', 'prime_check_smart.py',
                       'eratosthenes_sieve.py'):
            with self.subTest(script=script):
                result = self.run_script(script, 'not numbers\n2 10\n')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('Primes: [2, 3, 5, 7]', result.stdout)

    def test_congruences_reports_both_answers(self):
        result = self.run_script('congruences.py', '17 5\n4\n9\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        # 17 % 4 == 1 and 5 % 4 == 1
        self.assertIn('17 and 5 are congruent when divided by 4', result.stdout)
        self.assertIn('9 is not a prime number', result.stdout)

    def test_congruences_refuses_a_zero_divisor(self):
        result = self.run_script('congruences.py', '17 5\n0\n4\n7\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('divisor cannot be zero', result.stdout)
        self.assertIn('7 is a prime number', result.stdout)


def findCppCompiler():
    import shutil
    for candidate in ('g++', 'clang++'):
        path = shutil.which(candidate)
        if path:
            return path
    return None


@unittest.skipIf(findCppCompiler() is None, 'no C++ compiler on PATH')
class ModFindingCppTests(unittest.TestCase):
    """mod_finding.cpp, compiled and compared against pow()."""

    binary = None
    directory = None

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.binary = os.path.join(cls.directory.name, 'mod_finding')
        result = subprocess.run(
            [findCppCompiler(), '-std=c++17', '-O2', '-Wall', '-Wextra',
             '-Wpedantic', '-Werror',
             os.path.join(HERE, 'mod_finding.cpp'), '-o', cls.binary],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            cls.directory.cleanup()
            raise AssertionError(f'mod_finding.cpp did not compile:\n{result.stderr}')

    @classmethod
    def tearDownClass(cls):
        if cls.directory:
            cls.directory.cleanup()

    def run_binary(self, text):
        return subprocess.run([self.binary], input=text, capture_output=True,
                              text=True, timeout=120)

    def test_it_agrees_with_pow(self):
        cases = [
            (2, 10, 1000), (3, 5, 7), (5, 0, 7), (7, 0, 7), (2, 1, 1),
            (10, 3, 999983),
            # A 30-bit modulus: the original overflowed its int here and
            # answered -405786624.
            (123456789, 13, 1000000007),
            # A 32-bit modulus: this overflows a 64-bit product too, which is
            # why the multiplication doubles instead.
            (65537, 65536, 4294967291),
            (999999999999, 999, 1000000000039),
            (4611686018427387847, 12345, 4611686018427387903),
            (-5, 3, 7),
        ]
        for a, b, n in cases:
            with self.subTest(a=a, b=b, n=n):
                result = self.run_binary(f'{a} {b} {n}\n')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(int(result.stdout.strip()), pow(a, b, n))

    def test_it_refuses_bad_input(self):
        # `int s;` went uninitialised when b was below 2, and nothing checked
        # the modulus at all.
        for text in ('5 3 0\n', '5 3 -7\n', '5 -3 7\n', 'not numbers\n', '\n'):
            with self.subTest(text=text.strip()):
                result = self.run_binary(text)
                self.assertEqual(result.returncode, 1, f'stdout: {result.stdout}')
                self.assertTrue(result.stderr.strip(), 'said nothing about why')


if __name__ == '__main__':
    unittest.main(verbosity=2)
