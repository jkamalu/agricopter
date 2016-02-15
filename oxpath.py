# This module generates an ox-style (boustrophedon) coverage
# path for a given polygonal cell.

from shapely.geometry import (Polygon, LineString)

def generate_path(polygon, path_radius):
    minx, miny, maxx, maxy = polygon.bounds
    
    top_points = []
    bottom_points = []

    x = minx + path_radius
    while x <= maxx - path_radius:
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
            top_points.append(point1)
            bottom_points.append(point2)
        else:
            top_points.append(point2)
            bottom_points.append(point1)

        x += path_radius * 2

    waypoints = []
    top_to_bottom = True
    for i in range(0, len(top_points)):
        if top_to_bottom:
            waypoints.append(top_points.pop())
            waypoints.append(bottom_points.pop())
            top_to_bottom = False
        else:
            waypoints.append(bottom_points.pop())
            waypoints.append(top_points.pop())
            top_to_bottom = True

    return waypoints
