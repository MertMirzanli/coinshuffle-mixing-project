# CoinShuffle Mixing Protocol — Project 06

**Course:** COMP4052 — Introduction to Blockchain and DLT
**Instructor:** Osman Selvi
**Student:** Mert Mirzanli
**Term:** 2025–2026 Fall
**Project topic:** Project 06 — CoinShuffle Mixing Protocol

---

## 1. Project description

Bitcoin and most public blockchains advertise pseudo-anonymity, but every
transaction is recorded in a public ledger where input and output addresses
remain linkable. This project implements **CoinShuffle**, a decentralized
mixing protocol proposed by Ruffing, Moreno-Sanchez, and Kate (ESORICS 2014),
which breaks the link between sender and receiver addresses *without*
requiring a trusted third party.

### Goals (from the assignment brief)

- **Goal:** Break transaction traceability using coin mixing.
- **Requirements:**
  1. Implement a mixing pool *contract*.
  2. Shuffle inputs and outputs.
  3. Prevent linking sender to receiver.
- **Privacy concept:** Transaction unlinkability.

### How the implementation maps to the requirements

| Assignment requirement | Where it lives in the code |
|---|---|
| Mixing pool contract | `MixingPool` class in `coinshuffle_mixing.py` |
| Shuffle inputs and outputs | `MixingPool.shuffle_phase()` |
| Prevent linking sender → receiver | `build_onion()` + layered decryption inside `shuffle_phase()` |
| Transaction unlinkability | Demonstrated by `unlinkability_report()` and verified by `test_compare.py` |

---

## 2. Repository contents

```
coinshuffle-mixing-project/
├── coinshuffle_mixing.py    # Original implementation (the project)
├── naive_mixer.py           # Reference baseline (centralized mixer, pre-CoinShuffle era)
├── test_compare.py          # Automated 5-case comparison test
└── README.md                # This file
```

Three Python files, no other dependencies beyond the `cryptography` library.

---

## 3. Required software and dependencies

- **Python 3.10 or newer** (tested on Python 3.14 on Windows 11)
- **`cryptography` library** — used for RSA-OAEP, AES via Fernet, and RSA-PSS
  signatures

No build step, no compilation, no external services.

### Install

```bash
pip install cryptography
```

That's the only dependency.

---

## 4. Installation and run instructions

### Step 1 — Clone the repository

```bash
git clone https://github.com/MertMirzanli/coinshuffle-mixing-project.git
cd coinshuffle-mixing-project
```

### Step 2 — Install the single dependency

```bash
pip install cryptography
```

### Step 3 — Run the CoinShuffle implementation

Default run (3 players, amount 1, deterministic seed 42):

```bash
python coinshuffle_mixing.py
```

Custom run (any number of players, amount, and seed):

```bash
python coinshuffle_mixing.py <num_players> <amount> <seed>
# example:
python coinshuffle_mixing.py 5 10 100
```

### Step 4 — Run the reference baseline

```bash
python naive_mixer.py
python naive_mixer.py 5 10 100
```

### Step 5 — Run the automated comparison test

```bash
python test_compare.py
```

Expected output ends with:

```
RESULT: 5 passed, 0 failed (out of 5)
```

---

## 5. Sample input and output

### Input

The CLI accepts three positional arguments:

| Argument | Meaning | Default |
|---|---|---|
| `num_players` | Number of participants in the mixing round | 3 |
| `amount` | Coin amount each player mixes (must be equal for all) | 1 |
| `seed` | Random seed for deterministic reproduction | 42 |

### Output (truncated)

```json
{
  "status": "SUCCESS",
  "test_input": {"num_players": 3, "amount": 1, "seed": 42},
  "input_addresses": ["INPUT_001", "INPUT_002", "INPUT_003"],
  "output_addresses_shuffled": [
    "0x2a716e3e54f60c458253",
    "0x6996dc547984414cd0ad",
    "0x29a9c482a0fdd76aa0c3"
  ],
  "transaction": {
    "inputs":  [{"address": "INPUT_001", "amount": 1}, ...],
    "outputs": [{"address": "0x2a71...", "amount": 1}, ...],
    "signatures": [...]
  },
  "unlinkability": {
    "anonymity_set_size": 3,
    "possible_input_output_mappings": 6,
    "observer_can_link": false,
    "explanation": "An external observer sees 3 input addresses and 3 output
                    addresses but cannot determine which input paid which output.
                    All 6 permutations are equally likely."
  },
  "log": ["REGISTER P1 ...", "ANNOUNCE 3 players ...", "SHUFFLE step 1/3 ...", ...]
}
```

Notice that the output is fully structured JSON — this is intentional so the
result of `coinshuffle_mixing.py` and `naive_mixer.py` can be programmatically
compared (see `test_compare.py`).

---

## 6. Testing instructions

`test_compare.py` runs both implementations against five test inputs and
checks **functional equivalence**:

| Check | Pass criterion |
|---|---|
| Both runs status `SUCCESS` | Yes / No |
| Same set of output addresses | Set equality (order may differ; that's the point of mixing) |
| Same number of inputs and outputs | Counts match |
| Total amount preserved | `sum(inputs) == sum(outputs)` in both runs |

The five test cases cover:

| # | Scenario | Players | Amount | Seed |
|---|---|---|---|---|
| 1 | Minimum group | 2 | 1 | 7 |
| 2 | Typical small mix | 3 | 1 | 42 |
| 3 | Medium group | 5 | 1 | 100 |
| 4 | Larger amount | 4 | 10 | 999 |
| 5 | Bigger group | 6 | 5 | 2024 |

All five tests pass on the reference machine (Python 3.14 on Windows 11).

The test also prints the privacy difference between the two designs, e.g.:

```
privacy: coinshuffle.observer_can_link=False | naive.mixer_can_link=True
```

This is the central academic point of the project: both implementations
produce the same *set* of shuffled outputs, but only CoinShuffle hides the
input-to-output permutation from every party, including the mixer itself.

---

## 7. Reference implementation

The grading rubric requires a reference implementation to compare against.
Three sources were studied for this project:

| Source | Type | Status |
|---|---|---|
| Ruffing et al., 2014 — *CoinShuffle: Practical Decentralized Coin Mixing for Bitcoin* | Original ESORICS paper | Read in full; used as the protocol specification |
| `atong01/coinshuffle` (https://github.com/atong01/coinshuffle) | Open-source Python prototype, 2017 | **Studied** for structure, but **not runnable** on modern Python — its `requirements.txt` pins `pycrypto==2.6.1`, a package that was officially deprecated in 2018 and does not install on Python 3.10+. |
| `decred/cspp` (https://github.com/decred/cspp) | Modern production deployment | Reviewed as a real-world reference of the **CoinShuffle++** variant (DiceMix Light + DC-nets). Different protocol family, used as a contextual citation only. |

Because none of these external sources is directly runnable for an
instructor-driven side-by-side comparison, this project ships its own
runnable reference in the form of `naive_mixer.py`. This baseline implements
the **pre-CoinShuffle approach**: a centralized mixing server (the historical
state of the art represented by services like Bitcoin Fog and BitLaundry,
circa 2012–2014). It accepts the same CLI arguments and produces the same
JSON output shape, which makes empirical comparison straightforward and which
also lets the project demonstrate concretely *why* CoinShuffle was needed:

| Property | `naive_mixer.py` (pre-CoinShuffle) | `coinshuffle_mixing.py` (this project) |
|---|---|---|
| Architecture | Centralized coordinator | Fully decentralized |
| Encryption used during shuffling | None | Layered (onion) RSA-OAEP + AES |
| Trusted third party required | **Yes** | **No** |
| Mixer learns sender → receiver mapping | **Yes** (full permutation stored) | **No** (nobody has the full mapping) |
| External observer learns mapping | No | No |
| Funds at risk from a malicious mixer | **Yes** | No (all participants must sign) |

Running both files on the same seed produces the same *set* of output
addresses (functional equivalence), but their `unlinkability` reports
differ — see `test_compare.py` output.

---

## 8. Cryptographic primitives used

| Primitive | Where | Why this choice |
|---|---|---|
| RSA-2048 with OAEP padding | Layered encryption of output addresses | Standard public-key encryption supporting OAEP, well-supported in `cryptography` |
| AES-128 (via Fernet) | Hybrid encryption payload | RSA alone has a small message-size limit; AES handles arbitrary payload sizes inside RSA-encrypted envelopes |
| RSA-PSS with SHA-256 | Transaction signatures | Modern, provably secure RSA signature scheme (replaces older PKCS#1 v1.5) |
| SHA-256 | Output address derivation | Standard cryptographic hash |

The Ruffing et al. paper uses ECDSA (secp256k1) and ECIES because they target
Bitcoin specifically. This project uses RSA-based equivalents because:

1. The privacy properties are identical (layered public-key encryption +
   signed transactions); only the underlying curve / algebra differs.
2. The `cryptography` library's RSA support is more stable cross-platform than
   its secp256k1 support, and this project is meant to be runnable by the
   instructor on any modern OS without compilation.

---

## 9. What this implementation does *not* do (scope)

The assignment brief lists three concrete requirements (mixing pool
contract, shuffle inputs/outputs, prevent sender → receiver linking). The
project sticks to that scope. Deliberately *not* included:

- **Blame phase** for malicious participants (paper §3.4). Would add ~100
  lines of equivocation detection and cryptographic accusations. Out of
  scope for this assignment.
- **On-chain integration.** No real Bitcoin or Ethereum interaction; the
  protocol runs in-process and produces a JSON "transaction" object that
  represents what would be broadcast.
- **Network protocol.** No TCP/socket layer; players are simulated in the
  same Python process. The cryptography and protocol logic are identical to
  what a real distributed deployment would do.
- **Solidity smart contract.** CoinShuffle was designed for Bitcoin (which
  has no general-purpose smart contracts), and its core privacy mechanism
  must execute *off-chain* — running layered encryption on-chain would
  publish all ciphertexts and break unlinkability.

---

## 10. Submission information

- **Personal repository (this one):** https://github.com/MertMirzanli/coinshuffle-mixing-project
- **Course repository branch:** `students/<student-branch>/06-coinshuffle-mixing` on https://github.com/OsmanSelvi84/blockchain-privacy-projects (to be pushed after this version is finalized).

---

## 11. References

1. Ruffing, T., Moreno-Sanchez, P., Kate, A. (2014). *CoinShuffle: Practical
   Decentralized Coin Mixing for Bitcoin.* ESORICS 2014.
2. Chaum, D. (1981). *Untraceable Electronic Mail, Return Addresses, and
   Digital Pseudonyms.* Communications of the ACM, 24(2). — original
   decryption mix network on which CoinShuffle is built.
3. Maxwell, G. (2013). *CoinJoin: Bitcoin privacy for the real world.* —
   predecessor design that CoinShuffle improves upon.
4. `atong01/coinshuffle` — https://github.com/atong01/coinshuffle (studied
   reference, not runnable on modern Python).
5. `decred/cspp` — https://github.com/decred/cspp (modern CoinShuffle++
   reference).
