import Node
import Graph
import heapq
import math


def depth_first_search(graph, start_node, goal_node):

    frontier = [start_node]
    visited = set()

    path = []

    while len(frontier) > 0:
        current_node = frontier.pop()
        path.append(current_node)
        if current_node == goal_node:
            return path

        visited.add(current_node)

        for neighbour_node in current_node.neighbours:
            if neighbour_node not in frontier and neighbour_node not in visited:
                frontier.append(neighbour_node)

    return path


def a_star_search(graph, start_node, goal_node):
    """
    Assumes the nodes are CartesianNode.
    """

    def find_node_queue_index(node, queue):
        for i, (v, n) in enumerate(queue):
            if n == node:
                return i
        return -1

    def g(cost_map, node):
        return cost_map[node]

    def h(node_a, node_b):
        return node_a.distance(node_b)

    def f(cost_map, node_a, node_b):
        return g(cost_map, node_a) + h(node_a, node_b)

    visited = set()
    came_from = {node: None for node in graph.nodes.values()}
    actual_cost = {node: math.inf for node in graph.nodes.values()}
    actual_cost[start_node] = 0

    queue = [(math.inf if node != start_node else start_node.distance(goal_node), node)
             for node in graph.nodes.values()]

    heapq.heapify(queue)

    while len(queue) > 0:
        current = heapq.heappop(queue)
        current_node = current[1]
        heap_modified = False

        if current_node == goal_node:
            break

        visited.add(current)

        for neighbour_node in current_node.neighbours:
            if neighbour_node not in visited:
                inter_node_distance = current_node.distance(neighbour_node)
                tentative_actual_cost = actual_cost[current_node] + \
                    inter_node_distance

                # Neighbour was reached an actual distance than before
                if tentative_actual_cost < actual_cost[neighbour_node]:
                    actual_cost[neighbour_node] = tentative_actual_cost
                    came_from[neighbour_node] = current_node

                    neighbour_queue_index = find_node_queue_index(
                        neighbour_node, queue)

                    if 0 <= neighbour_queue_index < len(queue):
                        queue[neighbour_queue_index] = (
                            actual_cost[neighbour_node] + neighbour_node.distance(goal_node), neighbour_node)
                        heap_modified = True

        if heap_modified:
            heapq.heapify(queue)

    return came_from


def reconstruct_path(came_from, start_node, end_node):
    path = []

    # Terminal nodes are not in the A* search data
    if start_node not in came_from or end_node not in came_from:
        return None

    # No path exists to the end node
    if came_from[end_node] == None:
        return None

    current_node = end_node

    while current_node != None:
        path.append(current_node)
        current_node = came_from[current_node]

    path.reverse()

    return path


if __name__ == "__main__":

    node_a = Node.CartesianNode(key='A', value=(0, 0))
    node_b = Node.CartesianNode(key='B', value=(1, 0))
    node_c = Node.CartesianNode(key='C', value=(0, 1))
    node_d = Node.CartesianNode(key='D', value=(1, 1))
    node_e = Node.CartesianNode(key='E', value=(2, 2))

    node_a.add_neighbour(node_b)
    node_a.add_neighbour(node_b)
    node_a.add_neighbour(node_d)
    node_d.add_neighbour(node_e)

    nodes = [node_a, node_b, node_c, node_d, node_e]
    graph = Graph.Graph(nodes=nodes)

    dfs = depth_first_search(graph, node_a, node_e)
    astar_cf = a_star_search(graph, node_a, node_e)

    print(dfs)
    print(astar_cf)
    test_result = {
        c.key: f.key if f is not None else None for c, f in astar_cf.items()}
    print('test result: ', test_result)

    print(reconstruct_path(astar_cf, node_a, node_e))
    print()
