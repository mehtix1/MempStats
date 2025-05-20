# MempStats
lightweight mempool analyzer
# 🧠 Bitcoin Mempool Transaction Analyzer

A command-line tool to collect and analyze recent Bitcoin transactions from the mempool using [mempool.space API](https://mempool.space/docs/api/). It supports real-time stats collection such as transaction version distribution, script type breakdown, average fees, and output values.

---

## 🚀 Features

- ⏱️ User-defined duration for data collection
- 📊 Visual pie charts for:
  - Transaction version distribution (`v1`, `v2`)
  - Output script types (e.g., `p2pkh`, `p2sh`, `v0_p2wpkh`, etc.)
- 💸 Average transaction fee computation
- 🪙 Average value of transaction outputs
- 🎨 Color-coded CLI output for clarity

---

## 📦 Requirements

Install dependencies with:

```bash
pip install requests matplotlib colorama
