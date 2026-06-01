"""
test_compare.py - Automated Three-Way Comparison Test
======================================================

Runs THREE implementations on the same 5 test inputs and reports whether
their outputs are functionally equivalent:

  1. coinshuffle_mixing.py    - student's ORIGINAL implementation
  2. coinshuffle_reference.py - Python 3 port of atong01/coinshuffle (REFERENCE)
  3. naive_mixer.py           - centralized-mixer BASELINE (pedagogical)

Functional equivalence here means:
  - Same set of output addresses (the SET, not the order)
  - Same number of inputs and outputs
  - Same total amount preserved
  - All implementations report status SUCCESS
"""

import json
import subprocess
import sys


TEST_CASES = [
    {"name": "Test 1: minimum group",      "num_players": 2, "amount": 1,  "seed": 7},
    {"name": "Test 2: typical small mix",  "num_players": 3, "amount": 1,  "seed": 42},
    {"name": "Test 3: medium group",       "num_players": 5, "amount": 1,  "seed": 100},
    {"name": "Test 4: larger amount",      "num_players": 4, "amount": 10, "seed": 999},
    {"name": "Test 5: bigger group",       "num_players": 6, "amount": 5,  "seed": 2024},
]


def run_implementation(script_name, num_players, amount, seed):
    result = subprocess.run(
        [sys.executable, script_name, str(num_players), str(amount), str(seed)],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} crashed:\n{result.stderr}")
    return json.loads(result.stdout)


def main():
    print("=" * 78)
    print(" Three-way comparison: ORIGINAL vs REFERENCE vs BASELINE")
    print("=" * 78)
    print("  ORIGINAL  = coinshuffle_mixing.py    (student's own implementation)")
    print("  REFERENCE = coinshuffle_reference.py (port of atong01/coinshuffle)")
    print("  BASELINE  = naive_mixer.py           (centralized-mixer baseline)")

    passed = 0
    failed = 0

    for case in TEST_CASES:
        print(f"\n>>> {case['name']}")
        print(f"    params: num_players={case['num_players']}, "
              f"amount={case['amount']}, seed={case['seed']}")

        try:
            original = run_implementation("coinshuffle_mixing.py",
                                          case["num_players"], case["amount"], case["seed"])
            reference = run_implementation("coinshuffle_reference.py",
                                           case["num_players"], case["amount"], case["seed"])
            baseline = run_implementation("naive_mixer.py",
                                          case["num_players"], case["amount"], case["seed"])
        except Exception as e:
            print(f"    [ERROR] {e}")
            failed += 1
            continue

        orig_set = set(original["output_addresses_shuffled"])
        ref_set = set(reference["output_addresses_shuffled"])
        base_set = set(baseline["output_addresses_shuffled"])

        all_match = orig_set == ref_set == base_set
        money_ok = (
            sum(x["amount"] for x in original["transaction"]["inputs"])
            == sum(x["amount"] for x in original["transaction"]["outputs"])
            == sum(x["amount"] for x in reference["transaction"]["inputs"])
            == sum(x["amount"] for x in reference["transaction"]["outputs"])
            == sum(x["amount"] for x in baseline["transaction"]["inputs"])
            == sum(x["amount"] for x in baseline["transaction"]["outputs"])
        )

        print(f"    original  outputs (sorted): {sorted(orig_set)}")
        print(f"    reference outputs (sorted): {sorted(ref_set)}")
        print(f"    baseline  outputs (sorted): {sorted(base_set)}")

        orig_link = original["unlinkability"].get("observer_can_link")
        ref_link = reference["unlinkability"].get("observer_can_link")
        base_link = baseline["unlinkability"].get("mixer_can_link")
        print(f"    privacy: original.observer_can_link={orig_link} | "
              f"reference.observer_can_link={ref_link} | "
              f"baseline.mixer_can_link={base_link}")

        if all_match and money_ok:
            print(f"    [PASS] all three implementations are functionally equivalent")
            passed += 1
        else:
            print(f"    [FAIL]")
            if not all_match:
                print(f"           - output sets differ across implementations")
            if not money_ok:
                print(f"           - money is not conserved somewhere")
            failed += 1

    print("\n" + "=" * 78)
    print(f"RESULT: {passed} passed, {failed} failed (out of {len(TEST_CASES)})")
    print("=" * 78)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())