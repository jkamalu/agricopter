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
        self.transition = [] # waypoints to move to the next cell

    def start_point(self):
        return self.waypoints[0]
    
    def add_transition(self, target_point, this_node, next_node):
        if next_node == None:
            self.transition.append(target_point)
            return

        # find the edge between this cell and the next
        for edge in this_node.edges:
            if (edge.node_a == next_node or
                edge.node_b == next_node):
                break
        else:
            raise Exception('No edge found between this node '
                            'and next node in stack')

        border = edge.border_line
        passing_point = border.interpolate(border.project(
                                                   target_point))
        if this_node.eroded != None:
            exterior = this_node.eroded.exterior
            point = exterior.interpolate(exterior.project(
                                                  passing_point))
            self.transition.append(point)

        if next_node.eroded == None:
            self.transition.append(next_node.polygon.centroid)
        else:
            exterior = next_node.eroded.exterior
            point = exterior.interpolate(exterior.project(
                                                  passing_point))
            self.transition.append(point)

    def copy(self):
        waypoints_copy = self.waypoints[:]
        cell_copy = CellPath(waypoints_copy)
        cell_copy.transition = self.transition[:]
        return cell_copy

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
        if len(cell.waypoints) > 0:
            start_point = cell.waypoints[0]
            self.length += self.cells[-1].transition[-1].distance(
                                                     start_point)

        self.cells.append(cell)

    def add_transition(self, target_point, prev_node, this_node):
        self.cells[-1] = self.cells[-1].copy()
        self.cells[-1].add_transition(target_point, prev_node,
                                      this_node)

        prev_point = self.cells[-1].transition[0]
        for point in self.cells[-1].transition[1:]:
            self.length += prev_point.distance(point)
            prev_point = point

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

    if isinstance(intersection, Point):
        return intersection, intersection
    else:
        # TODO: better error handling
        assert isinstance(intersection, LineString)

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
    """
    Node: the polygon passed should have already been eroded
    before calling this function to ensure a safe margin for the
    drone.
    """
    minx, miny, maxx, maxy = polygon.bounds
    bottoms = []
    tops = []

    x = minx
    while x <= maxx:
        bottom, top = traversal_endpoints(polygon, x, miny, maxy)
        bottoms.append(bottom)
        tops.append(top)
        x += path_radius * 2

    assert(len(bottoms) > 0)

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
        if not hasattr(elem.node, 'eroded'):
            # Generate an eroded version of this cell (with the
            # edges pulled inward by path_radius)
            elem.node.eroded = elem.node.polygon.buffer(
                                                    -path_radius)
            if not isinstance(elem.node.eroded.exterior,
                              LinearRing):
                # After eroding, the cell disappeared completely,
                # meaning it was too small for the drone to
                # safely drop pesticides on it
                elem.node.eroded = None

        if elem.first_visit and elem.node.eroded != None:
            cell_paths.append(possible_paths(elem.node.eroded,
                                             path_radius))
        else:
            # leave it to the second part of the algorithm
            # (below) to figure out how to traverse this cell
            cell_paths.append([])
        
    # Find a CompletePath that covers the field in the minimum
    # distance.
    heap = []
    # TODO: FIX THIS, not safe to assume 2 elements in the stack
#    this_node = stack[0].node
#    next_node = stack[1].node
#    target_point = stack[1].node.polygon.centroid
    for initial_cell in cell_paths[0]:
#        initial_cell.add_transition(target_point, this_node,
#                                    next_node)
        heappush(heap, (0, CompletePath(initial_cell)))

    while True:
        priority, path = heappop(heap)
        index = len(path.cells)

        if index == len(stack):
            # this path already contains all the cells
            if len(path.cells[-1].transition) > 0:
                return path
            else:
                target_point = path.cells[0].waypoints[0]
                prev_node = stack[-1].node
                path.add_transition(target_point, prev_node,
                                    None)
                heappush(heap, (path.length, path))
                continue

        prev_node = stack[index-1].node
        this_node = stack[index].node

        if len(cell_paths[index]) > 0:
            for cell_path in cell_paths[index]:
                new_path = path.copy()
                new_path.add_transition(cell_path.start_point(),
                                        prev_node, this_node)
                new_path.add(cell_path)
                heappush(heap, (new_path.length, new_path))
        else:
            # generate a path to traverse this cell
            path.add_transition(this_node.polygon.centroid,
                                prev_node, this_node)
            path.add(CellPath([]))
            heappush(heap, (path.length, path))
