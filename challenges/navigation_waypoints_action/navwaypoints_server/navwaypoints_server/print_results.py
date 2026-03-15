#!/usr/bin/env python3
"""Print waypoint navigation results from a pickle file.

Usage:
    python3 print_results.py <path_to_pickle_file>
    python3 print_results.py  # defaults to /tmp/challenge_results/waypoint_results.pkl
"""

import sys
import os
import pickle

DEFAULT_RESULTS_FILE = '/tmp/challenge_results/waypoint_results.pkl'


def print_results(pickle_path):
    if not os.path.exists(pickle_path):
        print(f'File not found: {pickle_path}')
        sys.exit(1)

    with open(pickle_path, 'rb') as f:
        all_runs = pickle.load(f)

    if not all_runs:
        print('No runs recorded yet.')
        return

    print(f'{"="*60}')
    print(f'  WAYPOINT NAVIGATION RESULTS  ({len(all_runs)} run(s))')
    print(f'{"="*60}')

    for run_idx, run in enumerate(all_runs, start=1):
        status_str = 'SUCCESS' if run['success'] else 'FAILED/CANCELED'
        print(f'\nRun #{run_idx}  |  {run["timestamp"].strftime("%Y-%m-%d %H:%M:%S")}  |  {status_str}')
        print(f'  Total time : {run["total_time_seconds"]:.2f}s')
        print(f'  Waypoints  :')

        for wp in run['waypoints']:
            reached_str = 'REACHED' if wp['reached'] else 'NOT REACHED'
            print(
                f'    [{wp["index"]}] X={wp["point"]["x"]:.2f}  Y={wp["point"]["y"]:.2f}'
                f'  ->  {reached_str}  ({wp["time_seconds"]:.2f}s)'
            )

        reached_count = sum(1 for wp in run['waypoints'] if wp['reached'])
        print(f'  Reached {reached_count}/{len(run["waypoints"])} waypoints')

    print(f'\n{"="*60}')
    successful_runs = [r for r in all_runs if r['success']]
    if successful_runs:
        avg_total = sum(r['total_time_seconds'] for r in successful_runs) / len(successful_runs)
        best_total = min(r['total_time_seconds'] for r in successful_runs)
        print(f'  Successful runs : {len(successful_runs)}/{len(all_runs)}')
        print(f'  Best total time : {best_total:.2f}s')
        print(f'  Avg total time  : {avg_total:.2f}s')
    else:
        print(f'  No successful runs out of {len(all_runs)}.')
    print(f'{"="*60}')


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RESULTS_FILE
    print_results(path)
