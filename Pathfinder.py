import copy
import math
import bisect
import operator

import CompleteGraph
import LineIntersection


class Pathfinder:

    def __init__(self):
        self.itemGraph = CompleteGraph.CompleteGraph()
        self.obstacleDict = dict()

    def clear(self):
        self.itemGraph = CompleteGraph.CompleteGraph()
        self.obstacleDict = dict()

    ########################################################################

    def add_item(self, item_id: str = 'A', item_value=None, x_pos: float = 0, y_pos: float = 0):
        if item_id == '':
            raise ValueError('Item ID cannot be the empty string')

        self._validate_item_nonexistence(item_id)
        self.itemGraph.push_vertex(item_id, item_value, x_pos, y_pos)
        self._blockable_difference()

    def remove_item(self, item_id: str = ''):
        self._validate_item_existence(item_id)
        self.itemGraph.pop_vertex(item_id)
        # No need to take difference as pop already removes blocked edges

    def has_item(self, item_id: str):
        return self.itemGraph.has_vertex(item_id)

    def item_position(self, id_item: str):
        return self.itemGraph.get_position(id_item)

    def item_distance(self, item_id_1: str, item_id_2: str):
        self._validate_item_existence(item_id_1, item_id_2)
        return self.itemGraph.get_distance(item_id_1, item_id_2)

    def is_direct_move_possible(self, item_id_1: str, item_id_2: str):
        self._validate_item_existence(item_id_1, item_id_2)
        return not self.itemGraph.is_edge_blocked(item_id_1, item_id_2)

    def item_keys(self):
        return list(key for key in self.itemGraph.vertex_set())

    ########################################################################

    def add_obstacle(self, obs_id: str = 'A', x_pos: float = 0, y_pos: float = 0, radius: float = 0):
        obs_id = str(obs_id)
        if not self.has_obstacle(obs_id):
            obstacle_object = LineIntersection.Obstacle(
                x_pos, y_pos, radius)
            self.obstacleDict[obs_id] = obstacle_object
            self._blockable_difference()
        else:
            raise ValueError(f'Obstacle {obs_id} already exists')

    def remove_obstacle(self, obs_id: str = 'A'):
        obs_id = str(obs_id)
        if self.has_obstacle(obs_id):
            del self.obstacleDict[obs_id]
            self._blockable_difference()
        else:
            raise ValueError(f'Obstacle{obs_id} does not exist')

    def has_obstacle(self, obs_id: str = 'A'):
        obs_id = str(obs_id)
        return obs_id in self.obstacleDict

    def obstacle_position_radius(self, obs_id: str = 'A'):
        obs_id = str(obs_id)
        if self.has_obstacle(obs_id):
            return (self.obstacleDict[obs_id].x, self.obstacleDict[obs_id].y, self.obstacleDict[obs_id].r)

    def obstacle_keys(self):
        return list(key for key in self.obstacleDict)

    ########################################################################

    def _validate_item_existence(self, *item_keys: str):
        for item_key in item_keys:
            if not self.has_item(str(item_key)):
                raise ValueError(f'Item with ID {item_key} does not exist')

    def _validate_item_nonexistence(self, *item_keys: str):
        for item_key in item_keys:
            if self.has_item(str(item_key)):
                raise ValueError(f'Item with ID {item_key} already exists')

    # @DeprecationWarning
    def _blockable_edges(self):
        vertex_keys = self.itemGraph.vertex_set_tuple()
        blockable_edges = set()

        for i in range(len(vertex_keys)):
            vertex_key_a = vertex_keys[i]
            position_a = self.itemGraph.get_position(vertex_key_a)

            for j in range(i + 1, len(vertex_keys)):
                vertex_key_b = vertex_keys[j]
                position_b = self.itemGraph.get_position(vertex_key_b)

                for obstacle_key in self.obstacleDict:
                    is_edge_blocked = self.obstacleDict[obstacle_key].is_obstacle_on_edge_p(
                        position_a, position_b)
                    is_edge_already_in_set = (vertex_key_a, vertex_key_b) in blockable_edges or (
                        vertex_key_b, vertex_key_a) in blockable_edges
                    if is_edge_blocked and not is_edge_already_in_set:
                        blockable_edges.add((vertex_key_a, vertex_key_b))

        return tuple(blockable_edges)

    def _sweep_blockable_edges(self):
        blocked_edges = set()

        items = [(self.item_position(key)[0], key)
                 for key in self.itemGraph.vertexDict]
        items.sort(key=operator.itemgetter(0))
        items_x = [item[0] for item in items]  # Auxiliary for bisect
        obstacles = [(self.obstacleDict[key].x, key)
                     for key in self.obstacleDict]

        for obstacle in obstacles:
            obstacle_x = obstacle[0]
            obstacle_id = obstacle[1]

            left_partition = bisect.bisect_left(items_x, obstacle_x)
            right_partition = bisect.bisect_right(items_x, obstacle_x)

            # Case 1: If l == r, partition from there and check
            #   All items left of the left partition and right of the right partition will be paired
            # Case 2: If l != r, partition again, and also check between on same x's
            #   All items between the partition have the same x-value as the obstacle and will be paired

            # Sweep outside partition
            for left in range(0, left_partition):
                for right in range(right_partition, len(items)):
                    left_id = items[left][1]
                    right_id = items[right][1]
                    left_position = self.item_position(left_id)
                    right_position = self.item_position(right_id)

                    is_edge_blocked = self.obstacleDict[obstacle_id].is_obstacle_on_edge_p(
                        left_position, right_position)

                    if is_edge_blocked:
                        edge = (left_id, right_id)
                        blocked_edges.add(edge)

            # Sweep within partition
            for left in range(left_partition, right_partition):
                for right in range(left + 1, right_partition):
                    left_id = items[left][1]
                    right_id = items[right][1]
                    left_position = self.item_position(left_id)
                    right_position = self.item_position(right_id)

                    is_edge_blocked = self.obstacleDict[obstacle_id].is_obstacle_on_edge_p(
                        left_position, right_position)

                    if is_edge_blocked:
                        edge = (left_id, right_id)
                        blocked_edges.add(edge)

        return tuple(blocked_edges)

    def _blockable_difference(self):

        # If there are no obstacles, don't go through the loops
        # if not bool(self.obstacleDict):
        #     return

        current_blocked = copy.deepcopy(self.itemGraph.blockedEdges)
        current_blockable = self._blockable_edges()
        # current_blockable = self._sweep_blockable_edges()

        to_remove = filter(
            lambda edge: edge in current_blocked and edge not in current_blockable, current_blocked)
        to_add = filter(
            lambda edge: edge in current_blockable and edge not in current_blocked, current_blockable)

        for removable_edge in to_remove:
            self.itemGraph.unblock_edge(removable_edge[0], removable_edge[1])

        for blockable_edge in to_add:
            self.itemGraph.block_edge(blockable_edge[0], blockable_edge[1])

    ########################################################################

    def dijkstra(self, start_key: str = ''):
        self._validate_item_existence(start_key)
        return self.itemGraph.dijkstra(start_key)

    def available_path(self, start_key: str = '', end_key: str = ''):
        self._validate_item_existence(start_key, end_key)
        return self.itemGraph.available_path(start_key, end_key)

    def exists_path(self, start_key: str = '', end_key: str = ''):
        self._validate_item_existence(start_key, end_key)
        return self.itemGraph.exists_path(start_key, end_key)

    def all_reachable(self, start_key: str = '', max_distance: float = math.inf):
        self._validate_item_existence(start_key)
        return self.itemGraph.all_reachable(start_key, max_distance)

    # Does not consider blocked edges
    def nearest_neighbour(self, start_key: str = ''):
        self._validate_item_existence(start_key)
        return {start_key: self.itemGraph.nearest_neighbour(start_key)}

    def mst(self, start_key: str = ''):
        self._validate_item_existence(start_key)
        return self.itemGraph.get_mst(start_key)

    def euler_tour(self, start_key: str = ''):
        self._validate_item_existence(start_key)
        return {start_key: self.itemGraph.euler_tour(start_key)}

    # Construct euler tour around prim mst generated from the start key
    # This is the algorithm described by Matt DeVos which approximates the Hamiltonian travelling salesman
    def mst_euler_tour(self, start_key: str = ''):
        self._validate_item_existence(start_key)
        return {start_key: self.itemGraph.euler_tour_by_mst(start_key)}

    def mst_optimized_tour(self, start_key: str = ''):
        self._validate_item_existence(start_key)

        tour = self.itemGraph.euler_tour_by_mst(start_key)
        is_visited = set()
        path = []
        inflection_point = None

        for i, key in enumerate(tour):

            if key not in is_visited:
                is_visited.add(key)
                if inflection_point is None:
                    path.append(key)
                else:
                    if self.is_direct_move_possible(inflection_point, key):
                        path.append(key)
                    else:
                        path.extend(self.itemGraph.available_path(
                            inflection_point, key)[0][1:])
                    inflection_point = None

                # If the key ahead is already visited, jump to the next unvisited key
                if i < len(tour) - 1:
                    key_ahead = tour[i + 1]
                    if key_ahead in is_visited:
                        inflection_point = key

        # Return to start
        if len(path) > 1:
            path.extend(self.itemGraph.available_path(
                path[-1], start_key)[0][1:])

        return path


if __name__ == '__main__':

    branch_test = Pathfinder()
    branch_test.add_item('A', x_pos=0, y_pos=0, item_value=None)
    branch_test.add_item('B', x_pos=1, y_pos=1, item_value=None)
    branch_test.add_item('C', x_pos=1, y_pos=2, item_value=None)
    branch_test.add_item('D', x_pos=2, y_pos=1, item_value=None)
    branch_test.add_item('E', x_pos=10, y_pos=0)
    branch_test.add_item('F', x_pos=-1, y_pos=0)

    branch_test.add_obstacle('OBS1', x_pos=0.5, y_pos=0.5, radius=0.1)
    branch_test.add_obstacle('OBS2', x_pos=1, y_pos=1.5, radius=0.1)

    # print(branch_test.mst_euler_tour('A'))
    # print(branch_test.mst_optimized_tour('A'))

    print()
    print(branch_test.itemGraph.blockedEdges)

    # print(branch_test.is_direct_move_possible('D', 'B'))
    # print(branch_test.is_direct_move_possible('E', 'A'))
    # print(branch_test.is_direct_move_possible('D', 'A'))
    # print(branch_test.is_direct_move_possible('B', 'E'))

    # branch_mst = branch_test.mst('A')
    # print(f'Branch Test MST: {branch_mst}')

    # branch_nn = branch_test.nearest_neighbour('A')
    # print(f'Branch Test NN: {branch_nn}')

    # branch_et = branch_test.euler_tour('A')
    # print(f'Branch Test ET: {branch_et}')

    # branch_mstet = branch_test.mst_euler_tour('A')
    # print(f'Branch Test MST_ET: {branch_mstet}')

    # branch_opttour = branch_test.mst_optimized_tour('A')
    # print(f'Branch Test OPTTOUR: {branch_opttour}')
    # cost = 0

    # for i in range(len(branch_opttour['A']) - 1):
    #     cost += branch_test.item_distance(
    #         branch_opttour['A'][i], branch_opttour['A'][i + 1])

    # print(f'Optimal tour cost: {cost}')

    # def sequence_weight(seq, pather):
    #     weight = 0.0
    #     for i in range(len(seq) - 1):
    #         weight += pather.item_distance(seq[i], seq[i + 1])
    #     return weight

    # print(sequence_weight(branch_opttour['A'], branch_test))
    # print(sequence_weight(branch_mstet['A'], branch_test))
    # print(sequence_weight(branch_et['A'], branch_test))
    # print(sequence_weight(branch_nn['A'], branch_test))
