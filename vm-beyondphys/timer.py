#!/usr/bin/env python3
import argparse
import subprocess
import re
import matplotlib.pyplot as plt
import sys

def main():
    parser = argparse.ArgumentParser(
        description='Run mem and plot its per-loop times.'
    )
    parser.add_argument('mem_executable',
                        help='Path to your compiled mem program')
    parser.add_argument('size_mb', type=int,
                        help='Memory size argument to pass (in MB)')
    parser.add_argument('--loops', type=int, default=None,
                        help='Number of loops to capture before exiting')
    parser.add_argument('--output', '-o',
                        help='Filename to save the plot (e.g. times.png). '
                             'If omitted, the plot is shown interactively.')
    args = parser.parse_args()

    # Start the mem process
    cmd = [args.mem_executable, str(args.size_mb)]
    try:
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                bufsize=1)
    except FileNotFoundError:
        print(f"Error: cannot find executable {args.mem_executable}", file=sys.stderr)
        sys.exit(1)

    times = []
    loops = []
    # Regex to match lines like: "loop 3 in 52.13 ms"
    pat = re.compile(r'loop\s+(\d+)\s+in\s+([\d.]+)\s*ms')

    try:
        for line in proc.stdout:
            print(line, end='')  # echo the mem output
            m = pat.search(line)
            if m:
                loop_idx = int(m.group(1))
                t_ms = float(m.group(2))
                loops.append(loop_idx)
                times.append(t_ms)
                if args.loops and len(times) >= args.loops:
                    proc.terminate()
                    break
    except KeyboardInterrupt:
        proc.terminate()
    finally:
        proc.wait()

    if not times:
        print("No timing data was captured.", file=sys.stderr)
        sys.exit(1)

    # Plotting
    plt.figure(figsize=(8, 4))
    plt.plot(loops, times, marker='o', linestyle='-')
    plt.xlabel('Loop #')
    plt.ylabel('Time per loop (ms)')
    plt.title(f'Per-Loop Times for mem {args.size_mb} MB')
    plt.grid(True)
    plt.tight_layout()

    if args.output:
        plt.savefig(args.output)
        print(f"Plot saved to {args.output}")
    else:
        plt.show()

if __name__ == '__main__':
    main()
