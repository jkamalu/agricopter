# This module generates an ox-style (boustrophedon) coverage path
# for a field that has already been decomposed and linked into an
# ordered list of cells.

import shapely.affinity
from shapely.geometry import Point, LineString, LinearRing
from heapq import heappush, heappop # priority queue
import copy

class CellPath:
    """
    A wrapper class containing a list of waypoints for the drone to
    cover a single cell.
    """
    def __init__(self, waypoints):
        """
        waypoints: a list of shapely Point objects
        """
        self.waypoints = waypoints

    def start_point(self):
        return self.waypoints[0]

    def end_point(self):
        return self.waypoints[-1]

class Transition:
    """
    A class that generates a list of waypoints for the drone to pass
    from one point in the polygon to another point in the polygon.
    Used to generate transitions between the coverage path for one
    cell and the coverage path for the following cell (or a path to
    return to the starting point).
    """
    def __init__(self, start_node, end_node, start_point, end_point,
                 graph_traps, eroded_polygon):
        """
        start_node:     The CellNode in which the transition begins
        end_node:       The CellNode in which the transition ends
        start_point:    The point (shapely Point object) at which the
                        transition begins. Should be within the start
                        node.
        end_point:      The point at which the transition ends.
                        Should be within the end node.
        graph_traps:    A list of CellTrap objects representing the
                        graph of trapezoids, as returned by
                        cellgrapher.build_graph().
        eroded_polygon: The polygon representing the field, with its
                        edges eroded to ensure a safe radius for the
                        drone.
        """
        self.start_node = start_node
        self.end_node = end_node
        self.start_point = start_point
        self.end_point = end_point
        self.graph_traps = graph_traps
        self.eroded_polygon = eroded_polygon

        # Determine a path through the graph of trapezoids to get
        # from the start point to the end point
        self.trap_start, self.trap_end = self.find_start_and_end()
        trap_sequence = [self.trap_start]
        self.mark_traps_unvisited()
        self.find_seq_to_end(trap_sequence)

        # Generate a list of transition waypoints using this path
        self.generate_waypoints(trap_sequence)

        # Calculate the length of this transition
        self.update_length()

    def find_start_and_end(self):
        # Determine which trapezoid contains the start point
        for trap_start in self.start_node.children:
            if trap_start.polygon.contains(self.start_point):
                break
        else:
            raise Exception("None of the children of start node "
                            "contains start point")

        # Determine which trapezoid contains the end point
        for trap_end in self.end_node.children:
            if trap_end.polygon.contains(self.end_point):
                break
        else:
            raise Exception("None of the children of end node "
                            "contains end point")

        return (trap_start, trap_end)

    def mark_traps_unvisited(self):
        for node in self.graph_traps:
            node.visited = False

    def find_seq_to_end(self, trap_sequence):
        """
        Returns True if a sequence to the next cell was successfully
        found (i.e. trap_sequence is now complete), False otherwise.
        """
        trap_curr = trap_sequence[-1]
        trap_curr.visited = True
        if trap_curr is self.trap_end:
            return True

        neighbors = []
        for edge in trap_curr.edges:
            if edge.node_a is trap_curr:
                neighbor = edge.node_b
            else:
                neighbor = edge.node_a
            if not neighbor.visited:
                neighbors.append(neighbor)

        neighbors.sort(key=lambda n : n.polygon.distance(
                                              self.trap_end.polygon))
        for neighbor in neighbors:
            trap_sequence.append(neighbor)
            success = self.find_seq_to_end(trap_sequence)
            if success:
                return True
            else:
                trap_sequence.pop()

        return False

    def generate_waypoints(self, trap_sequence):
        self.waypoints = [self.start_point]
        trap_index = 0

        while True:
            # try to go directly to target
            # TODO: deal with case where, even once in the final
            # cell, the drone isn't able to fly directly to the
            # target for some reason. This should never happen, but
            # given the potential imprecision of shapely, it seems
            # worth checking for.
            current_point = self.waypoints[-1]
            if current_point.equals(self.end_point):
                break

            line = LineString([(current_point.x, current_point.y),
                               (self.end_point.x, self.end_point.y)])
            assert line.is_valid

            if self.eroded_polygon.contains(line):
                self.waypoints.append(self.end_point)
                break

            curr_trap = trap_sequence[trap_index]
            next_trap = trap_sequence[trap_index + 1]

            # find the edge between this trapezoid and the next
            for edge in curr_trap.edges:
                if (edge.node_a == next_trap or
                    edge.node_b == next_trap):
                    break
            else:
                raise Exception('No edge found between this '
                                'trapezoid and next trapezoid in '
                                'sequence')

            border = edge.border_line
            passing_point = border.interpolate(border.project(
                                                     self.end_point))
            if curr_trap.eroded != None:
                exterior = curr_trap.eroded.exterior
                point = exterior.interpolate(exterior.project(
                                                      passing_point))
                self.waypoints.append(point)

            if next_trap.eroded == None:
                self.waypoints.append(next_trap.polygon.centroid)
            else:
                exterior = next_trap.eroded.exterior
                point = exterior.interpolate(exterior.project(
                                                      passing_point))
                self.waypoints.append(point)

            trap_index += 1

    def update_length(self):
        """
        Set the self.length property to the total of all the
        straight-line distances between consecutive waypoints in this
        transition
        """
        self.length = 0
        prev_point = self.waypoints[0]
        for point in self.waypoints[1:]:
            self.length += prev_point.distance(point)
            prev_point = point

    def start_point(self):
        return self.waypoints[0]

    def end_point(self):
        return self.waypoints[-1]

def rotate_path(path, angle, origin):
    """
    Rotate all the waypoints in a cell path or transition by the
    given angle around the given origin.
    """
    for i in xrange(0, len(path.waypoints)):
        path.waypoints[i] = shapely.affinity.rotate(
                                path.waypoints[i], angle,
                                origin=origin)

class CompletePath:
    """
    A coverage path for an entire field.

    The coverage path is represented as a list of CellPaths and a
    list of Transitions. Each CellPath contains the waypoints to
    cover a given cell. Each Transition contains the waypoints to
    move from that cell to the subsequent cell without exiting the
    bounds of the field or touching obstacles.

    The drone should follow the CellPath at self.cells[0], followed
    by the transition at self.transitions[0], then the path at
    cells[1], transition at transitions[1], etc. The transition at
    index i is always intended to follow the path at index i. In
    order to ensure this, the user of this class should alternate calls
    to add_cell() and add_transition(), starting with add_transition()
    (since the first cell is added by the constructor). Not obeying
    this alternation will cause an Exception to be raised.
    """
    def __init__(self, initial_cell, eroded_polygon):
        self.cells = [initial_cell] # list of CellPaths
        self.transitions = [] # list of transitions
        self.length = 0 # total length of transitions
                        # between cells (i.e. not including the
                        # distance spent covering each cell, just
                        # the distance going from one cell to
                        # the next one)
        self.polygon = eroded_polygon

    def cells_traversed(self):
        return len(self.cells)

    def add_cell_path(self, cell_path):
        if not self.has_transition():
            raise Exception("Tried to append cell path without "
                            "first adding a transition")

        self.cells.append(cell_path)

    def start_point(self):
        return self.cells[0].start_point()

    def end_point(self):
        if self.has_transition():
            return self.transitions[-1].end_point()
        else:
            return self.cells[-1].end_point()

    def has_transition(self):
        return len(self.cells) == len(self.transitions)

    def add_transition(self, this_node, next_node,
                       start_point, end_point, graph_traps):
        if self.has_transition():
            raise Exception("Tried to add transition when "
                            "transition was already present")

        transition = Transition(this_node, next_node, start_point,
                                end_point, graph_traps, self.polygon)
        self.transitions.append(transition)
        self.length += transition.length

    def copy(self):
        """
        Return a shallow copy of this CompletePath, with additional
        shallow copies of the cell and transition lists so that they
        can safely be modified in the copy.
        """
        path_copy = copy.copy(self)
        path_copy.cells = copy.copy(self.cells)
        path_copy.transitions = copy.copy(self.transitions)

        return path_copy

    def rotate(self, angle, origin):
        """
        Rotate all the waypoints that make up the cell paths and
        transitions by the given angle around the given origin.
        """
        for cell_path in self.cells:
            rotate_path(cell_path, angle, origin)
        for transition in self.transitions:
            rotate_path(transition, angle, origin)

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

def possible_paths(node, path_radius):
    """
    Note: the node passed should already have a .eroded property,
    as generated by generate_eroded_nodes() (and not equal to
    None).
    """
    polygon = node.eroded
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

def generate_eroded_nodes(stack, path_radius):
    """
    For each cell (node) in the stack, generate an eroded version
    of its polygon, as well as an eroded version of each of its
    child trapezoids. These eroded versions are used when generating
    the path to make sure the drone does not pass too close to the
    edge of the field.
    """
    for node in stack:
        node.eroded = node.polygon.buffer(-path_radius)
        if not isinstance(node.eroded.exterior, LinearRing):
            # After eroding, the cell disappeared completely,
            # meaning it was too small for the drone to
            # safely drop pesticides on it
            node.eroded = None
        for child in node.children:
            child.eroded = child.polygon.buffer(-path_radius)
            if not isinstance(child.eroded.exterior, LinearRing):
                child.eroded = None

def remove_uncoverable_cells(stack):
    """
    Remove all the cells in the stack that cannot be covered
    because they are too small (the eroded version has zero area)
    """
    stack[:] = [node for node in stack
                if node.eroded != None]

def generate_path(stack, path_radius, polygon, graph_traps):
    eroded_polygon = polygon.buffer(-path_radius / 2)

    generate_eroded_nodes(stack, path_radius)
    remove_uncoverable_cells(stack)

    # Generate all possible ox paths for each of the individual
    # cells (linear time), as CellPath objects. The indices of
    # stack and cell_paths are the same, i.e. the possible ox
    # paths for the cell at stack[i] are stored in a list at
    # cell_paths[i].
    cell_paths = []
    for node in stack:
        cell_paths.append(possible_paths(node, path_radius))
        
    # Find a CompletePath that covers the field in the minimum
    # distance.

    # heap is a priority queue containing partially complete coverage
    # paths, prioritized so that a pop will remove the shortest path
    heap = []
    for initial_cell in cell_paths[0]:
        heappush(heap, (0, CompletePath(initial_cell,
                                        eroded_polygon)))

    while True:
        # pop the shortest path from the heap
        priority, path = heappop(heap)
        index = path.cells_traversed()

        if index == len(stack):
            if path.has_transition():
                return path
            else:
                # add transition back to start point
                path.add_transition(stack[-1], stack[0],
                       path.end_point(), path.start_point(),
                       graph_traps)

                heappush(heap, (path.length, path))
                continue

        for cell_path in cell_paths[index]:
            new_path = path.copy()
            new_path.add_transition(stack[index-1], stack[index],
                                    new_path.end_point(),
                                    cell_path.start_point(),
                                    graph_traps)
            new_path.add_cell_path(cell_path)
            heappush(heap, (new_path.length, new_path))
