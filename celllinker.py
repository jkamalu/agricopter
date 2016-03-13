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

# A wrapper class to keep track of whether a node needs
# to be given a coverage path on its first pass-through
# with the drone
class StackElem:
    def __init__(self, node, first_visit):
        self.node = node
        self.first_visit = first_visit

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
			optimal_helper(node, stack, len(graph_nodes))

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

def optimal_helper(node, stack, to_visit):
	"""
	This is the recursive method in the optimal/optimal_helper method pair.
	Accepts: node - the CellNode from which to start searching for the 
			 coverage path.
			 stack - an empty list meant to hold the complete coverage path.
			 to_visit - the total number of cells which have yet to be found
			 by the algorithm.
	Alters: stack - (1) every time a node which has not been visited is found
					(2) every time the path must backtrack because it has
						reached a dead end
	"""
	# We've found an unvisited node, so mark it as visited and
	# append a new StackElem instance to the stack indicating that
	# this is the first time the node has been visited.
	node.visited = True
	stack.append(StackElem(node, first_visit=True))

	# Base case: every single node has been visited at least once.
	if to_visit == 0:
		return None

	# For the current node, shuffle its edges to simulate, in
	# conjunction with multiple passes from the same starting 
	# node, an exhaustive search.
	shuffle(node.edges)

	# For each of the current node's edges, i.e. for each of the
	# current node's neighbors, determine whether to visit and 
	# recur, or to skip and move on to the next neighbor.
	for edge in node.edges:
		next_node = get_neighbor(node, edge)

		# Recursive case: if the node has never been visited before,
		# recurse with next_node as the base node and with to_visit 
		# indicating that there is one less node to visit. 
		if next_node.visited is False:
			optimal_helper(next_node, stack, to_visit - 1)

			# optimal_helper() returns in two cases, (1) when every node
			# has been visited and (2) when a node no longer has any
			# unvisited neighbors. These additions to the stack are all
			# node revisits and/or the path back home.
			stack.append(StackElem(node, first_visit=False))

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
