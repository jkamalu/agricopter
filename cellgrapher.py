# This module builds a graph which relates every polygon
# to those with with it shares a border, using a Node/
# Edge paradigm

from shapely.geometry import Polygon, LineString

class CellNode:
	def __init__(self, polygon):
		self.polygon = polygon
		self.visited = False
		self.edges = []

class CellEdge:
	def __init__(self, node_a, node_b, weight=1, border_line=None):
		self.node_a = node_a
		self.node_b = node_b
		self.weight = weight
		self.border_line = border_line

def build_graph(cells):
	"""
	build_graph generates a graph to represent the relationship between every
	Polygon object in cells. Polygons which share a border share a common
	CellEdge instance.
	
	Accepts: cells, a list of Polygon instances as defined in the shapely
			 geometry library.
	Returns: a list of initialized CellNode instances representing a graph
			 of polygons and their interior borders.
	"""
	nodes = []
	for cell in cells:
		nodes.append(CellNode(cell))
	
	for i in range(0, len(cells)):
		for j in range(i + 1, len(cells)):

			# Find the intersection of the two relevant Polygons. Originally
			# used the touching() method outlined in the shapely library but
			# touches returns true for Polygons which share just a point and 
			# not a full border.
			intersection = nodes[i].polygon.intersection(nodes[j].polygon)

			# If the intersection is an instance of a LineString i.e. if the
			# intersection between the two Polygons is a line and thus a bona
			# fide interior border
			if isinstance(intersection, LineString):

				# Create the edge and add the reference to the list of edges in each
				# relevant CellNode instance.
				edge = CellEdge(nodes[i], nodes[j])
				edge.border_line = intersection
				nodes[i].edges.append(edge)
				nodes[j].edges.append(edge)

	return nodes




