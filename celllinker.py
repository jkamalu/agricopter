# This module finds for a graph of cells
# the optimal complete covereage path for
# the drone, crossing from cell to cell only
# by existing edges

from cellgrapher import (GraphMeta, CellNode, CellEdge)

def optimal(graph_meta):
	stack = []
	optimal_helper(graph_meta.start, stack, graph_meta.node_count)
	return stack

def optimal_helper(node, stack, to_visit):
	node.visited = True
	stack.append(node)
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
			stack.append(node)