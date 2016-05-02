# This module generates a complete cellular decomposition for a
# polygon, as a first step in the generation of a complete
# coverage path.

import shapely.affinity
from shapely.geometry import (Point, Polygon,
                              LineString, GeometryCollection,
                              MultiPolygon)
import pdb

class Cell:
    def __init__(self, polygon, parent = None):
        self.polygon = polygon
        self.parent = parent
        self.children = []

    def add_child(self, cell):
        self.children.append(cell)

def decompose(polygon):
    """
    Generates boustrophedon decompositions of the given polygon,
    passing a line from left to right while rotating the polygon
    at all angles that are multiples of 15 degrees. Selects the
    "best" rotation angle based on a simple heuristic (described
    in the code below).

    Returns a tuple: (best_decomposition, angle, rotate_point)
     -- best_decomposition is a list of Polygon objects
        that represent the cells of the decomposition. These
        polygons will still be rotated by the given angle when
        they are returned. This makes the job of oxpath.py easier.
        However, the path should be rotated back to the correct
        orientation before it is actually used to generate a drone
        mission.
     -- angle is the angle by which the polygon was rotated in the
        best decomposition. It follows the convention of a unit
        circle (i.e. an increasing angle means rotating CCW).
     -- rotate_point is the point about which the polygon was
        rotated. In order to get the returned polygons back to
        their original orientation, they need to be rotated
        -angle degrees about the rotate_point.
    """
    decompositions = []
    for angle in xrange(0, 180, 15):
        decomposition = decompose_helper(polygon, angle)
        decompositions.append((decomposition[0], angle,
                               decomposition[1]))

    # Choose the best decomposition, using the size of the
    # smallest polygon in the decomposition as a heuristic, and
    # attempting to maximize that heuristic.
    max_heuristic = 0
    for i in range(0, len(decompositions)):
        heuristic = smallest_polygon_area(decompositions[i][0])
        if heuristic > max_heuristic:
            max_heuristic = heuristic
            index = i

    return decompositions[index]

def decompose_helper(polygon, angle=0):
    """
    Decomposes the given Polygon into cells that can be easily
    covered by a simple, "ox-like" path.

    In order to generate the boustrophedon decomposition, this
    function passes a line from left to right through the given
    Polygon. The angle parameter can be modified in order
    to rotate the polygon before passing the line.

    Returns a tuple: (list, rotate_point)
     -- where list is a list of the decomposed cells (as Polygons)
     -- and rotate_point is the point about which the polygon was
        rotated. Note that the decomposed cells will still be
        rotated about this point when they are returned.
    """
    # copy the polygon, since we will destructively modify it
    polygon = Polygon(polygon)

    # Rotate
    rotate_point = polygon.representative_point()
    polygon = shapely.affinity.rotate(polygon, angle,
                                      origin=rotate_point)

    # Assemble a list of all interior and exterior vertices
    coords = polygon.exterior.coords
    coords = coords[:-1] # last coord is a repeat of the first
    if len(coords) <= 2: return [] # this is a line, not a polygon
    for interior_ring in polygon.interiors:
        interior_coords = interior_ring.coords
        interior_coords = interior_coords[:-1]
        coords += interior_coords

    minx, miny, maxx, maxy = polygon.bounds
    start_line = LineString([(minx - 1, miny - 1),
                             (minx - 1, maxy + 1)])
    end_line = LineString([(maxx + 1, miny - 1),
                           ( maxx + 1, maxy + 1)])

    # Sort the indices so that we consider the vertices closest to
    # the start line first, and the farthest vertices last. This
    # creates the effect of passing the line from left to right
    # through the polygon.
    sorted_indices = range(0, len(coords))
    sorted_indices.sort(
        key=lambda index:
        Point(coords[index]).distance(start_line))

    cells = []
    for index in sorted_indices:
        point = Point(coords[index])
        dist = point.distance(start_line)

        prev_index = (index - 1) % len(coords)
        prev_point = Point(coords[prev_index])
        prev_dist = prev_point.distance(start_line)

        next_index = (index + 1) % len(coords)
        next_point = Point(coords[next_index])
        next_dist = next_point.distance(start_line)

        if ((prev_dist < dist and next_dist > dist) or
            (prev_dist > dist and next_dist < dist)):
            # A basic ox-like path can pass by this vertex without
            # a problem (it is a MIDDLE event), so we do not
            # need to consider it as a critical point. However, for now
            # it is more convenient to only have trapezoidal cells, so we
            # consider all points to be critical points. To change this,
            # replace "pass" with "continue".
            cut_cell = True


        if (cut_cell):

        # Create new cell(s) by slicing the polygon with a vertical
        # line at this point
        box = start_line.union(point).envelope
        new_cell = box.intersection(polygon)
        if isinstance(new_cell, Polygon):
            cells.append(new_cell)
        elif (isinstance(new_cell, GeometryCollection) or
              isinstance(new_cell, MultiPolygon)):
            for item in new_cell:
                if isinstance(item, Polygon):
                    cells.append(item)

        remainder_box = end_line.union(point).envelope
        polygon = polygon.intersection(remainder_box)
    

    return (cells, rotate_point)

def smallest_polygon_area(polygon_list):
    """
    Returns the area of the smallest polygon in the given list of
    polygons.
    """
    if len(polygon_list) == 0:
        # TODO: raise an exception here?
        return 0

    smallest_area = polygon_list[0].area
    for i in range(1, len(polygon_list)):
        if polygon_list[i].area < smallest_area:
            smallest_area = polygon_list[i].area

    return smallest_area
