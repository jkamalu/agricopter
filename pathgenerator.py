import decompose
import cellsequencer
import oxpath
import shapely.affinity
import cellgrapher
from MissionGenerator import MissionGenerator
from Command import Command

def generate_path(polygon, path_radius):
    cells, angle, rotate_point = decompose.decompose(polygon)

    sequence = cellsequencer.generate_sequence(cells,
                                               path_radius)
    waypoints = []
    for elem in sequence:
        path = oxpath.generate_path(elem.polygon, path_radius,
                                    elem.start_top,
                                    elem.start_left)
        waypoints += path

    mission = MissionGenerator()
    
    for i in range(0, len(waypoints)):
        waypoints[i] = shapely.affinity.rotate(
            waypoints[i], -angle, origin=rotate_point)
        mission.add_command(
            Command(16, waypoints[i].y, waypoints[i].x,
                    waypoints[i].z))

    return (waypoints, mission)