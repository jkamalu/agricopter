# This module finds for a graph of cells
# the optimal complete covereage path for
# the drone, crossing from cell to cell only
# by existing edges

from cellgrapher import (GraphMeta, CellNode, CellEdge)

class StackElem:
    def __init__(self, node, first_visit):
        self.node = node
        self.first_visit = first_visit

class Matrix:
	def __init__(self, nodes):
		self.matrix = build_node_matrix(nodes)
		self.nodes = nodes
		
	# Very inefficient method - need way to remember
	# the index of each node in 'nodes' so that
	# building matrix from edges is simpler
	def build_node_matrix(nodes):
		matrix = []
		for i in range(0, len(nodes)):
			matrix.append([])
		for i in range(0, len(nodes)):
			for j in range(0, len(nodes)):
				if nodes[i] is nodes[j]:
					matrix[i].append(0)
					continue
				connected = False
				for edge in nodes[i].edges:
					if nodes[j] is edge.node_a or nodes[j] is edge.node_b:
						matrix[i].append(edge.weight)
						connected = True
				if connected is False:
					matrix[i].append(float("inf"))
		return matrix

class Index:
	def __init__(self, index, index_set):
		self.index = index
		self. index_set = index_set

def optimal_path(graph_meta):
	matrix = Matrix(graph_meta.nodes)
	current_optimals = {}
	previous_optimals = {}
	subsets = generate_subsets(graph_meta.node_count)

def generate_subsets(node_count):
	subsets = []
	indeces = []
	for i in range(node_count):
		indeces.append(i)
	generate_subsets_helper(set(), indeces, subsets) 
	return subsets	

def generate_subsets_helper(subset, indeces, subsets):
	if len(indeces) == 0:
		subsets.append(subset)
	else:
		temp_set = set(subset)
		temp_indeces = list(indeces)
		temp_set.add(temp_indeces.pop(0))
		generate_subsets_helper(temp_set, temp_indeces, subsets)
		generate_subsets_helper(subset, temp_indeces, subsets)




































#########################################################################

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
	print generate_subsets(3)
