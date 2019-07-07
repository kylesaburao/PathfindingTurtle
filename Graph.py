import Node
import random


class Graph:

    def __init__(self, nodes=[]):
        self.nodes = {node.key: node for node in nodes}

    def add_node(self, node):
        try:
            self.nodes[node.key] = node
        except:
            pass

    def remove_node(self, node):
        try:
            del self.nodes[node.key]
        except:
            pass

    def get_node(self, key):
        try:
            return self.nodes[key]
        except:
            return None

    def add_edge(self, node_a, node_b):
        try:
            node_a = self.get_node(node_a.key)
            node_b = self.get_node(node_b.key)
            if node_a is not None and node_b is not None:
                node_a.add_neighbour(node_b)
                node_b.add_neighbour(node_a)
        except:
            pass

    def remove_edge(self, node_a, node_b):
        try:
            node_a = self.get_node(node_a.key)
            node_b = self.get_node(node_b.key)
            if node_a is not None and node_b is not None:
                node_a.remove_neighbour(node_b)
                node_b.remove_neighbour(node_a)
        except:
            pass


def construct_graph(dict_graph={}):
    graph = Graph()
    for key in dict_graph:
        node = Node.Node(key=key)
        graph.add_node(node)

    for key in dict_graph:
        current_node = graph.get_node(key)
        for neighbour_key in dict_graph[key]:
            current_node.add_neighbour(graph.get_node(neighbour_key))
    return graph


def rand_graph(n, p):
    graph = {x: set() for x in range(n)}

    for i in range(n):
        for j in range(i + 1, n):
            if i != j and random.random() < p:
                graph[i].add(j)
                graph[j].add(i)

    for i in range(n):
        newList = [j for j in graph[i]]
        graph[i] = newList

    return graph


if __name__ == "__main__":
    rg = rand_graph(10, 0.3)

    graph = construct_graph(rg)

    for key in graph.nodes:
        node = graph.get_node(key)
        print(key)
        for neighbour in node.neighbours:
            print(f'\t{neighbour.key}')
