# This module finds for a graph of cells
# the ______  complete covereage path for
# the drone, crossing from cell to cell only
# by existing edges

import time
from random import shuffle

import shapely
from shapely.geometry import Polygon

import parsepolygon
import decompose
import cellgrapher

TOTAL_TIME = 5

class StackElem:
    def __init__(self, node, first_visit):
        self.node = node
        self.first_visit = first_visit

def optimal(graph_meta):
	stacks = []
	time_per_node = TOTAL_TIME / float(graph_meta.node_count)
	for node in graph_meta.nodes:
		found_path = False
		start_time = time.time()
		while (time.time() - start_time) < time_per_node or not found_path:
			stack = []
			optimal_helper(node, stack, graph_meta.node_count)
			optimal_cleanup(graph_meta.nodes)
			stacks.append(stack)
			found_path = True
		print time.time() - start_time
	min_stack = float("inf")
	final_stack = []
	for stack in stacks:
		if len(stack) < min_stack:
			min_stack = len(stack)
			final_stack = stack
	return final_stack

def optimal_helper(node, stack, to_visit):
	node.visited = True
	stack.append(StackElem(node, first_visit=True))
	if to_visit == 0:
		return None
	shuffle(node.edges)
	for edge in node.edges:
		next_node = None
		if edge.node_a == node:
			next_node = edge.node_b
		else:
			next_node = edge.node_a
		if next_node.visited is False:
			optimal_helper(next_node, stack, to_visit - 1)
			stack.append(StackElem(node, first_visit=False))

def optimal_cleanup(nodes):
	for node in nodes:
		node.visited = False

