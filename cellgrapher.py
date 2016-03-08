# This module builds a graph which relates each
# polygon in terms of its neighbors with which
# it shares a border

from shapely.geometry import Polygon, LineString

class GraphMeta:
	def __init__(self, start, node_count, nodes):
		self.start = start
		self.node_count = node_count
		self.nodes = nodes

class CellNode:
	def __init__(self, polygon):
		self.polygon = polygon
		self.visited = False
		self.edges = []

class CellEdge:
	def __init__(self, node_a, node_b, border_line=None):
		self.node_a = node_a
		self.node_b = node_b
		self.border_line = border_line

def build_graph(cells):
	"""
	Accepts a list of Polygon objects and relies on the accuracy of the
	shapely geometry library to generate a graph relating each Polygon
	to its direct neighbors through a node/edge paradigm.

	Returns the aforementioned graph referenced by a CellNode representing
	the first Polygon in the original list of Polygons
	"""

	nodes = []

	for cell in cells:
		nodes.append(CellNode(cell))

	for i in range(0, len(cells)):
		for j in range(i + 1, len(cells)):
			intersection = nodes[i].polygon.intersection(nodes[j].polygon)
			if isinstance(intersection, LineString):
				edge = CellEdge(nodes[i], nodes[j])
				nodes[i].edges.append(edge)
				nodes[j].edges.append(edge)

	meta = GraphMeta(nodes[0], len(nodes), nodes)

	return meta
