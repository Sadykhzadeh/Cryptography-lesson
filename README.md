# Cryptography lesson

Worked examples for a cryptography lesson: primality testing, modular
arithmetic and RSA key generation. Python 3.9 or newer, standard library only
— nothing to install.

```sh
python -m unittest -v        # 32 tests over everything here
```

The slides are `Presentation.pptx` / `Presnetation.pdf`.

## The files

| File | What it shows |
| --- | --- |
| `prime_check_native.py` | Primality by trying every divisor up to `n - 1`. |
| `prime_check_smart.py` | The same, stopping at `sqrt(n)` — a divisor above the root is always paired with one below it. |
| `eratosthenes_sieve.py` | The sieve of Eratosthenes: every prime up to `n` at once. |
| `fermat_primality_test.py` | Fermat's test, and where it fails. |
| `congruences.py` | Whether two integers are congruent modulo a divisor. |
| `modular_exponentiation.py` | Exponentiation by squaring, with and without a modulus, plus a brute-force discrete log. |
| `mod_finding.cpp` | `(a^b) % n` in C++. Build with `g++ -std=c++17 -O2 mod_finding.cpp -o mod_finding`. |
| `primeNum.py` | Miller-Rabin, and generating a prime of a given bit width. |
| `cryptomath.py` | Euclid's algorithm, extended Euclid, modular inverse. |
| `generate_keys.py` | RSA key generation on top of the two modules above. |

`primeNum.py` and `cryptomath.py` are new. `generate_keys.py` imported both and
neither existed here, so it could not be run at all.

Most files run on their own and print a short demonstration:

```sh
python primeNum.py
python cryptomath.py
python fermat_primality_test.py
python generate_keys.py mykey --key-size 2048
```

## Two things worth taking away

### Fermat's test has a blind spot; Miller-Rabin does not

A Carmichael number is composite but satisfies Fermat's congruence for every
base coprime to it, so Fermat's test can only catch one by stumbling onto a
base that shares a factor. `python fermat_primality_test.py` measures it: with
`k = 5` rounds over 200 runs, 561 (= 3·11·17), 1105 and 1729 are each called
prime a good fraction of the time.

That is why `primeNum.py` uses Miller-Rabin to generate RSA primes. Every
round rejects a composite with probability at least 3/4, independently, so 40
rounds leave a false positive far less likely than the hardware getting the
arithmetic wrong.

### Reducing late overflows

`mod_finding.cpp` used `int` and took the modulus once at the end.
`123456789^13 mod 1000000007` came out as `-405786624` instead of `354411480`.
Widening to `int64_t` is not enough either: with a modulus near 2^32 the
product of two values below it still overflows, which is why the
multiplication there doubles rather than multiplies.

## Key generation

`generate_keys.py` writes `<name>_pubkey.txt` and `<name>_privkey.txt`, each
holding `keySize,modulus,exponent`.

- `keySize` is the size of the **modulus**, so `p` and `q` get half each. The
  previous version asked for two 1024-bit primes — a 2048-bit modulus — and
  then wrote `1024` into the file as the size.
- The private key file is created with mode `0600`, and the private exponent
  is not printed. It used to go to standard output, and from there into
  terminal scrollback and any log that captured it.
- Randomness comes from `secrets`, not `random`. A Mersenne Twister's output
  can be reconstructed from enough of it, which for key material means the
  key can be.
- `p` and `q` are checked to differ. `p == q` gives `n = p²`, whose factors
  fall out of a square root.
- `e` is 65537 unless that shares a factor with the totient. The previous
  version drew `e` at random from `[2^(keySize-1), 2^keySize)`, which is valid
  but leaves every encryption doing a full-width exponentiation for nothing.
- The pair is checked to round-trip before anything is written.

None of which makes this a production RSA implementation. It has no padding,
so it is textbook RSA — deterministic, malleable, and not safe for real
messages. Use your platform's library for that.
