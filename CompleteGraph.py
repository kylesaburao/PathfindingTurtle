import copy
import math
import operator
import heapq
from collections import deque

# Supports edge blocking where algorithms will not traverse an edge that is marked blocked

##########################################################################################################


class CompleteGraph:

    def __init__(self):
        # Initialize instance variables
        self.vertexDict = {}
        self.blockedEdges = set()

    def push_vertex(self, key: str = '', value=None, x: float = 0, y: float = 0):
        key = str(key)
        x = float(x)
        y = float(y)
        if key != '' and not self.has_vertex(key):
            newVertexPosition = (x, y)
            self.vertexDict[key] = [value, newVertexPosition]
        else:
            raise ValueError(f"Vertex {key} already in graph")

    def pop_vertex(self, key: str = ''):
        key = str(key)
        self._validate_keys_in_graph(key)
        del self.vertexDict[key]

        edge_remove_queue = []
        for edge in self.blockedEdges:
            if edge[0] == key or edge[1] == key:
                edge_remove_queue.append(edge)

        for edge in edge_remove_queue:
            self.blockedEdges.remove(edge)

    def block_edge(self, key_a: str = '', key_b: str = ''):
        key_a = str(key_a)
        key_b = str(key_b)
        self._validate_keys_in_graph(key_a, key_b)

        if not self.is_edge_blocked(key_a, key_b):
            self.blockedEdges.add((key_a, key_b))
        else:
            raise ValueError(f'Edge {{{key_a}, {key_b}}} already blocked')

    def unblock_edge(self, key_a: str = '', key_b: str = ''):
        key_a = str(key_a)
        key_b = str(key_b)
        if self.is_edge_blocked(key_a, key_b):
            if (key_a, key_b) in self.blockedEdges:
                self.blockedEdges.remove((key_a, key_b))
            else:
                self.blockedEdges.remove((key_b, key_a))
        else:
            raise ValueError(f'Edge {{{key_a}, {key_b}}} was not blocked')

    def is_edge_blocked(self, key_a: str = '', key_b: str = ''):
        key_a = str(key_a)
        key_b = str(key_b)
        if key_a != key_b:
            return (key_a, key_b) in self.blockedEdges or (key_b, key_a) in self.blockedEdges
        else:
            return True  # Deny loops

    def set_position(self, key: str = '', x: float = 0, y: float = 0):
        key = str(key)
        self._validate_keys_in_graph(key)
        x = float(x)
        y = float(y)
        newVertexPosition = (x, y)
        self.vertexDict[key][1] = newVertexPosition

    def get_position(self, key: str = ''):
        key = str(key)
        self._validate_keys_in_graph(key)
        position = self.vertexDict[key][1]
        return position

    def has_vertex(self, key: str = ''):
        key = str(key)
        return key in self.vertexDict

    def get_distance(self, key_a: str = '', key_b: str = ''):
        key_a = str(key_a)
        key_b = str(key_b)

        self._validate_keys_in_graph(key_a, key_b)
        if self.is_edge_blocked(key_a, key_b):
            return math.inf  # Keep?

        position_a = self.get_position(key_a)
        position_b = self.get_position(key_b)
        delta_x = position_a[0] - position_b[0]
        delta_y = position_a[1] - position_b[1]
        distance = math.sqrt(delta_x * delta_x + delta_y * delta_y)
        return distance

    def get_all_adjacent(self, key: str = ''):
        """Closest adjacent list

        Get the list of all (open or blocked) vertex keys adjacent to a given vertex.
        """
        key = str(key)
        self._validate_keys_in_graph(key)
        output = [(adj_key, self.get_distance(key, adj_key))
                  for adj_key in self.vertexDict if adj_key != key]
        # Sort by distance, then key
        output.sort(key=operator.itemgetter(1, 0))
        return output

    def vertex_set(self):
        return set(key for key in self.vertexDict)

    def vertex_set_tuple(self):
        return tuple(key for key in self.vertexDict)

    def edge_set(self):
        edges = set()
        for key_a in self.vertexDict:
            for key_b in self.vertexDict:
                if (key_a, key_b) not in edges and (key_b, key_a) not in edges and key_a != key_b:
                    edges.add((key_a, key_b))
        return edges

    def _vertex_set_generator(self):
        for key in self.vertexDict:
            yield key

    def _validate_keys_in_graph(self, *keys):
        for key in keys:
            if not self.has_vertex(key):
                raise ValueError(f'Vertex \'{key}\' does not exist')

    def _get_all_adjacent_generator(self, key: str = ''):
        """Closest adjacent generator

        Use when searching for the first closest (open or blocked) adjacent vertex satisfying some property.

        Deferred heap sort.  
        Expected Runtime: O(n + klog(n))  
            n: heapify.  
            klog(n): Pop the k-th smallest elements.
        """
        key = str(key)
        self._validate_keys_in_graph(key)

        adj = [(self.get_distance(key, adj_key), adj_key)
               for adj_key in self._vertex_set_generator() if adj_key != key]
        heapq.heapify(adj)

        while len(adj) > 0:
            yield heapq.heappop(adj)

    def _get_open_adjacent_keys(self, key: str = ''):
        key = str(key)
        self._validate_keys_in_graph(key)
        return tuple(adj_key for adj_key in self.vertexDict if adj_key != key and not self.is_edge_blocked(key, adj_key))

    def _get_open_adjacent(self, key: str = ''):
        key = str(key)
        self._validate_keys_in_graph(key)
        return tuple((adj_key, self.get_distance(key, adj_key)) for adj_key in self._get_open_adjacent_keys(key))

    def _get_blocked_adjacent_keys(self, key: str = ''):
        key = str(key)
        self._validate_keys_in_graph(key)
        return tuple(adj_key for adj_key in self.vertexDict if adj_key != key and self.is_edge_blocked(key, adj_key))

    def _get_blocked_adjacent(self, key: str = ''):
        key = str(key)
        self._validate_keys_in_graph(key)
        return tuple((adj_key, self.get_distance(key, adj_key)) for adj_key in self._get_blocked_adjacent_keys(key))

    ##########################################################################################################

    def euler_tour(self, start_key: str = ''):
        start_key = str(start_key)
        self._validate_keys_in_graph(start_key)

        key_stack = [start_key]
        is_visited = set()
        output = []

        while len(key_stack) > 0:
            current_key = key_stack[-1]
            output.append(current_key)
            foundUnvisitedAdjacent = False

            if current_key not in is_visited:
                is_visited.add(current_key)

            adj_generator = self._get_all_adjacent_generator(current_key)

            for adj in adj_generator:
                adj_key = adj[1]
                if not self.is_edge_blocked(current_key, adj_key) and adj_key not in is_visited:
                    key_stack.append(adj_key)
                    foundUnvisitedAdjacent = True
                    # break

            if not foundUnvisitedAdjacent:
                key_stack.pop()

        return output

    def euler_tour_by_mst(self, start_key: str = ''):
        start_key = str(start_key)
        self._validate_keys_in_graph(start_key)

        key_stack = [start_key]
        is_visited = set()
        output = []

        mst_adjacency_dict = self.get_mst(start_key)
        mst_adjacency_dict_heapable = dict(
            (key, []) for key in mst_adjacency_dict)
        for key in mst_adjacency_dict_heapable:
            mst_adjacency_dict_heapable[key] = [(self.get_distance(
                key, adjacent_key), adjacent_key) for adjacent_key in mst_adjacency_dict[key]]
            heapq.heapify(mst_adjacency_dict_heapable[key])

        while len(key_stack) > 0:
            current_key = key_stack[-1]
            output.append(current_key)
            foundUnvisitedAdjacent = False

            if current_key not in is_visited:
                is_visited.add(current_key)

            current_adjacency_heap = mst_adjacency_dict_heapable[current_key]

            while len(current_adjacency_heap) > 0:
                current_adjacent = heapq.heappop(current_adjacency_heap)
                current_adjacent_key = current_adjacent[1]

                # Adjacent vertices that are already visited do not have to be considered
                # so it is fine to pop them off the adjacency list of a given vertex
                if current_adjacent_key not in is_visited:
                    key_stack.append(current_adjacent_key)
                    foundUnvisitedAdjacent = True
                    break
                    # Break so that the closest are considered first. Equivalent to simulating stack
                    # or reversing a sorted list that goes into a stack.

            if not foundUnvisitedAdjacent:
                key_stack.pop()

        return output

    ##########################################################################################################

    def available_path(self, start_key: str = '', end_key: str = ''):
        start_key = str(start_key)
        end_key = str(end_key)
        self._validate_keys_in_graph(start_key, end_key)

        path = []
        # data = self.dijkstra(start_key, end_key)
        data = self.a_star(start_key, end_key)

        if start_key == end_key:
            output = ([start_key], 0.0)
        elif data['previous'][end_key] != '':
            current_key = end_key

            while current_key != '':
                path.append(current_key)
                current_key = data['previous'][current_key]

            path.reverse()
            output = (path, data['distance'][end_key])
        else:
            output = ([''], math.inf)

        return output

    def exists_path(self, start_key: str = '', end_key: str = ''):
        path_data = self.available_path(start_key, end_key)
        return path_data != ('', math.inf)

    def all_reachable(self, start_key: str = '', max_distance: float = math.inf):
        start_key = str(start_key)
        self._validate_keys_in_graph(start_key)

        data = self.dijkstra(start_key)
        reachable_vertices = filter(
            lambda key: key != start_key and data['distance'][key] <= max_distance, data['distance'])
        output_paths = {}

        for key in reachable_vertices:
            path = self.available_path(start_key, key)
            output_paths[key] = path

        return output_paths

    def a_star(self, start_key: str = '', target_key: str = ''):
        start_key = str(start_key)
        target_key = str(target_key)
        self._validate_keys_in_graph(start_key)
        self._validate_keys_in_graph(target_key)

        def get_h_score(key_a: str):
            return self.get_distance(key_a, target_key)

        vertex_keys = self.vertex_set_tuple()
        distances = {}  # Closed set
        previous = dict((key, '') for key in vertex_keys)

        # Treat the f_score set as open set
        f_score = [(math.inf, key) for key in vertex_keys if key != start_key]
        g_score = dict((key, math.inf) for key in vertex_keys)

        g_score[start_key] = 0
        f_score.append((get_h_score(start_key), start_key))

        heapq.heapify(f_score)

        while len(f_score) > 0:
            current = heapq.heappop(f_score)
            current_key = current[1]
            distances[current_key] = g_score[current_key]

            if current_key == target_key:
                break

            heapModified = False

            for i, adjacent in enumerate(f_score):
                adjacent_key = adjacent[1]

                if adjacent_key not in distances and not self.is_edge_blocked(current_key, adjacent_key):
                    tentative_distance = g_score[current_key] + \
                        self.get_distance(current_key, adjacent_key)

                    if tentative_distance < g_score[adjacent_key]:
                        previous[adjacent_key] = current_key
                        g_score[adjacent_key] = tentative_distance
                        f_score[i] = (g_score[adjacent_key] +
                                      get_h_score(adjacent_key), adjacent_key)
                        heapModified = True

            if heapModified:
                heapq.heapify(f_score)

        return_dict = {}
        return_dict['distance'] = distances
        return_dict['previous'] = previous
        return return_dict

    def dijkstra(self, start_key: str = '', target_key: str = ''):
        # Redundant if there are no blocked edges
        start_key = str(start_key)

        self._validate_keys_in_graph(start_key)
        returnDict = {}
        previous = dict((key, '') for key in self.vertexDict)
        closedSetDistances = {}

        openHeap = [(0, start_key)]
        openHeap.extend(((math.inf, key)
                         for key in self.vertexDict if key != start_key))

        exit_on_target_reached = False
        if target_key != '':
            self._validate_keys_in_graph(target_key)
            exit_on_target_reached = True

        while len(openHeap) != 0:
            current = heapq.heappop(openHeap)
            current_key = current[1]
            current_distance = current[0]

            # Add the current key to the closed set
            # Algorithm states that the current key is finally minimized
            closedSetDistances[current_key] = current_distance

            if exit_on_target_reached and current_key == target_key:
                break

            heapModified = False

            # Only non-visited vertices are considered as the visited have already
            # been popped from the heap.
            for i, adj in enumerate(openHeap):
                adj_key = adj[1]
                adj_dist = adj[0]

                # Loops are blocked by default
                if not self.is_edge_blocked(current_key, adj_key):
                    tentative_distance = current_distance + \
                        self.get_distance(current_key, adj_key)

                    if tentative_distance < adj_dist:
                        openHeap[i] = (tentative_distance, adj_key)
                        previous[adj_key] = current_key
                        heapModified = True

            if heapModified:
                heapq.heapify(openHeap)

        returnDict['distance'] = closedSetDistances
        returnDict['previous'] = previous
        return returnDict

    def nearest_neighbour(self, start_key: str = ''):
        start_key = str(start_key)

        self._validate_keys_in_graph(start_key)
        is_visited = dict((key, False) for key in self.vertexDict)
        current_key = start_key
        path = [start_key]
        vertexFound = True

        while vertexFound:
            vertexFound = False
            is_visited[current_key] = True

            adj_generator = self._get_all_adjacent_generator(current_key)

            for adj in adj_generator:
                adj_key = adj[1]
                if not is_visited[adj_key] and not self.is_edge_blocked(current_key, adj_key):
                    path.append(adj_key)
                    current_key = adj_key
                    vertexFound = True
                    break

        return path

    # Prim MST
    def get_mst(self, start_key: str = ''):
        start_key = str(start_key)
        self._validate_keys_in_graph(start_key)
        VERTEX_KEYS = tuple(key for key in self.vertexDict)
        mst_vertices = {}  # Treat as closed set {key : [adj]}
        edge_queue = []  # Min-priority queue

        mst_vertices[start_key] = []

        def is_open(key):
            return key not in mst_vertices

        def push_edges(key, queue):
            insert_list = ((self.get_distance(key, adjacent), key, adjacent)
                           for adjacent in VERTEX_KEYS if is_open(adjacent) and not is_open(key) and not self.is_edge_blocked(key, adjacent))

            for edge in insert_list:
                heapq.heappush(queue, edge)

        push_edges(start_key, edge_queue)

        while len(edge_queue) > 0 and (len(mst_vertices) < len(VERTEX_KEYS)):
            current_edge = heapq.heappop(edge_queue)

            if is_open(current_edge[1]) != is_open(current_edge[2]):
                closed_key = current_edge[1] if not is_open(
                    current_edge[1]) else current_edge[2]
                open_key = current_edge[2] if closed_key == current_edge[1] else current_edge[1]

                mst_vertices[closed_key].append(open_key)
                mst_vertices[open_key] = [closed_key]
                # For any vertex that isn't the start, the first vertex in its adjacency list is the algorithm parent

                if len(mst_vertices) < len(VERTEX_KEYS):
                    push_edges(open_key, edge_queue)

        return mst_vertices


if __name__ == '__main__':

    g = CompleteGraph()

    g.push_vertex('a', x=0, y=0)
    g.push_vertex('b', x=1, y=1)
    g.push_vertex('c', x=2, y=1)
    g.push_vertex('d', x=10, y=10)
    g.block_edge('a', 'c')

    print(g.a_star('a', 'c'))

    pass
