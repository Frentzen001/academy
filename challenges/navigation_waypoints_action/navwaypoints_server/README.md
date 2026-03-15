# navwaypoints_server

## Results

Navigation results are saved to `/tmp/challenge_results/waypoint_results.pkl` after each run (appended, not overwritten). `/tmp` is not persisted across container restarts.

### Print results

```bash
python3 navwaypoints_server/print_results.py
# or specify a path explicitly
python3 navwaypoints_server/print_results.py /tmp/challenge_results/waypoint_results.pkl
```

### Persist results to the shared volume

Copy the file back to the package directory before stopping the container:

```bash
cp /tmp/challenge_results/waypoint_results.pkl \
   ~/ros2_ws/src/linorobot2/navigation_waypoints_action/navwaypoints_server/
```

The file will then be available on the host via the mounted volume.
