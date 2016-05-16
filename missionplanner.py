import shapely.affinity

import decompose
import cellgrapher
import celllinker
import oxpath

from Mission import (Mission, Command)

def plan_complete_coverage_mission(polygon, path_radius,
                                   drone_elevation):
    # Decompose the polygon into cells and trapezoids
    nodes, traps, angle, rotate_point = decompose.decompose(polygon)

    # Generate adjacencey graphs for the cells and trapezoids
    graph_nodes = cellgrapher.build_graph(nodes)
    graph_traps = cellgrapher.build_graph(traps)
    cellgrapher.debug_print_graph(graph_nodes)

    # Find a sequence that travels through the graph of cells,
    # visiting each at least once
    stack = celllinker.optimal(graph_nodes)

    # Based on this sequence, generate a detailed path that can be
    # used by a drone to cover the entirety of the given polygon
    rotated_polygon = shapely.affinity.rotate(
        polygon, angle, origin=rotate_point)
    path = oxpath.generate_path(stack, path_radius,
                                rotated_polygon, graph_traps)

    # Rotate this path back to the original orientation
    path.rotate(-angle, rotate_point)

    # Consolidate an ordered list of the waypoints that make up the
    # path (including while covering a given cell, and while
    # transitioning between cells, with no distinction between the
    # two for the moment)
    waypoints = []
    for i in xrange(0, path.cells_traversed()):
        waypoints += path.cells[i].waypoints
        waypoints += path.transitions[i].waypoints

    # Create a mission containing all of these waypoints
    mission = Mission()
    for waypoint in waypoints:
        mission.add_command(Command(16, waypoint.y, waypoint.x,
                                    drone_elevation))

    # Along with the mission, return a dictionary with some
    # data structures that allow the client to generate a
    # visualization of the algorithm
    visualization_data = {
        'waypoints': waypoints,
        'graph_nodes': graph_nodes,
        'graph_traps': graph_traps,
        'stack': stack,
        'angle': angle,
        'rotate_point': rotate_point,
        'path': path
    }

    return (visualization_data, mission)
