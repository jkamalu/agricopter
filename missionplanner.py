import shapely.affinity

import decompose
import cellgrapher
import celllinker
import oxpath

from Mission import (Mission, Command)

def plan_complete_coverage_mission(polygon, path_radius,
                                   drone_elevation):
    nodes, traps, angle, rotate_point = decompose.decompose(polygon)
    graph_nodes = cellgrapher.build_graph(nodes)
    graph_traps = cellgrapher.build_graph(traps)
    cellgrapher.debug_print_graph(graph_nodes)
    stack = celllinker.optimal(graph_nodes)
    rotated_polygon = shapely.affinity.rotate(
        polygon, angle, origin=rotate_point)
    path = oxpath.generate_path(stack, path_radius,
                                rotated_polygon)

    waypoints = []
    for cell_path in path.cells:
        for i in xrange(0, len(cell_path.waypoints)):
            cell_path.waypoints[i] = shapely.affinity.rotate(
                cell_path.waypoints[i], -angle,
                origin=rotate_point)
        for i in xrange(0, len(cell_path.transition)):
            cell_path.transition[i] = shapely.affinity.rotate(
                cell_path.transition[i], -angle,
                origin=rotate_point)

        waypoints += cell_path.waypoints
        waypoints += cell_path.transition

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
        'stack': stack,
        'angle': angle,
        'rotate_point': rotate_point,
        'path': path
    }

    return (visualization_data, mission)
