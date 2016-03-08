# This module generates an ox-style (boustrophedon) coverage
# path for a given polygonal cell.

from shapely.geometry import (Polygon, LineString, Point)
from heapq import heappush, heappop

# TODO: Figure out why I can't "from cellsequencer

import cellsequencer

def traversal_endpoints(polygon, path_radius, x, miny, maxy):
    line = LineString([(x, miny - 1), (x, maxy + 1)])
    intersection = line.intersection(polygon)

    # TODO: more intelligent error handling than an assert
    assert isinstance(intersection, LineString)

    # TODO: better handling of areas where there is not
    # enough vertical space in the field to safely pass the
    # drone
    if intersection.length <= path_radius * 2:
        point1 = intersection.interpolate(.5,
                                          normalized=True)
        point2 = point1
    else:
        point1 = intersection.interpolate(path_radius)
        point2 = intersection.interpolate(intersection.length
                                          - path_radius)

    if point1.y > point2.y:
        return (point1, point2)
    else:
        return (point2, point1)

def coverage_options(polygon, path_radius):
    minx, miny, maxx, maxy = polygon.bounds
    
    # TODO: better handling of areas where there is not
    # enough horizontal space in the field to safely pass the
    # drone
    xleft = minx + path_radius
    xcenter = (minx + maxx) / 2
    if xleft > xcenter:
        xleft = xcenter

    xright = xleft
    ntraversals = 1
    while (xright + path_radius * 2) <= (maxx - path_radius):
        xright += path_radius * 2
        ntraversals += 1

    upper_left, lower_left = traversal_endpoints(polygon,
                                                 path_radius,
                                                 xleft,
                                                 miny, maxy)
    upper_right, lower_right = traversal_endpoints(polygon,
                                                   path_radius,
                                                   xright,
                                                   miny, maxy)

    if ntraversals % 2 == 0:
        # Drone will end its coverage of this polygon at the same
        # y-position as where it started
        return [
            cellsequencer.SequenceElement(
                polygon, lower_left, lower_right, False, True),
            cellsequencer.SequenceElement(
                polygon, lower_right, lower_left, False, False),
            cellsequencer.SequenceElement(
                polygon, upper_left, upper_right, True, True),
            cellsequencer.SequenceElement(
                polygon, upper_right, upper_left, True, False)]
    else:
        # Drone will end its coverage at the opposite y-position
        # (i.e. start high, end low, or vice versa)
        return [
            cellsequencer.SequenceElement(
                polygon, lower_left, upper_right, False, True),
            cellsequencer.SequenceElement(
                polygon, upper_right, lower_left, True, False),
            cellsequencer.SequenceElement(
                polygon, upper_left, lower_right, True, True),
            cellsequencer.SequenceElement(
                polygon, lower_right, upper_left, False, False)]

class CellPath:
    """
    A coverage path for an individual cell.
    """
    def __init__(self, waypoints):
        self.waypoints = waypoints

class CompletePath:
    """
    A coverage path for an entire field, comprising a list of
    coverage paths for each of its cells.
    """
    def __init__(self, initial_cell):
        self.cells = [initial_cell] # list of CellPaths
        self.length = 0 # total length of connecting lines
                        # between cells (i.e. not including the
                        # distance spent covering each cell, just
                        # the distance going from one cell to
                        # the next one)

    def copy(self):
        """
        Return a copy of this CompletePath, using a shallow copy
        of the list of CellPaths.
        """
        path_copy = CompletePath(None)
        path_copy.cells = self.cells[:]
        path_copy.length = self.length
        return path_copy

    def add(self, cell):
        """
        Add a CellPath to the end of the list and update length.
        Precondition: there is at least one CellPath in the list.
        """
        added_length = self.cells[-1].waypoints[-1].distance(
            cell.waypoints[0])
        self.cells.append(cell)
        self.length += added_length

def generate_path(polygon, path_radius, start_top, start_left):
    minx, miny, maxx, maxy = polygon.bounds
    
    top_points = []
    bottom_points = []

    x = minx + path_radius
    while x <= maxx - path_radius:
        top, bottom = traversal_endpoints(polygon, path_radius,
                                          x, miny, maxy)
        top_points.append(top)
        bottom_points.append(bottom)
        x += path_radius * 2

    waypoints = []
    top_to_bottom = start_top
    if start_left:
        pop_index = 0 # pop leftmost point
    else:
        pop_index = -1 # pop rightmost point

    for i in range(0, len(top_points)):
        if top_to_bottom:
            waypoints.append(top_points.pop(pop_index))
            waypoints.append(bottom_points.pop(pop_index))
            top_to_bottom = False
        else:
            waypoints.append(bottom_points.pop(pop_index))
            waypoints.append(top_points.pop(pop_index))
            top_to_bottom = True

    # TODO: Deal correctly with cells that are too small for the
    # drone to pass through them. For the time being, just pass
    # through the center of the cell.
    if len(waypoints) == 0:
        waypoints.append(polygon.centroid)

    return waypoints

def generate_paths(polygon, path_radius):
    return [
        CellPath(generate_path(polygon, path_radius, True, True)),
        CellPath(generate_path(polygon, path_radius, True, False)),
        CellPath(generate_path(polygon, path_radius, False, True)),
        CellPath(generate_path(polygon, path_radius, False, False))
    ]

def generate_oxpath(stack, path_radius):
    # Generate all possible ox paths for each of the individual
    # cells (linear time), as CellPath objects. The indices of
    # stack and cell_paths are the same, i.e. the possible ox
    # paths for the cell at stack[i] are stored in a list at
    # cell_paths[i].
    cell_paths = []
    for elem in stack:
        if elem.first_visit:
            # record a list of the four possible ways to cover
            # this cell with an ox path
            cell_paths.append(generate_paths(elem.node.polygon,
                                             path_radius))
        else:
            # for now, if the cell has already been visited,
            # just pass through its centroid and continue
            # TODO: find an efficient path through the cell
            # that avoids obstacles
            centroid = elem.node.polygon.centroid
            cell_paths.append([ CellPath([centroid]) ])

    # Find a CompletePath that covers the field in the minimum
    # distance.
    heap = []
    for initial_cell in cell_paths[0]:
        heappush(heap, (0, CompletePath(initial_cell)))

    while True:
        priority, path = heappop(heap)
        index = len(path.cells)
        for cell in cell_paths[index]:
            new_path = path.copy()
            new_path.add(cell)
            if len(new_path.cells) == len(stack):
                return new_path
            heappush(heap, (new_path.length, new_path))
