# This code was written as a trace of a java
# implementation found on github by Tushar Roy.
# See his header below

"""
/**
* Date 11/17/2015
* @author Tushar Roy
*
* Help Karp method of finding tour of traveling salesman.
*
* Time complexity - O(2^n * n^2)
* Space complexity - O(2^n)
*
* https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm
*/

Copyright 2015 Tushar Roy

"""

class Node:
	def __init__(self, load):
		self.load = load
		self.visited = False
		self.edges = []

class Edge:
	def __init__(self, node_a, node_b, weight=1):
		self.node_a = node_a
		self.node_b = node_b
		self.weight = weight

class NodeEdgeMatrix:
	def __init__(self, nodes):
		self.matrix = self.build_matrix(nodes)
		self.nodes = nodes

	def __getitem__(self, a):
		return self.matrix[a]	

	def __len__(self):
		return len(self.matrix)
		
	# Very inefficient method - need way to remember
	# the index of each node in 'nodes' so that
	# building matrix from edges is simpler
	def build_matrix(self, nodes):
		matrix = []
		num_nodes = len(nodes)
		for i in range(0, num_nodes):
			matrix.append([])
		for row in range(0, num_nodes):
			for col in range(0, num_nodes):
				if nodes[row] is nodes[col]:
					matrix[row].append(0)
					continue
				connected = False
				for edge in nodes[row].edges:
					if nodes[col] is edge.node_a or nodes[col] is edge.node_b:
						matrix[row].append(edge.weight)
						connected = True
				if connected is False:
					matrix[row].append(float("inf"))
		return matrix

class Vertex:
	def __init__(self, vertex, vertex_set):
		self.vertex = vertex
		self.vertex_set = vertex_set

	def __hash__(self):
		return hash((self.vertex, self.vertex_set))

	def __eq__(self, o):
		return self.vertex == o.vertex and self.vertex_set == o.vertex_set

	def __ne__(self, o):
		return not self.__eq__(o)

	def __str__(self):
		return "(%d, %s)" %(self.vertex, str(self.vertex_set))

def optimal_path(matrix):
	# Generate matrix, each cell representing an edge
	# between two nodes, as well as all possible
	# subsets not including 0
	subsets = generate_subsets(len(matrix))
	current_optimals = {}
	previous_optimals = {}

	# For each subset generated, loop through every 
	# index in matrix
	for subset in subsets:
		for current_index in range(1, len(matrix)):
			
			# Ignore the index if it is already in the
			# subset
			if current_index in subset:
				continue

			vertex = Vertex(current_index, frozenset(subset))
			subset_copy = set(subset)
			min_cost = float("inf")
			min_prev_index = 0
			
			# Of all possible previous indeces in subset, select
			# the one which yields the lowest cost
			for prev_index in subset:
				cost = (matrix[prev_index][current_index] + 
				get_current_cost(subset_copy, prev_index, current_optimals)) 
				if cost < min_cost:
					min_cost = cost
					min_prev_index = prev_index

			# If subset is the empty set, find direct distance
			# from the current index to the start index (0)
			if len(subset) == 0:
				min_cost = matrix[0][current_index]

			# Update dictionaries with minimum cost and
			# corresponding previous index for given index
			current_optimals[vertex] = min_cost
			previous_optimals[vertex] = min_prev_index

	# Create set of all indeces and copy it
	indeces = set()
	for index in range(1, len(matrix)):
		indeces.add(index)
	indeces_copy = set(indeces)

	min_cost = float("inf")
	min_prev_index = -1

	# Of all possible indeces in matrix, select the
	# one which yields the lowest cost
	for index in indeces:
		cost = matrix[index][0] + get_current_cost(indeces_copy, index, current_optimals) 
		if cost < min_cost:
			min_cost = cost
			min_prev_index = index

	# The final step
	vertex = Vertex(0, frozenset(indeces))
	previous_optimals[vertex] = min_prev_index
	return min_cost

def get_current_cost(subset, index, current_optimals):
	subset.remove(index)
	vertex = Vertex(index, frozenset(subset))
	subset.add(index)
	current_cost = current_optimals.get(vertex)
	return current_cost

def generate_subsets(num_indeces):
	subsets = []
	indeces = []
	for i in range(1, num_indeces):
		indeces.append(i)
	generate_subsets_helper(set(), indeces, subsets) 
	return sorted(subsets, key=lambda subset: len(subset))	

def generate_subsets_helper(subset, indeces, subsets):
	if len(indeces) == 0:
		subsets.append(subset)
	else:
		temp_set = set(subset)
		temp_indeces = list(indeces)
		temp_set.add(temp_indeces.pop(0))
		generate_subsets_helper(temp_set, temp_indeces, subsets)
		generate_subsets_helper(subset, temp_indeces, subsets)
