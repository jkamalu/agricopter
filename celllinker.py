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
	final_stack = []
	for each in graph_meta.nodes:
		print each.polygon.centroid
	optimal_helper(graph_meta.nodes, graph_meta.start, [], graph_meta.node_count, final_stack)
	for each in final_stack:
		print each.node.polygon.centroid
	return final_stack

def optimal_helper(nodes, root, stack, to_visit, final_stack):
	root.visited = True
	stack.append(StackElem(root, first_visit=True))
	if to_visit == 0:
		to_visit = len(nodes)
		return None

	# Go through each permutation of edges, example
	# being [1, 2, 3], [1, 3, 2], [2, 1, 3]
	#       [2, 3, 1], [3, 1, 2], [3, 2, 1]
	permutations = permute(root.edges)
	print "Num permutations:", len(permutations)
	for edge_permutation in permutations:
		
		# Go through each edge in the permutation and 
		for edge in edge_permutation:
			next_node = get_neighbor(root, edge)
			if next_node.visited is False:
				optimal_helper(nodes, next_node, stack, to_visit - 1, final_stack)
				
				# Should only be called for the retourn
				# journey back to the home node
				stack.append(StackElem(root, first_visit=False))

		print "\nStack found len():", len(stack)
		if len(stack) < len(final_stack) or len(final_stack) == 0:
			final_stack[:] = stack
		print "Final len():      ", len(final_stack)

		# Reset relevant values in case that recursion 
		# continues
		for node in nodes:
			node.visited = False
		del stack[:]

def get_neighbor(node, edge):
	if edge.node_a == node:
		return edge.node_b
	else:
		return edge.node_a

# only edges that border something not visited
def permute(edges):
	permutations = []
	permute_helper(edges, [], permutations)
	return permutations

def permute_helper(to_go, so_far, permutations):
	if len(to_go) == 0:
		permutations.append(so_far)
		return
	for i in range(0, len(to_go)):
		copy_to_go = list(to_go)
		copy_so_far = list(so_far)
		copy_so_far.append(copy_to_go.pop(i))
		permute_helper(copy_to_go, copy_so_far, permutations)

if __name__ == "__main__":
	string = list("doy")
	for item in permute(string):
		print "\n", item
