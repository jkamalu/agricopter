import shapely.affinity
from shapely.geometry import Polygon, Point

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
    # home point, which will be (0, 0) in the new coordinate frame
    home = (params["home"]["lat"], params["home"]["lon"])
    coordtransform.latlon_to_meters(exterior, home)
    for interior in interiors:
        coordtransform.latlon_to_meters(interior, home)

    # Generate a shapely Polygon representing the field
    polygon = Polygon(exterior, interiors)

    # Decompose the polygon into cells and trapezoids
    # Note that the cells and traps returned will be rotated by angle
    # degrees about the point (0, 0)
    cells, traps, angle = decompose.decompose(polygon)

    # Generate adjacencey graphs for the cells and trapezoids
    cellgrapher.build_graph(cells)
    cellgrapher.build_graph(traps)

    # Determine which cell contains the home point
    for start_cell in cells:
        if start_cell.polygon.contains(Point(0, 0)):
            break
    else:
        raise Exception("Home point is not within polygon")

    # Starting with that cell, find a sequence that travels through
    # the graph of cells, visiting all of them at least once
    stack = celllinker.optimal(start_cell, cells)

    # Based on this sequence, generate a detailed path that can be
    # used by a drone to cover the entirety of the given polygon
    rotated_polygon = shapely.affinity.rotate(
        polygon, angle, origin=Point(0, 0))
    path = oxpath.generate_path(stack, params["radius"],
                                rotated_polygon, traps)

    # Rotate this path back to the original orientation
    path.rotate(-angle, Point(0, 0))

    # Consolidate an ordered list of the waypoints that make up the
    # path (including while covering a given cell, and while
    # transitioning between cells, with no distinction between the
    # two for the moment)
    waypoints = []
    for i in range(0, path.cells_traversed()):
        waypoints += path.transitions[i].waypoints
        waypoints += path.cells[i].waypoints
    waypoints += path.transitions[i+1].waypoints

    mission = {
        "waypoints": [
            {
                "x": waypoint.x,
                "y": waypoint.y
            } for waypoint in waypoints
        ]
    }

    # Return a dictionary with some data structures that allow the
    # client to generate a visualization of the algorithm's output
    visualization_data = {
        'polygon': polygon,
        'waypoints': waypoints,
        'cells': cells,
        'traps': traps,
        'stack': stack,
        'angle': angle,
        'path': path
    }

    return (visualization_data, mission)
