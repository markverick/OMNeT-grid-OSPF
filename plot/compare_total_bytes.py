import os
import re
import sys
import matplotlib.pyplot as plt

def get_max_N(directory):
    N_values = []
    for entry in os.listdir(directory):
        match = re.match(r'results-(\d+)x\1', entry)
        if match:
            N_values.append(int(match.group(1)))
    return max(N_values) if N_values else None

def extract_packet_counts(filename):
    packet_counts = []
    with open(filename, 'r') as file:
        for line in file:
            match = re.match(r'scalar GridCompact\.R\[\d+\]\.ethernet encapPk:count (\d+)', line)
            if match:
                packet_counts.append(int(match.group(1)))
    return packet_counts

def extract_bytes(filename):
    num_bytes = []
    with open(filename, 'r') as file:
        for line in file:
            match = re.match(r'scalar GridCompact\.R\[\d+\]\.eth\[\d+\]\.mac txPk:sum\(packetBytes\) (\d+)', line)
            if match:
                num_bytes.append(int(match.group(1)))
                # print(int(match.group(1)))
    return num_bytes

def main():
    config = ['static', 'linkfail']
    directory = "../"
    max_N = get_max_N(directory)
    
    if max_N is None:
        print("No matching directories found.")
        return

    N_values = {}
    totals_bytes = {}
    totals_pkts = {}
    for c in config:
        N_values[c] = []
        totals_bytes[c] = []
        totals_pkts[c] = []

    for N in range(2, max_N + 1):
        for c in config:
            filename = f"../results/{N}x{N}/{c}-#0.sca"
            if os.path.isfile(filename):
                num_bytes = extract_bytes(filename)
                num_pkts = extract_packet_counts(filename)
                if num_bytes:
                    N_values[c].append(N*N)
                    total_bytes = sum(num_bytes)
                    totals_bytes[c].append(total_bytes)
                if (num_pkts):
                    total_packet_count = sum(num_pkts)
                    totals_pkts[c].append(total_packet_count)
    
    plt.figure(figsize=(10, 6))
    for c in config:
        plt.plot(N_values[c], totals_bytes[c], label=c, marker='o')
    plt.legend()
    plt.xlabel('NxN')
    plt.ylabel('Total Bytes')
    plt.title('Total Bytes vs. NxN')
    plt.grid(True)
    plt.savefig(f"total_bytes_compare.png")
    plt.show()

if __name__ == "__main__":
    main()
