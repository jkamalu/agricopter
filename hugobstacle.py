# This module inserts into the cell sequence a path 
# which navigates around an obstacle which juts out
# from the field's side.

from shapely.geometry import Polygon
from cellsequencer import SequenceElement

def round_obstacle(self, polygon, start_elem, end_elem, radius, ccw=True):
	"""
	Accepts two SequenceElement points which surround
	a polygon as well as the distance from and direction 
	around which the drone should travel.

	Updates the SequenceElement start_elem with new
	distance_to_end that includes the path around and
	returns list of Point objects.
	"""

	# method to find closest point on polygon to some other point
	# http://stackoverflow.com/questions/33311616/find-coordinate-of-closest-point-on-polygon-shapely

	# assumes polygon is cww oriented

	vertices = polygon.exterior.coords
	polygon_ring = LinearRing(vertices)

	start_point = start_elem.end
	start_point_on_polygon = polygon_ring.interpolate(polygon_ring.project(start_point))

	first_vertex = None 
	for i in range(0, len(vertices) - 1):
		if LineString(vertices[i], vertices[i +1]).contains(start_point_on_polygon)
			if cww:
				first_vertex = vertices[i + 1]
			else:
				first_vertex = vertices[i]

	end_point = end_elem.start
	end_point_on_polygon = polygon_ring.interpolate(polygon_ring.project(end_point))

	last_vertex = None
	for i in range(0, len(vertices) - 1):
		if LineString(vertices[i], vertices[i +1]).contains(end_point_on_polygon)
			if cww:
				last_vertex = vertices[i]
			else:
				last_vertex = vertices[i + 1]

	if first_vertex is None or last_vertex is None:
		return []

	