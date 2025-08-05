<!--
Template: **Basic Bitcoin SV Course**
This scaffold is filled in automatically by the generator; keep the
place-holders (`{{ … }}`) intact so Jinja / f-string style substitution
works.  Lines that start with <!-- comments are ignored when rendering.
-->

# {{ course_title | default("Bitcoin SV Basics") }}

**Duration:** {{ duration | default("4 weeks") }}
**Level:** Beginner
**Prerequisites:** None – ideal for absolute newcomers

---

## Course Overview
Welcome to *Bitcoin SV Basics*. By the end of this course you will:

1. Understand what the Bitcoin SV blockchain is and why it exists.
2. Be able to send and verify a simple BSV transaction.
3. Explain UTXO, miners, blocks, and fees in plain language.
4. Identify real-world use-cases uniquely suited to BSV.

---

## Module 1  Introduction to Bitcoin SV
### Lesson 1.1  Genesis and Philosophy
- Origins of Bitcoin – the Satoshi Vision
- Fork history (BTC → BCH → BSV)
- *Discussion:* Does protocol stability matter?

### Lesson 1.2  Key Concepts
- Satoshis, Addresses, and Keys
- Proof-of-Work recap
- The role of miners vs. nodes

---

## Module 2  Transactions in Practice
### Lesson 2.1  Anatomy of a BSV Transaction
- Inputs, Outputs, and Scripts
- **Code Lab:** Build and broadcast a testnet TX

### Lesson 2.2  Fees & Economics
- Why micro-fees matter
- Fee calculation walkthrough

---

## Module 3  Exploring the Blockchain
### Lesson 3.1  Block Structure
- Header fields
- Merkle roots
- *Exercise:* Inspect a recent block

### Lesson 3.2  Simple Payment Verification
- SPV nodes vs. full nodes
- Bloom filters & payment channels

---

## Module 4  Real-World Applications
### Lesson 4.1  Data on-chain
- `OP_RETURN` basics
- Use-cases: Certificates, Supply-chain, NFTs

### Lesson 4.2  BSV Ecosystem Overview
- Wallets (HandCash, Centi, RelayX)
- SDKs & APIs (BSV SDK, Merchant API)
- Major enterprise projects

---

## Assessment
1. **Quiz:** 10 MCQs covering Modules 1-4.
2. **Practical:** Broadcast a mainnet transaction worth 1 sat.
3. **Reflection:** Write 300 words on a compelling BSV use-case.

---

## Capstone Project
Design a *micro-payment* web service that charges ≤ 10 sats per request.
Deliverables:
- System overview diagram
- Smart-contract or server-side code snippet
- Business value statement (½ page)

---

> **Instructor note:**
> Feel free to extend any section with extra examples, region-specific
> regulations, or localised resources before publishing.
