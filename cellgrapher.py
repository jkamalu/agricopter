# This module builds a graph which relates each
# polygon in terms of its neighbors with which
# it shares a border

from shapely.geometry import Polygon

class CellNode:
	def __init__(self, polygon):
		self.polygon = polygon
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

	print "loop runs for %d loops" %(len(cells))
	for i in range(0, len(cells)):
		print "OUTER LOOP"
		for j in range(i + 1, len(cells)):
			print "INNER LOOP"
			if nodes[i].polygon.touches(nodes[j].polygon):
				print "cell %d touches cell %d" %(i, j)
				edge = CellEdge(nodes[i], nodes[j])
				nodes[i].edges.append(edge)
				nodes[j].edges.append(edge)
			else:
				print "cell %d does not touch cell %d" %(i, j)
	return nodes