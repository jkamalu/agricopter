# This module generates an ox-style (boustrophedon) coverage path
# for a field that has already been decomposed and linked into an
# ordered list of cells.

from shapely.geometry import Point, LineString
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

def average_z(polygon):
    """
    Determine the average z value of the vertices of the polygon.
    Used as a (very rough) approximation for the z value of the
    centroid of that polygon.
    """
    exterior = polygon.exterior.coords[:-1]
    total = sum([point[2] for point in exterior])
    return total / len(exterior)

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

def generate_cell_path(polygon, path_radius,
                       start_top, start_left):
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
        centroid = polygon.centroid
        waypoints.append(Point(centroid.x, centroid.y,
                               average_z(polygon)))

    return CellPath(waypoints)

def possible_paths(polygon, path_radius):
    return [
        generate_cell_path(polygon, path_radius, True, True),
        generate_cell_path(polygon, path_radius, True, False),
        generate_cell_path(polygon, path_radius, False, True),
        generate_cell_path(polygon, path_radius, False, False)
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
            centroid = Point(centroid.x, centroid.y,
                             average_z(elem.node.polygon))
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
