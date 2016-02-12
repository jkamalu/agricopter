# This module generates a complete coverage path for a field
# defined by an arbitrary polygon

from shapely.geometry import (Point, Polygon,
                              LineString, GeometryCollection,
                              MultiPolygon)

def sign(val):
    if val >= 0:
        return 1
    else:
        return -1

def decompose_polygon(polygon):
    # copy the polygon, since we will be destructively modifying
    polygon = Polygon(polygon)

    coords = polygon.exterior.coords
    coords = coords[:-1] # last coord is a repeat of the first

    minx, miny, maxx, maxy = polygon.bounds
    minx -= 1
    miny -= 1
    maxy += 1
    
    # For now, pass a vertical line from bottom to top through
    # the polygon
    reference_line = LineString([(minx, miny), (maxx, miny)])
    
    sorted_indices = range(0, len(coords))
    sorted_indices.sort(
        key=lambda index:
        Point(coords[index]).distance(reference_line))

    cells = []
    for index in sorted_indices:
        point = Point(coords[index])
        dist = point.distance(reference_line)

        # Vertices are only critical if the two edges of the
        # polygon that are connected to that vertex go on the same
        # side of the reference line when it passes through that
        # vertex, forming a point that points opposite the
        # direction of motion of the reference line.
        #
        # Exception: the last vertex is always critical.
        prev_index = (index - 1) % len(coords)
        prev_point = Point(coords[prev_index])
        prev_dist = prev_point.distance(reference_line)

        next_index = (index + 1) % len(coords)
        next_point = Point(coords[next_index])
        next_dist = next_point.distance(reference_line)

        if ((prev_dist <= dist or next_dist <= dist) and
            index != sorted_indices[-1]):
            # This is not a critical point (see comment above)
            continue

        # Create a new cell
        box = reference_line.union(point).envelope
        new_cell = box.intersection(polygon)
        if isinstance(new_cell, Polygon):
            cells.append(new_cell)
        elif (isinstance(new_cell, GeometryCollection) or
              isinstance(new_cell, MultiPolygon)):
            for item in new_cell:
                if isinstance(item, Polygon):
                    cells.append(item)
        
        polygon = polygon.symmetric_difference(new_cell)
    
    return cells
