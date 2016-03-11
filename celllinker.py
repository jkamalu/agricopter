# This module finds for a graph of cells
# the optimal complete covereage path for
# the drone, crossing from cell to cell only
# by existing edges

# This code performs but doesn't serve our
# purposes. AKA it cannot retrace its steps
# through already visited champs.

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

from cellgrapher import (GraphMeta, CellNode, CellEdge)

import shapely
from shapely.geometry import Polygon

import parsepolygon
from decompose import decompose
from cellgrapher import build_graph


class StackElem:
    def __init__(self, node, first_visit):
        self.node = node
        self.first_visit = first_visit

class Matrix:
	def __init__(self, nodes):
		self.matrix = self.build_node_matrix(nodes)
		self.nodes = nodes

	def __getitem__(self, a):
		return self.matrix[a]	
		
	# Very inefficient method - need way to remember
	# the index of each node in 'nodes' so that
	# building matrix from edges is simpler
	def build_node_matrix(self, nodes):
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
		print "\nMATRIX\n"
		for row in matrix:
			print row
		return matrix

class Index:
	def __init__(self, index, index_set):
		self.index = index
		self.index_set = index_set

	def __hash__(self):
		return hash((self.index, self.index_set))

	def __eq__(self, o):
		return self.index == o.index and self.index_set == o.index_set

	def __ne__(self, o):
		return not self.__eq__(o)

	def __str__(self):
		return "(%d, %s)" %(self.index, str(self.index_set))

def optimal_path(graph_meta):
	"""
	Accepts:
	Returns:
	Note: node refers here to the index of a node in the matrix.

	"""

	# Generate matrix, each cell representing an edge
	# between two CellNode's, as well as all possible
	# subsets not including 0
	matrix = Matrix(graph_meta.nodes)
	subsets = generate_subsets(graph_meta.node_count)
	current_optimals = {}
	previous_optimals = {}

	# For each subset generated, loop through every 
	# node in matrix
	for subset in subsets:
		print "SUBSET", subset
		for current_node in range(1, graph_meta.node_count):
			
			print "CURRENT NODE", current_node
			# Ignore the node if it is already in the
			# subset
			if current_node in subset:
				continue

			index = Index(current_node, frozenset(subset))
			subset_copy = set(subset)
			min_cost = float("inf")
			min_prev_node = 0
			
			# Of all possible previous nodes in subset, select
			# the one which yields the lowest cost
			for prev_node in subset:
				print "PREVIOUS NODE", prev_node
				cost = matrix[prev_node][current_node] + get_current_cost(subset_copy, prev_node, current_optimals) 
				if cost < min_cost:
					min_cost = cost
					min_prev_node = prev_node

			# If subset is the empty set, find direct distance
			# from the current node to the start node (0)
			if len(subset) == 0:
				min_cost = matrix[0][current_node]

			# Update dictionaries with minimum cost and
			# corresponding previous node for given index
			current_optimals[index] = min_cost
			previous_optimals[index] = min_prev_node

	# Create set of all node indeces and copy it
	nodes = set()
	for i in range(1, graph_meta.node_count):
		nodes.add(i)
	nodes_copy = set(nodes)

	min_cost = float("inf")
	prev_node = -1

	# Of all possible nodes in matrix, select the
	# one which yields the lowest cost
	for node in nodes:
		cost = matrix[node][0] + get_current_cost(nodes_copy, node, current_optimals) 
		if cost < min_cost:
			min_cost = cost
			prev_node = node

	index = Index(0, frozenset(nodes))
	previous_optimals[index] = prev_node
	print "MIN COST = ", min_cost
	return min_cost

def get_current_cost(subset, node_index, current_optimals):
	subset.remove(node_index)
	new_index = Index(node_index, frozenset(subset))
	subset.add(node_index)
	current_cost = current_optimals.get(new_index)
	print ""
	for key in current_optimals:
		print key,"->", current_optimals[key]
	print ""
	print "get_current_cost searching for", new_index
	print "get_current_cost returns", current_cost
	return current_cost

#########################################################################

def generate_subsets(node_count):
	subsets = []
	indeces = []
	for i in range(node_count):
		indeces.append(i)
	generate_subsets_helper(set(), indeces, subsets) 
	print "\nSUBSETS\n\n", subsets, "\n"
	return sorted(subsets, key=lambda subset: len(subset))	

def generate_subsets_helper(subset, indeces, subsets):
	if len(indeces) == 1:
		subsets.append(subset)
	else:
		temp_set = set(subset)
		temp_indeces = list(indeces)
		temp_set.add(temp_indeces.pop(1))
		generate_subsets_helper(temp_set, temp_indeces, subsets)
		generate_subsets_helper(subset, temp_indeces, subsets)

#########################################################################

if __name__ == '__main__':

	INPUT_FILE = "test_fields/test2.txt"
	DRONE_RADIUS = .1

	polygon = parsepolygon.parse_polygon(INPUT_FILE)
	cells = decompose(polygon)[0]
	meta = build_graph(cells)
	optimal = optimal_path(meta)

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

