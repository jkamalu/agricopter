# This module finds for a graph of cells
# the ______  complete covereage path for
# the drone, crossing from cell to cell only
# by existing edges

import shapely
from shapely.geometry import Polygon

import parsepolygon
import decompose
import cellgrapher

class StackElem:
    def __init__(self, node, first_visit):
        self.node = node
        self.first_visit = first_visit

def optimal(graph_meta):
	stack = []
	optimal_helper(graph_meta.start, stack, graph_meta.node_count)
	return stack

def optimal_helper(node, stack, to_visit):
	node.visited = True
	stack.append(StackElem(node, first_visit=True))
	to_visit = to_visit - 1
	if to_visit == 0:
		return None
	for edge in node.edges:
		next_node = None
		if edge.node_a == node:
			next_node = edge.node_b
		else:
			next_node = edge.node_a
		if next_node.visited is False:
			optimal_helper(next_node, stack, to_visit)
			stack.append(StackElem(node, first_visit=False))

if __name__ == '__main__':

	INPUT_FILE = "test_fields/test2.txt"
	DRONE_RADIUS = .1

	polygon = parsepolygon.parse_polygon(INPUT_FILE)
	cells = decompose.decompose(polygon)[0]
	meta = cellgrapher.build_graph(cells)
	optimal = optimal(meta)

