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

    mission = MissionGenerator()
    
    for waypoint in waypoints:
        mission.add_command(Command(16, waypoint.y, waypoint.x,
                                    drone_elevation))

    # Along with the mission, return a dictionary with some
    # data structures that allow the client to generate a
    # visualization of the algorithm
    visualization_data = {
        'waypoints': waypoints,
        'graph_meta': graph_meta,
        'stack': stack,
        'angle': angle,
        'rotate_point': rotate_point,
        'path': path
    }

    return (visualization_data, mission)
