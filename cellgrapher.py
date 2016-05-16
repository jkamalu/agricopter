# This module builds a graph which relates every polygon
# to those with with it shares a border, using a Node/
# Edge paradigm

from shapely.geometry import Polygon, LineString

from decompose import (CellNode, CellTrap, Edge)

def build_graph(cells):
	"""
	build_graph generates a graph to represent the relationship between every
	Polygon object in cells. Polygons which share a border share a common
	CellEdge instance.
	
	Accepts: cells, a list of CellNode or CellTrap instances as defined in decompose.py,
			 'visited' set to False and 'edges' still empty.
	Returns: a list of initialized CellNode or CellTrap instances representing a graph
			 of polygons and their shared borders.
	"""
	for cell_i in range(0, len(cells)):		
		for cell_j in range(cell_i + 1, len(cells)):
			# If the two parent nodes share a border, look to see if their
			# children share a border. This will be the only border they share
			# and therefore shared also among each parent
			compare_cell_nodes(cells[cell_i], cells[cell_j])

	return cells

def compare_cell_nodes(cell_node1, cell_node2):
	"""
	compare_cell_nodes() compares the intersection of the respective polygons of
	two CellNodes objects and, depending on the result of the comparison (do they
	share an edge), generates a CellEdge and adds it to each CellNode passed in.

	Accepts: cell_node1 and cell_node2, two CellNode objects meant to be compared.

	Returns: True if share a border, False otherwise.
	"""
	# Find the intersection of the two relevant Polygons. Originally
	# used the touching() method outlined in the shapely library but
	# touches returns true for Polygons which share just a point and 
	# not a full border.
	intersection = cell_node1.polygon.intersection(cell_node2.polygon)

	# If the intersection is an instance of a LineString i.e. if the
	# intersection between the two Polygons is a line and thus a bona
	# fide interior border
	if isinstance(intersection, LineString):

		# Create the edge and add the reference to the list of edges in each
		# relevant CellNode instance.
		edge = Edge(cell_node1, cell_node2)
		edge.border_line = intersection
		cell_node1.edges.append(edge)
		cell_node2.edges.append(edge)

		return True

	return False 

def debug_print_graph(cell_nodes):
	for parent in cell_nodes:
		parent_label = "\nPARENT : ({0:.4g}, {1:.4g})".format(parent.polygon.centroid.x, parent.polygon.centroid.y)
		print parent_label

		for child in parent.children:
			child_label = "\tCHILD : ({0:.10g}, {1:.10g})".format(child.polygon.centroid.x, child.polygon.centroid.y)
			print child_label
			for edge in child.edges:
				if child is edge.node_a:
					not_me = edge.node_b
				else:
					not_me = edge.node_a
				edge_label = "\t\tEDGE : ({0:.4g}, {1:.4g})".format(not_me.polygon.centroid.x, not_me.polygon.centroid.y)
				print edge_label

		for edge in parent.edges:
			if parent is edge.node_a:
				not_me = edge.node_b
			else:
				not_me = edge.node_a
			edge_label = "\tEDGE : ({0:.4g}, {1:.4g})".format(not_me.polygon.centroid.x, not_me.polygon.centroid.y)
			print edge_label