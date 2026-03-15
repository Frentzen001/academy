import math
import itertools
import networkx as nx


def solve_tsp(start: tuple, waypoints: list[tuple]) -> list[tuple]:
    """
    Solve the Travelling Salesman Problem to find the most efficient order
    to visit all waypoints starting from the robot's current position.

    Args:
        start: (x, y) tuple of the robot's current position
        waypoints: list of (x, y) tuples to visit

    Returns:
        Reordered list of waypoints in the most efficient visit order
    """
    if len(waypoints) <= 1:
        return list(waypoints)

    all_nodes = [start] + list(waypoints)
    n = len(all_nodes)

    G = nx.Graph()
    for i in range(n):
        for j in range(i + 1, n):
            dist = math.sqrt(
                (all_nodes[i][0] - all_nodes[j][0]) ** 2 +
                (all_nodes[i][1] - all_nodes[j][1]) ** 2
            )
            G.add_edge(i, j, weight=dist)

    # Use greedy TSP approximation (nearest-neighbour) then improve with 2-opt
    # networkx greedy_tsp starts and ends at node 0 (the robot's position)
    path = nx.approximation.greedy_tsp(G, source=0, weight='weight')

    # path is a cycle: [0, ..., 0]; strip start/end node (index 0 = robot pos)
    ordered_indices = [node for node in path if node != 0]

    return [waypoints[i - 1] for i in ordered_indices]


if __name__ == '__main__':
    robot_pos = (0.0, 0.0)
    coords = [(0.3845, 1.49), (0.52, -1.75), (-1.59, 1.63), (-1.55, -1.55)]

    print(f'Robot position : {robot_pos}')
    print(f'Original order : {coords}')

    sorted_coords = solve_tsp(robot_pos, coords)

    print(f'Optimised order: {sorted_coords}')

    # Show total path length for both orderings
    def path_length(start, points):
        total = 0.0
        prev = start
        for p in points:
            total += math.sqrt((p[0] - prev[0]) ** 2 + (p[1] - prev[1]) ** 2)
            prev = p
        return total

    orig_len = path_length(robot_pos, coords)
    opt_len  = path_length(robot_pos, sorted_coords)
    print(f'Original path length : {orig_len:.3f} m')
    print(f'Optimised path length: {opt_len:.3f} m')
    print(f'Saving               : {orig_len - opt_len:.3f} m ({(1 - opt_len/orig_len)*100:.1f}%)')
