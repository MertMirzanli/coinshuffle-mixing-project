"""
test_compare.py - Automated Comparison Test
============================================

Runs both implementations on the same 5 test inputs and reports whether the
outputs are functionally equivalent.

Functional equivalence here means:
  - Same set of output addresses (the SET, not the order)
  - Same number of inputs and outputs
  - Same total amount preserved
  - Both implementations report status SUCCESS

The order of output addresses is allowed to differ, because that is precisely
the whole point of mixing: a random permutation is applied. What matters is
that the same coins end up at the same set of new addresses.

Usage:
    python test_compare.py
"""

import json
import subprocess
import sys


# The 5 test cases the instructor might give. We pick a variety:
#  - small group (2 players, the minimum)
#  - typical group (3 players)
#  - bigger groups
#  - varying amounts
#  - varying seeds
TEST_CASES = [
    {"name": "Test 1: minimum group",      "num_players": 2, "amount": 1,  "seed": 7},
    {"name": "Test 2: typical small mix",  "num_players": 3, "amount": 1,  "seed": 42},
    {"name": "Test 3: medium group",       "num_players": 5, "amount": 1,  "seed": 100},
    {"name": "Test 4: larger amount",      "num_players": 4, "amount": 10, "seed": 999},
    {"name": "Test 5: bigger group",       "num_players": 6, "amount": 5,  "seed": 2024},
]


def run_implementation(script_name, num_players, amount, seed):
    """Run one implementation and return its parsed JSON output."""
    result = subprocess.run(
        [sys.executable, script_name, str(num_players), str(amount), str(seed)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} crashed:\n{result.stderr}")
    return json.loads(result.stdout)


def compare(coin_result, naive_result):
    """Compare two results. Returns (passed: bool, reasons: list[str])."""
    reasons = []

    # 1) Both must have status SUCCESS
    if coin_result.get("status") != "SUCCESS":
        reasons.append(f"coinshuffle status = {coin_result.get('status')}")
    if naive_result.get("status") != "SUCCESS":
        reasons.append(f"naive status = {naive_result.get('status')}")

    # 2) Same set of output addresses (order doesn't matter)
    coin_outputs = set(coin_result.get("output_addresses_shuffled", []))
    naive_outputs = set(naive_result.get("output_addresses_shuffled", []))
    if coin_outputs != naive_outputs:
        only_coin = coin_outputs - naive_outputs
        only_naive = naive_outputs - coin_outputs
        if only_coin:
            reasons.append(f"only in coinshuffle: {only_coin}")
        if only_naive:
            reasons.append(f"only in naive: {only_naive}")

    # 3) Same number of inputs/outputs
    if len(coin_result["input_addresses"]) != len(naive_result["input_addresses"]):
        reasons.append("input counts differ")
    if len(coin_result["output_addresses_shuffled"]) != len(
        naive_result["output_addresses_shuffled"]
    ):
        reasons.append("output counts differ")

    # 4) Total amount preserved in both transactions
    coin_in_total = sum(x["amount"] for x in coin_result["transaction"]["inputs"])
    coin_out_total = sum(x["amount"] for x in coin_result["transaction"]["outputs"])
    naive_in_total = sum(x["amount"] for x in naive_result["transaction"]["inputs"])
    naive_out_total = sum(x["amount"] for x in naive_result["transaction"]["outputs"])
    if coin_in_total != coin_out_total:
        reasons.append(f"coinshuffle conserves money? in={coin_in_total} out={coin_out_total}")
    if naive_in_total != naive_out_total:
        reasons.append(f"naive conserves money? in={naive_in_total} out={naive_out_total}")
    if coin_in_total != naive_in_total:
        reasons.append("input totals differ between implementations")

    return (len(reasons) == 0, reasons)


def main():
    print("=" * 70)
    print("CoinShuffle vs Naive Mixer - Automated Comparison Test")
    print("=" * 70)

    passed = 0
    failed = 0

    for case in TEST_CASES:
        print(f"\n>>> {case['name']}")
        print(f"    params: num_players={case['num_players']}, "
              f"amount={case['amount']}, seed={case['seed']}")

        try:
            coin = run_implementation("coinshuffle_mixing.py",
                                      case["num_players"], case["amount"], case["seed"])
            naive = run_implementation("naive_mixer.py",
                                       case["num_players"], case["amount"], case["seed"])
        except Exception as e:
            print(f"    [ERROR] {e}")
            failed += 1
            continue

        ok, reasons = compare(coin, naive)

        # Pretty-print both output address sets for visual inspection
        coin_outs = sorted(coin["output_addresses_shuffled"])
        naive_outs = sorted(naive["output_addresses_shuffled"])
        print(f"    coinshuffle outputs (sorted): {coin_outs}")
        print(f"    naive outputs       (sorted): {naive_outs}")

        # Show the privacy difference - this is the whole point
        coin_link = coin["unlinkability"].get("observer_can_link")
        naive_link = naive["unlinkability"].get("mixer_can_link")
        print(f"    privacy: coinshuffle.observer_can_link={coin_link} | "
              f"naive.mixer_can_link={naive_link}")

        if ok:
            print(f"    [PASS] functional equivalence verified")
            passed += 1
        else:
            print(f"    [FAIL] reasons:")
            for r in reasons:
                print(f"           - {r}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULT: {passed} passed, {failed} failed (out of {len(TEST_CASES)})")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
