import shapely.affinity
from shapely.geometry import Polygon

import coordtransform
import decompose
import cellgrapher
import celllinker
import oxpath

def plan_complete_coverage_mission(params):
    # Extract lists of exterior and interior points
    exterior = [(point["lat"], point["lon"])
                    for point in params["exterior"]]
    interiors = []
    for obstacle in params["obstacles"]:
        interiors.append([(point["lat"], point["lon"])
                             for point in obstacle])

    # Convert lists from latitude/longitude to meters relative to the
    # home point
    home = (params["home"]["lat"], params["home"]["lon"])
    coordtransform.latlon_to_meters(exterior, home)
    for interior in interiors:
        coordtransform.latlon_to_meters(interior, home)

    # Generate a shapely Polygon representing the field
    polygon = Polygon(exterior, interiors)

    # Decompose the polygon into cells and trapezoids
    nodes, traps, angle, rotate_point = decompose.decompose(polygon)

    # Generate adjacencey graphs for the cells and trapezoids
    graph_nodes = cellgrapher.build_graph(nodes)
    graph_traps = cellgrapher.build_graph(traps)

    # Find a sequence that travels through the graph of cells,
    # visiting each at least once
    stack = celllinker.optimal(graph_nodes)

    # Based on this sequence, generate a detailed path that can be
    # used by a drone to cover the entirety of the given polygon
    rotated_polygon = shapely.affinity.rotate(
        polygon, angle, origin=rotate_point)
    path = oxpath.generate_path(stack, params["radius"],
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

    mission = [{ "x": waypoint.x, "y": waypoint.y }
               for waypoint in waypoints]

    # Return a dictionary with some data structures that allow the
    # client to generate a visualization of the algorithm's output
    visualization_data = {
        'polygon': polygon,
        'waypoints': waypoints,
        'graph_nodes': graph_nodes,
        'graph_traps': graph_traps,
        'stack': stack,
        'angle': angle,
        'rotate_point': rotate_point,
        'path': path
    }

    return (visualization_data, mission)
