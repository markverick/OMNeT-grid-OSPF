import os
import re
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

def main():
    directory = "../"
    max_N = get_max_N(directory)
    
    if max_N is None:
        print("No matching directories found.")
        return

    N_values = []
    totals = []

    for N in range(1, max_N + 1):
        filename = f"../results-{N}x{N}/General-#0.sca"
        if os.path.isfile(filename):
            packet_counts = extract_packet_counts(filename)
            if packet_counts:
                total_packet_count = sum(packet_counts)
                N_values.append(N)
                totals.append(total_packet_count)
    
    plt.figure(figsize=(10, 6))
    plt.plot(N_values, totals, marker='o')
    plt.xlabel('N')
    plt.ylabel('Total Packet Count')
    plt.title('Total Packet Count vs. N')
    plt.grid(True)
    plt.savefig('total_packet_count.png')
    plt.show()

if __name__ == "__main__":
    main()
