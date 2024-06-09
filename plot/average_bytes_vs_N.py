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
            num_bytes = extract_bytes(filename)
            if num_bytes:
                total_packet_count = sum(num_bytes) / len(num_bytes)
                N_values.append(N*N)
                totals.append(total_packet_count)
    
    plt.figure(figsize=(10, 6))
    plt.plot(N_values, totals, marker='o')
    plt.xlabel('NxN')
    plt.ylabel('Total Bytes')
    plt.title('Total Bytes vs. NxN')
    plt.grid(True)
    plt.savefig('total_bytes.png')
    plt.show()

if __name__ == "__main__":
    main()
