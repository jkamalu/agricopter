# This module generates an ox-style (boustrophedon) coverage path
# for a field that has already been decomposed and linked into an
# ordered list of cells.

from shapely.geometry import Point, LineString, LinearRing
from heapq import heappush, heappop # priority queue

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

    def add(self, cell):
        """
        Add a CellPath to the end of the list and update length.
        Precondition: there is at least one CellPath in the list.
        """
        added_length = self.cells[-1].waypoints[-1].distance(
            cell.waypoints[0])
        self.cells.append(cell)
        self.length += added_length

    def copy(self):
        """
        Return a copy of this CompletePath, using a shallow copy
        of the list of CellPaths.
        """
        path_copy = CompletePath(None)
        path_copy.cells = self.cells[:]
        path_copy.length = self.length
        return path_copy

def traversal_endpoints(polygon, x, miny, maxy):
    line = LineString([(x, miny - 1), (x, maxy + 1)])
    intersection = line.intersection(polygon)

    if not isinstance(intersection, LineString):
        # This should never happen, since traversal endpoints
        # are only calculated for x-values between the minx
        # and maxx for the polygon, but we check just in case.
        # TODO: print a warning message.
        return None, None

    endpoints = intersection.boundary
    return (min(endpoints, key=lambda point: point.y),
            max(endpoints, key=lambda point: point.y))

def generate_cell_path(bottoms, tops, start_top, start_left):
    waypoints = []
    top_to_bottom = start_top
    if start_left:
        indices = range(0, len(bottoms))
    else:
        indices = range(len(bottoms) - 1, -1, -1)

    for i in indices:
        if top_to_bottom:
            waypoints += [tops[i], bottoms[i]]
        else:
            waypoints += [bottoms[i], tops[i]]

        top_to_bottom = not top_to_bottom

    return CellPath(waypoints)

def possible_paths(polygon, path_radius):
    centroid = polygon.centroid

    # erode polygon (pull the edges inward) to ensure that drone
    # does not fly too close to the edge
    polygon = polygon.buffer(-path_radius)
    if not isinstance(polygon.exterior, LinearRing):
        # Polygon no longer exists, meaning it was too small for
        # the drone to pass through it. For now just pass through
        # the centroid and move on.
        return CellPath([centroid])

    minx, miny, maxx, maxy = polygon.bounds
    bottoms = []
    tops = []

    x = minx
    while x <= maxx:
        bottom, top = traversal_endpoints(polygon, x, miny, maxy)
        if bottom != None:
            bottoms.append(bottom)
            tops.append(top)
        x += path_radius * 2

    if len(bottoms) == 0:
        # This should theoretically not happen but we include it
        # just in case.
        # TODO: print a warning message.
        return CellPath([centroid])

    return [
        generate_cell_path(bottoms, tops, True, True),
        generate_cell_path(bottoms, tops, True, False),
        generate_cell_path(bottoms, tops, False, True),
        generate_cell_path(bottoms, tops, False, False)
    ]

def generate_path(stack, path_radius):
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
            cell_paths.append(possible_paths(elem.node.polygon,
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
