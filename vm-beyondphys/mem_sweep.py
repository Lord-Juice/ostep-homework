#!/usr/bin/env python3
import argparse
import subprocess
import re
import numpy as np
import matplotlib.pyplot as plt
import sys

def measure_size(mem_exec, size_mb, loops):
    """
    Run `mem size_mb` and capture the first `loops` bandwidth reports.
    Returns: (bw0, bw_avg) in MB/s
    """
    cmd = [mem_exec, str(size_mb)]
    pat = re.compile(r'loop\s+\d+\s+in\s+[\d.]+\s*ms\s+\(bandwidth:\s*([\d.]+)\s*MB/s\)')
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, bufsize=1)
    except Exception as e:
        print(f"Error launching {cmd!r}: {e}", file=sys.stderr)
        return None, None

    bws = []
    for line in p.stdout:
        m = pat.search(line)
        if m:
            bws.append(float(m.group(1)))
            if len(bws) >= loops:
                p.terminate()
                break
    p.wait()

    if not bws:
        return None, None
    bw0 = bws[0]
    bw_avg = float(np.mean(bws[1:])) if len(bws) > 1 else bw0
    return bw0, bw_avg

def main():
    parser = argparse.ArgumentParser(
        description="Sweep mem over various sizes and plot bandwidth"
    )
    parser.add_argument('mem_executable',
                        help='Path to your mem program')
    parser.add_argument('--sizes', type=int, nargs='+', required=True,
                        help='List of sizes in MB to test')
    parser.add_argument('--loops', type=int, default=3,
                        help='How many loops to capture (first + subsequent)')
    parser.add_argument('--output', '-o',
                        help='Where to save the plot PNG (if omitted, shows on screen)')
    args = parser.parse_args()

    sizes = sorted(args.sizes)
    bw0_list = []
    bw_ss_list = []
    valid_sizes = []

    print("Measuring bandwidth for sizes:", sizes)
    for sz in sizes:
        print(f" → size={sz} MB … ", end='', flush=True)
        bw0, bwss = measure_size(args.mem_executable, sz, args.loops)
        if bw0 is None:
            print("failed")
            continue
        print(f"bw0={bw0:.1f} MB/s, steady≈{bwss:.1f} MB/s")
        valid_sizes.append(sz)
        bw0_list.append(bw0)
        bw_ss_list.append(bwss)

    if not valid_sizes:
        print("No valid measurements, aborting.", file=sys.stderr)
        sys.exit(1)

    # Plot
    plt.figure(figsize=(8,5))
    plt.plot(valid_sizes, bw_ss_list, marker='o', linestyle='-',
             label='Steady‐state bandwidth')
    plt.plot(valid_sizes, bw0_list, marker='s', linestyle='--',
             label='First‐loop bandwidth')
    plt.xlabel('Allocated memory size (MB)')
    plt.ylabel('Bandwidth (MB/s)')
    plt.title('mem: bandwidth vs. working set size')
    plt.axvline(x=8000, color='gray', linestyle=':', label='~8 GB RAM')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if args.output:
        plt.savefig(args.output, dpi=150)
        print(f"Plot saved to {args.output}")
    else:
        plt.show()

if __name__ == '__main__':
    main()
