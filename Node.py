import time
import math
import functools

DEFAULT_DIMENSIONS = 2

def make_timestamp_id():
    return str(int(time.time() * 1000))

@functools.total_ordering
class Node:

    def __init__(self, key=make_timestamp_id(), value=None, neighbours=[]):
        self.key = key
        self.value = value
        self.neighbours = set(neighbours)

    def __eq__(self, other):
        try:
            return self.key == other.key
        except:
            return False

    def __lt__(self, other):
        try:
            return self.key < other.key
        except:
            return False

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return f'({self.key}, {self.value}, {len(self.neighbours)})'

    def add_neighbour(self, node):
        self.neighbours.add(node)

    def remove_neighbour(self, node):
        if self.has_neighbour(node):
            self.neighbours.remove(node)

    def has_neighbour(self, node):
        return node in self.neighbours

    def degree(self):
        return len(self.neighbours)

    def distance(self, node):
        return 1


class CartesianNode(Node):
    """
    Represents a node whose value is a position in N-dimensional space.
    The node expects that the value is a n-tuple of length n for the n-dimensions.
    There is no enforced or preferred ordering of the dimensions. The only requirement for the user is consistency.
    """

    def __init__(self, key=make_timestamp_id(), value=None, neighbours=[]):
        super().__init__(key=key, value=value, neighbours=neighbours)

        if self.value is not None:
            if not isinstance(self.value, tuple):
                raise RuntimeError(
                    "The value must be a n-length tuple, for n-dimensions")
        else:
            self.value = tuple(0 for x in range(DEFAULT_DIMENSIONS))

    def dimensions(self):
        return len(self.value)

    def euclidian_distance(self, dim_zip):
        return math.sqrt(sum(pow(abs(dim_pair[0] - dim_pair[1]), 2) for dim_pair in dim_zip))

    def manhattan_distance(self, dim_zip):
        return sum(abs(dim_pair[0] - dim_pair[1]) for dim_pair in dim_zip)

    def distance(self, node, dim_compare=None):
        """
        Straight-line (euclidian distance) between two points in cartesian space.

        Pre-condition: The dimensions of both nodes must match.
                       Both value position tuples must be non-null and match in length.

                       dim_compare is a function that takes dimension pairs from the zipped
                       positions of both nodes, and calculates the "distance" between them.
        """

        assert self.value is not None
        assert node.value is not None
        assert isinstance(self.value, tuple) and isinstance(
            node.value, tuple) and len(self.value) == len(node.value)
        assert isinstance(node, CartesianNode)
        if self.dimensions() != node.dimensions():
            raise RuntimeError(
                f'Position of a {self.dimensions()}-dimensional node cannot be compared to a {node.dimensions()}-dimensional node')

        if dim_compare == None:
            dim_compare = self.euclidian_distance

        distance = dim_compare(zip(self.value, node.value))
        return distance

    def set_position(self, position):
        assert isinstance(position, tuple) and len(position) == self.dimensions()
        self.value = position

if __name__ == "__main__":
        
    x = CartesianNode(value=(1, 1, 1, 1))
    y = CartesianNode(value=(0, 0, 0, 0))
    print(x.distance(y, x.euclidian_distance))
    print(x.distance(y, x.manhattan_distance))
