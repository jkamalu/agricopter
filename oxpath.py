# This module generates an ox-style (boustrophedon) coverage
# path for a given polygonal cell.

from shapely.geometry import (Polygon, LineString, Point)

# TODO: Figure out why I can't "from cellsequencer
# import SequenceElement"
import cellsequencer

def traversal_endpoints(polygon, path_radius, x, miny, maxy):
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
        return (point1, point2)
    else:
        return (point2, point1)

def coverage_options(polygon, path_radius):
    minx, miny, maxx, maxy = polygon.bounds
    
    # TODO: better handling of areas where there is not
    # enough horizontal space in the field to safely pass the
    # drone
    xleft = minx + path_radius
    xcenter = (minx + maxx) / 2
    if xleft > xcenter:
        xleft = xcenter

    xright = xleft
    ntraversals = 1
    while (xright + path_radius * 2) <= (maxx - path_radius):
        xright += path_radius * 2
        ntraversals += 1

    upper_left, lower_left = traversal_endpoints(polygon,
                                                 path_radius,
                                                 xleft,
                                                 miny, maxy)
    upper_right, lower_right = traversal_endpoints(polygon,
                                                   path_radius,
                                                   xright,
                                                   miny, maxy)

    if ntraversals % 2 == 0:
        # Drone will end its coverage of this polygon at the same
        # y-position as where it started
        return [
            cellsequencer.SequenceElement(
                polygon, lower_left, lower_right, False, True),
            cellsequencer.SequenceElement(
                polygon, lower_right, lower_left, False, False),
            cellsequencer.SequenceElement(
                polygon, upper_left, upper_right, True, True),
            cellsequencer.SequenceElement(
                polygon, upper_right, upper_left, True, False)]
    else:
        # Drone will end its coverage at the opposite y-position
        # (i.e. start high, end low, or vice versa)
        return [
            cellsequencer.SequenceElement(
                polygon, lower_left, upper_right, False, True),
            cellsequencer.SequenceElement(
                polygon, upper_right, lower_left, True, False),
            cellsequencer.SequenceElement(
                polygon, upper_left, lower_right, True, True),
            cellsequencer.SequenceElement(
                polygon, lower_right, upper_left, False, False)]

def generate_path(polygon, path_radius, start_top, start_left):
    minx, miny, maxx, maxy = polygon.bounds
    
    top_points = []
    bottom_points = []

    x = minx + path_radius
    while x <= maxx - path_radius:
        top, bottom = traversal_endpoints(polygon, path_radius,
                                          x, miny, maxy)
        top_points.append(top)
        bottom_points.append(bottom)
        x += path_radius * 2

    waypoints = []
    top_to_bottom = start_top
    if start_left:
        pop_index = 0 # pop leftmost point
    else:
        pop_index = -1 # pop rightmost point

    for i in range(0, len(top_points)):
        if top_to_bottom:
            waypoints.append(top_points.pop(pop_index))
            waypoints.append(bottom_points.pop(pop_index))
            top_to_bottom = False
        else:
            waypoints.append(bottom_points.pop(pop_index))
            waypoints.append(top_points.pop(pop_index))
            top_to_bottom = True

    return waypoints
