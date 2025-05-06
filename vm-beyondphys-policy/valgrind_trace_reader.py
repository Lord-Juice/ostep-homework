import matplotlib.pyplot as plt
from collections import OrderedDict
import os
import sys

def parse_trace(file_path, page_size=4096):
    page_refs = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('=='):
                continue  # Skip Valgrind metadata
            parts = line.split()
            if len(parts) == 2:
                addr_str = parts[1].split(',')[0]
                try:
                    addr = int(addr_str, 16)
                    page_num = addr // page_size
                    page_refs.append(page_num)
                except ValueError:
                    continue
    return page_refs


def simulate_lru(page_refs, cache_size):
    cache = OrderedDict()
    hits = 0
    for page in page_refs:
        if page in cache:
            hits += 1
            cache.move_to_end(page)  # Update LRU
        else:
            if len(cache) >= cache_size:
                cache.popitem(last=False)  # Remove LRU page
            cache[page] = True
    return hits, len(page_refs) - hits

def run_simulation(trace_file):
    if not os.path.isfile(trace_file):
        print(f"❌ Error: File '{trace_file}' not found.")
        sys.exit(1)

    page_refs = parse_trace(trace_file)
    cache_sizes = [2**i for i in range(0, 12)]  # Cache sizes from 1 to 2048
    hit_rates = []

    for size in cache_sizes:
        hits, misses = simulate_lru(page_refs, size)
        total = hits + misses
        hit_rate = hits / total if total > 0 else 0
        hit_rates.append(hit_rate)
        print(f"Cache size {size:4d}: Hit rate = {hit_rate:.2%}")

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(cache_sizes, hit_rates, marker='o')
    plt.xscale('log', base=2)
    plt.xlabel('Cache Size (in pages)')
    plt.ylabel('Hit Rate')
    plt.title('Working Set Behavior of Application')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("out.png")
    print("✅ Plot saved as 'out.png'.")

# Run
if __name__ == "__main__":
    run_simulation("trace.out")
