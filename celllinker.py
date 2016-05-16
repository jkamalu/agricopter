# This module finds for a graph of cells a
# relatively optimized complete covereage path
# for the drone, crossing from cell to cell
# only by existing edges

import time
from random import shuffle

import shapely
from shapely.geometry import Polygon

import parsepolygon
import decompose
import cellgrapher

# The total amount of time the algorithm will have to 
# split between each start point i.e. each node in the
# graph
TOTAL_TIME = 5

def optimal(graph_nodes):
	"""
	This is the wrapper method in the optimal/optimal_helper method pair.
	optimal(), given a graph of nodes and edges, will determine at least
	one complete coverage path starting at each node, and at each fork
	randomly shuffles the edges so as to simulate an exhaustive search in
	lieu of a fully polished algorithm. It returns the shortest of all
	paths where length is the number of elements in each list.

	Accepts: a list of CellNode objects as defined in cellgrapher.py
	Returns: a list of StackElem objects as defined here above that
			 may be followed by the drone in that order, unless 
			 further optimizations in oxpath.py or some other such
			 file are made.

	TODO: Consider possibility of making 'stacks' a set and each 'stack'
		  an immutable and thus hashable tuple
	"""
	stacks = []

	# the minimum amount of time the algorithm is given with
	# each node to find complete coverage paths
	time_per_node = TOTAL_TIME / float(len(graph_nodes))

	# For each node in graph_nodes, find as many coverage
	# paths as possible and add them to stacks
	for node in graph_nodes:

		# found_path: to keep track of whether or not at least one 
		# path has been found for this iteration's node
		# start_time: to keep track of how much of the time alloted
		# to this iteration's node has passed
		found_path = False
		start_time = time.time()

		# While this iteration's node still has some time left and 
		# while no complete coverage path has yet to be found for this
		# node
		while (time.time() - start_time) < time_per_node or not found_path:
			stack = []
			optimal_helper(node, stack)

			# Mark every node visited = False for further iterations and
			# coverage paths
			optimal_cleanup(graph_nodes)
			stacks.append(stack)
			found_path = True

	# Initialize variables in preparation to find the minimum
	# stack in stacks.
	min_stack = float("inf")
	final_stack = []

	# Find the shortest stack in stacks, giving certain preference 
	# to the stacks which begin with graph_nodes[0]
	for stack in stacks:
		if len(stack) < min_stack or (len(stack) == min_stack and stack[0] is graph_nodes[0]):
			min_stack = len(stack)
			final_stack = stack

	return final_stack

def optimal_helper(node, stack):
	"""
	This is the recursive method in the optimal/optimal_helper method pair.
	Accepts: node - the CellNode from which to start searching for the 
			 coverage path.
			 stack - an empty list meant to hold the complete coverage path
	Alters:  stack - every time a node which has not been visited is found
	Returns: The number of times the path passes back through a cell that
	         had already been visited (note that these extraneous passes
	         through cells are NOT added to the stack). This includes passing
	         through cells to return to the starting position.
	"""
	# We've found an unvisited node, so mark it as visited and
	# append it to the stack
	node.visited = True
	stack.append(node)

	# For the current node, shuffle its edges to simulate, in
	# conjunction with multiple passes from the same starting 
	# node, an exhaustive search.
	shuffle(node.edges)

	extraneous_visits = 0

	# For each of the current node's edges, check if the corresponding
	# neighbor has been visited. If it hasn't, call optimal_helper()
	# recursively on that neighbor.
	for edge in node.edges:
		next_node = get_neighbor(node, edge)

		# If the node has never been visited before, recurse with
		# next_node as the base node
		if next_node.visited is False:
			extraneous_visits += optimal_helper(next_node, stack)

			# The path passes back through this cell, either as a transition
			# to another unvisited cell or as part of the return home.
			extraneous_visits += 1

	# Note that optimal_helper() will only return when this node has no
	# unvisited neighbors. If this is the outermost call to optimal_helper(),
	# every node in the graph has been visited.
	return extraneous_visits

# Utility method to mark each node as visited = False.
def optimal_cleanup(nodes):
	for node in nodes:
		node.visited = False

# Utility method to determine which node referenced in edge
# is a neighbor to the passed in node.
def get_neighbor(node, edge):
	if edge.node_a == node:
		return edge.node_b
	else:
		return edge.node_a
