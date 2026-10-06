// Computes (a^b) % n by squaring.
//
// Reads a, b and n on standard input and prints the result.

#include <cstdint>
#include <iostream>
#include <limits>

namespace {

// The largest modulus the fallback multiplication below can take without
// overflowing: it adds two values below n, so 2n has to fit in an int64_t.
constexpr std::int64_t kMaxModulus = std::numeric_limits<std::int64_t>::max() / 2;

// (a * b) % n without overflowing on the way.
//
// Reducing after a plain a * b is not enough: with a modulus near 2^32 the
// product of two values below it already overflows a 64-bit integer, and the
// answer comes out wrong rather than merely large - 65537^65536 mod
// 4294967291 is 842477647, and an int64_t multiplication answers 1214198697.
//
// This doubles instead of multiplying, so no intermediate exceeds 2n. The
// obvious alternative, unsigned __int128, is a compiler extension that
// -Wpedantic rejects and MSVC does not have; a handful of extra additions is
// a better trade for a lesson than a non-standard type.
std::int64_t mulmod(std::int64_t a, std::int64_t b, std::int64_t n) {
    std::int64_t result = 0;
    a %= n;
    while (b > 0) {
        if (b & 1) {
            result = (result + a) % n;
        }
        a = (a + a) % n;
        b >>= 1;
    }
    return result;
}

}  // namespace

int main() {
    std::int64_t a, b, n;
    if (!(std::cin >> a >> b >> n)) {
        std::cerr << "expected three integers: a b n\n";
        return 1;
    }
    if (n <= 0) {
        // Every line below divides by n, and a negative modulus is not a
        // modulus.
        std::cerr << "n must be positive\n";
        return 1;
    }
    if (n > kMaxModulus) {
        std::cerr << "n must be at most " << kMaxModulus << "\n";
        return 1;
    }
    if (b < 0) {
        std::cerr << "b must not be negative\n";
        return 1;
    }

    // The original built a std::map<int,int> of successive squares and then
    // walked back down it. Four things went wrong with that:
    //
    //   * int everywhere. arr[i/2]*arr[i/2] with a modulus above about 46341
    //     overflows a 32-bit int, which is undefined behaviour and in
    //     practice a wrong answer: 123456789^13 mod 1000000007 came out as
    //     -405786624 instead of 354411480.
    //   * `mod *= arr[i]` accumulated the whole product and took the modulus
    //     once at the end, so it overflowed too - 65537^65536 mod 4294967291
    //     answered 0.
    //   * `int s;` was left uninitialised and only assigned inside the first
    //     loop, which does not run for b below 2; the second loop then
    //     started from whatever was on the stack.
    //   * No table is needed at all. Squaring as it goes uses no memory and
    //     reduces at every step.
    std::int64_t base = ((a % n) + n) % n;  // keep it non-negative
    std::int64_t result = 1 % n;            // 1 % 1 is 0, which is correct

    while (b > 0) {
        if (b & 1) {
            result = mulmod(result, base, n);
        }
        base = mulmod(base, base, n);
        b >>= 1;
    }

    std::cout << result << '\n';
    return 0;
}
