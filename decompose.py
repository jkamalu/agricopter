# This module generates a complete cellular decomposition for a
# polygon, as a first step in the generation of a complete
# coverage path.

import shapely.affinity
from shapely.geometry import (Point, Polygon,
                              LineString, GeometryCollection,
                              MultiPolygon)
import pdb

class CellNode:
    def __init__(self, polygon):
        self.polygon = polygon
        self.children = []
        self.edges = []
        self.visited = False

    def add_child(self, cell_node):
        self.children.append(cell_node)

    def add_edge(self, edge):
        self.edges.append(edge)

class TrapNode:
    def __init__(self, polygon, parent):
        self.polygon = polygon
        self.parent = parent
        self.edges = []
        self.visited = False

    def add_edge(self, edge):
        self.edges.append(edge)

class Edge:
    def __init__(self, node_a, node_b, border_line=None):
        self.node_a = node_a
        self.node_b = node_b
        self.border_line = border_line

def decompose(field):
    """
    Generates boustrophedon decompositions of the given polygon,
    passing a line from left to right while rotating the polygon
    at all angles that are multiples of 15 degrees. Selects the
    "best" rotation angle based on a simple heuristic (described
    in the code below).

    Returns a tuple: (best_decomposition, angle)
     -- best_decomposition is a list of Polygon objects
        that represent the cells of the decomposition. These
        polygons will still be rotated by the given angle when
        they are returned. This makes the job of oxpath.py easier.
        However, the path should be rotated back to the correct
        orientation before it is actually used to generate a drone
        mission.
     -- angle is the angle by which the polygon was rotated in the
        best decomposition. It follows the convention of a unit
        circle (i.e. an increasing angle means rotating CCW). The
        polygon is rotated about the origin, Point(0, 0). In order
        to get the returned polygons back to their original
        orientation, they need to be rotated -angle degrees about
        (0, 0).
    """
    decompositions = []
    for angle in xrange(0, 180, 15):
        rotate_point = Point(0, 0)
        polygon = shapely.affinity.rotate(field, angle, origin=rotate_point)
        decomposition = decompose_helper(polygon)
        decompositions.append((decomposition, angle))

    # Choose the best decomposition, using the size of the
    # smallest polygon in the decomposition as a heuristic, and
    # attempting to maximize that heuristic.
    max_heuristic = 0
    for i in range(0, len(decompositions)):
        heuristic = smallest_polygon_area(decompositions[i][0])
        if heuristic > max_heuristic:
            max_heuristic = heuristic
            index = i

    finalCellNodes, finalAngle = decompositions[index]
    finalTrapNodes = []
    for cell_node in finalCellNodes:
        finalTrapNodes.extend(decompose_further(cell_node))

    return (finalCellNodes, finalTrapNodes, finalAngle)

def decompose_helper(polygon):
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
    # Assemble a list of all interior and exterior vertices
    coords = get_coords(polygon)

    # Create start_line and end_line
    start_line = get_start_line(polygon)
    end_line = get_end_line(polygon)

    # Sort the indices so that we consider the vertices closest to
    # the start line first, and the farthest vertices last. This
    # creates the effect of passing the line from left to right
    # through the polygon.
    sorted_indices = sort_indices(coords, start_line)

    cell_nodes = []
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
            continue

        # Create new cell(s) by slicing the polygon with a vertical
        # line at this point
        box = start_line.union(point).envelope
        new_polygon = box.intersection(polygon)
        if isinstance(new_polygon, Polygon):
            cell_nodes.append(CellNode(new_polygon))
        elif (isinstance(new_polygon, GeometryCollection) or
              isinstance(new_polygon, MultiPolygon)):
            for item in new_polygon:
                if isinstance(item, Polygon):
                    cell_nodes.append(CellNode(item))

        remainder_box = end_line.union(point).envelope
        polygon = polygon.intersection(remainder_box)

    return cell_nodes

def decompose_further(cell_node):
    cell_polygon = Polygon(cell_node.polygon)

    coords = get_coords(cell_polygon)
    
    start_line = get_start_line(cell_polygon)
    end_line = get_end_line(cell_polygon)
    
    sorted_indices = sort_indices(coords, start_line)

    trap_nodes = []
    for index in sorted_indices:
        point = Point(coords[index])

        box = start_line.union(point).envelope
        new_polygon = box.intersection(cell_polygon)

        if isinstance(new_polygon, Polygon):
            trap_node = TrapNode(new_polygon, parent=cell_node)
            cell_node.add_child(trap_node)
            trap_nodes.append(trap_node)
        elif (isinstance(new_polygon, GeometryCollection) or
              isinstance(new_polygon, MultiPolygon)):
            for item in new_polygon:
                if isinstance(item, Polygon):
                    trap_node = TrapNode(item, parent=cell_node)
                    cell_node.add_child(trap_node)
                    trap_nodes.append(trap_node)

        remainder_box = end_line.union(point).envelope
        cell_polygon = cell_polygon.intersection(remainder_box)
        
    return trap_nodes

def get_coords(polygon):
    coords = polygon.exterior.coords
    coords = coords[:-1] # last coord is a repeat of the first
    if len(coords) <= 2: return [] # this is a line, not a polygon
    for interior_ring in polygon.interiors:
        interior_coords = interior_ring.coords
        interior_coords = interior_coords[:-1]
        coords += interior_coords
    return coords

def get_start_line(polygon):
    minx, miny, maxx, maxy = polygon.bounds
    return LineString([(minx - 1, miny - 1),
                       (minx - 1, maxy + 1)])

def get_end_line(polygon):
    minx, miny, maxx, maxy = polygon.bounds
    return LineString([(maxx + 1, miny - 1),
                       (maxx + 1, maxy + 1)])

def sort_indices(indices, line):
    sorted_indices = range(0, len(indices))
    sorted_indices.sort(
        key=lambda index:
        Point(indices[index]).distance(line))
    return sorted_indices

def smallest_polygon_area(polygon_list):
    """
    Returns the area of the smallest polygon in the given list of
    polygons.
    """
    if len(polygon_list) == 0:
        # TODO: raise an exception here?
        return 0

    smallest_area = polygon_list[0].polygon.area
    for i in range(1, len(polygon_list)):
        if polygon_list[i].polygon.area < smallest_area:
            smallest_area = polygon_list[i].polygon.area

    return smallest_area