<!--
Template: **Interactive Bitcoin SV Foundations**
Designed for *live* or *self-paced* learning with an emphasis on
hands-on labs, quizzes, and real-time coding challenges.
-->

# {{ course_title | default("Interactive Bitcoin SV Foundations") }}

**Duration:** {{ duration | default("2 weeks (intensive bootcamp)") }}
**Level:** Beginner → Intermediate
**Format:** 50 % live coding · 30 % quizzes · 20 % mini-projects

---

## How to Use This Template
1. Replace the `{{ … }}` placeholders programmatically.
2. The generator will inject additional modules or labs based on
   learner analytics (adaptive path).
3. Each *Lab* section is auto-linked to a Jupyter Notebook hosted on
   a Git service of your choice.

---

## Learning Path

### Module 1 · Getting Started
| Activity | Time | Description |
|----------|------|-------------|
| **Kick-off Poll** | 5 min | Gauge learner familiarity with blockchain |
| **Live Demo** | 15 min | Send 1 satoshi using HandCash *test* wallet |
| **Quiz 1** | 10 min | Five MCQs on basic terminology |

#### Lab 1.1 · Wallet Setup
* Objective: Create and fund a Regtest BSV wallet.
* Tooling: Docker + `bitcoin-sv` full node image.
* Completion Criteria: Screenshot of `listunspent` showing ≥ 5 UTXOs.

---

### Module 2 · Understanding Transactions
| Activity | Time | Description |
|----------|------|-------------|
| **Code-Along** | 20 min | Build a raw TX with `bitcoinx` Python lib |
| **Instant Feedback** | — | Auto-grader verifies scriptSig correctness |
| **Quiz 2** | 8 min | Identify parts of a UTXO |

#### Lab 2.1 · Fee Exploration
Interactive slider adjusts fee-rate and shows mempool acceptance
probability in real-time.

---

### Module 3 · On-Chain Data & Smart Contracts
| Activity | Time | Description |
|----------|------|-------------|
| **Break-out Rooms** | 15 min | Debate pros/cons of storing data on-chain |
| **Live Coding** | 25 min | Write an `OP_RETURN` inscription tool |
| **Quiz 3** | 10 min | Scenario-based decision questions |

#### Lab 3.1 · Simple Token Contract
1. Fork provided Git repo.
2. Implement missing *locking* script.
3. CI pipeline runs unit tests; green ✓ unlocks next module.

---

## Final Project · “Build & Ship”
Create a **micro-blogging dApp** that stores posts on-chain and charges
≤ 5 sats per post.

Deliverables
1. Git repo with README & screenshots.
2. Demo video (max 4 min).
3. Cost analysis (TX fees, storage, bandwidth).

---

## Assessment
* **Cumulative Quiz:** 15 questions (auto-graded).
* **Peer Review:** Evaluate another student’s dApp for UX & fee strategy.
* **Instructor Checkpoint:** Live Q&A session.

---

> **Facilitator Tips**
> • Encourage screen-sharing during labs.
> • Use breakout rooms for peer-assisted debugging.
> • Reward the fastest correct submission each day with bonus sats.

