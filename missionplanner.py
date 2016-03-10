import shapely.affinity

import decompose
import cellgrapher
import celllinker
import oxpath

from MissionGenerator import MissionGenerator
from Command import Command

def plan_complete_coverage_mission(polygon, path_radius,
                                   drone_elevation):
    cells, angle, rotate_point = decompose.decompose(polygon)
    graph_meta = cellgrapher.build_graph(cells)
    stack = celllinker.optimal(graph_meta)
    path = oxpath.generate_path(stack, path_radius)

    waypoints = []
    for cell_path in path.cells:
        waypoints += cell_path.waypoints

    mission = MissionGenerator()
    
    for i in range(0, len(waypoints)):
        waypoints[i] = shapely.affinity.rotate(
            waypoints[i], -angle, origin=rotate_point)
        mission.add_command(
            Command(16, waypoints[i].y, waypoints[i].x,
                    drone_elevation))

    # Along with the mission, return a dictionary with some
    # data structures that allow the client to generate a
    # visualization of the algorithm
    visualization_data = {
        'waypoints': waypoints,
        'graph_meta': graph_meta,
        'stack': stack,
        'angle': angle,
        'rotate_point': rotate_point
    }

    return (visualization_data, mission)
