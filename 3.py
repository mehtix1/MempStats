import requests
import time
import matplotlib.pyplot as plt
from collections import Counter
import os
import csv
import argparse
from colorama import init, Fore

init(autoreset=True)

BASE_URL = "https://mempool.space/api"

def get_recent_txids():
    url = f"{BASE_URL}/mempool/recent"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def get_transaction_details(txid):
    url = f"{BASE_URL}/tx/{txid}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

def save_transaction_to_csv(tx, filename):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "txid", "fee", "weight", "size", "version", "locktime",
                "inputs", "outputs", "input_type", "output_type"
            ])
        input_type = tx.get("vin", [{}])[0].get("prevout", {}).get("scriptpubkey_type", "unknown")
        output_type = tx.get("vout", [{}])[0].get("scriptpubkey_type", "unknown")
        writer.writerow([
            tx.get("txid", ""),
            tx.get("fee", ""),
            tx.get("weight", ""),
            tx.get("size", ""),
            tx.get("version", ""),
            tx.get("locktime", ""),
            len(tx.get("vin", [])),
            len(tx.get("vout", [])),
            input_type,
            output_type
        ])

def main(args):
    seen_txids = set()
    version_counter = Counter()
    output_type_counter = Counter()
    total_fee = 0
    total_value = 0
    tx_count = 0
    output_count = 0

    print(Fore.CYAN + f"⏳ Collecting transactions for {args.duration} seconds...")
    end_time = time.time() + args.duration

    while time.time() < end_time:
        txs = get_recent_txids()
        seen_txids.update(tx['txid'] for tx in txs)
        time.sleep(1)

    print(Fore.YELLOW + f"📦 Collected {len(seen_txids)} unique txids. Fetching details...")

    for txid in seen_txids:
        tx = get_transaction_details(txid)
        if not tx:
            continue

        version = tx.get("version", None)
        if version in [1, 2]:
            version_counter[version] += 1

        fee = tx.get("fee")
        if fee is not None:
            total_fee += fee
            tx_count += 1

        for vout in tx.get("vout", []):
            output_type = vout.get("scriptpubkey_type", "unknown")
            output_type_counter[output_type] += 1

            value = vout.get("value")
            if value is not None:
                total_value += value
                output_count += 1

    avg_fee = total_fee / tx_count if tx_count else 0
    avg_value = total_value / output_count if output_count else 0

    if args.version_stat:
        plt.figure()
        versions = [1, 2]
        counts = [version_counter.get(v, 0) for v in versions]
        plt.pie(counts, labels=[str(v) for v in versions], autopct='%1.1f%%', startangle=140)
        plt.title("Transaction Version Distribution")
        plt.axis('equal')
        plt.show()

    if args.type_stat:
        plt.figure()
        labels = list(output_type_counter.keys())
        sizes = list(output_type_counter.values())
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title("Output Script Type Distribution")
        plt.axis('equal')
        plt.show()

    if args.averagefee:
        print(Fore.GREEN + f"💸 Average transaction fee: {avg_fee:.2f} sats")

    if args.averagevalue:
        print(Fore.MAGENTA + f"🪙 Average output value: {avg_value:.2f} sats")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="📊 Bitcoin Mempool Transaction Analyzer",
        epilog="""
Examples:
  python 1.py --version_stat
  python 1.py --type_stat --averagefee
  python 1.py --averagefee --averagevalue --duration 30
""",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--version_stat', action='store_true',
                        help='Show a pie chart of transaction versions (1 and 2)')
    parser.add_argument('--type_stat', action='store_true',
                        help='Show a pie chart of output script types')
    parser.add_argument('--averagefee', action='store_true',
                        help='Display the average transaction fee (in sats)')
    parser.add_argument('--averagevalue', action='store_true',
                        help='Display the average value of transaction outputs (in sats)')
    parser.add_argument('--duration', type=int, default=20,
                        help='Duration (in seconds) to collect mempool txs (default: 20)')

    args = parser.parse_args()
    main(args)
