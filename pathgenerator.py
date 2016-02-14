# This module generates a complete coverage path for a field
# defined by an arbitrary polygon

import shapely.affinity
from shapely.geometry import (Point, Polygon,
                              LineString, GeometryCollection,
                              MultiPolygon)
import pdb

def decompose(polygon):
    return decompose_helper(polygon, angle=-30)

def decompose_helper(polygon, angle=0):
    """
    Decomposes the given Polygon into cells that can be easily
    covered by a simple, "ox-like" path. Returns a list of the
    decomposed cells (as Polygons).

    In order to generate the boustrophedon decomposition, this
    function passes a line from left to right through the given
    Polygon. The angle parameter can be modified in order
    to pass the line in a different direction (0 <= angle < 365).
    """
    # copy the polygon, since we will destructively modify it
    polygon = Polygon(polygon)

    # Rotate. We undo this rotation at the end of the function.
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
            # consider it as a critical point.
            continue

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
    
    # Undo rotation for all of the cells
    for i in xrange(0, len(cells)):
        cells[i] = shapely.affinity.rotate(cells[i], -angle,
                                           origin=rotate_point)
    return cells
