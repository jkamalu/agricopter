import parsepolygon
import decompose
import cellgrapher
import celllinker
import shapely
from shapely.geometry import Polygon
from matplotlib import pyplot
from oxpath import generate_oxpath

INPUT_FILE = "test_fields/test3.txt"
DRONE_RADIUS = .1

exterior = [(0, 0, 0), (0, 5, 0), (6, 6, 0), (5, -1, 0)]
interior = [(1, 1, 0), (2, 1, 0), (1.5, 3, 0)]
test_with_interior = Polygon(exterior, [interior])

if __name__ == '__main__':
    polygon = parsepolygon.parse_polygon(INPUT_FILE)
#    polygon = test_with_interior
    cells, angle, rotate_point = decompose.decompose(polygon)
    graph_meta = cellgrapher.build_graph(cells)
    stack = celllinker.optimal(graph_meta)

    path = generate_oxpath(stack, DRONE_RADIUS)
    waypoints = []
    for cellpath in path.cells:
        waypoints += cellpath.waypoints

    # Display the exterior and interior edges of the polygon
    fig = pyplot.figure(1, figsize=(5,5), dpi=90)
    ax = fig.add_subplot(111)

    x, y = polygon.exterior.xy
    ax.plot(x, y, 'b', linewidth=2)
    for interior in polygon.interiors:
        x, y = interior.xy
        ax.plot(x, y, 'b', linewidth=2)

    for i in range(0, len(graph_meta.nodes)):
        # Rotate cells back to original orientation
        graph_meta.nodes[i].polygon = shapely.affinity.rotate(
            graph_meta.nodes[i].polygon, -angle,
            origin=rotate_point)

        # Label each cell with coordinates of its centroid
        cell = graph_meta.nodes[i].polygon
        label = "(%.2g, %.2g)"%(cell.centroid.x,
                                cell.centroid.y)
        ax.text(cell.centroid.x, cell.centroid.y, label,
                fontsize=8, verticalalignment='center',
                horizontalalignment='center')

    # Rotate waypoints back to original orientation
    for i in range(0, len(waypoints)):
        waypoints[i] = shapely.affinity.rotate(
            waypoints[i], -angle, origin=rotate_point)

    # Display chosen path in green
    ax.plot([waypoint.x for waypoint in waypoints],
            [waypoint.y for waypoint in waypoints], 'g')

    # Print out the centroids of the cells, in the order that
    # they should be traversed according to the results of
    # celllinker.optimal()
    for stackelem in stack:
        cell = stackelem.node.polygon
        label = "({0:.2g}, {1:.2g})".format(cell.centroid.x,
                                            cell.centroid.y)
        label = "{0:12}  first visit: {1}".format(
            label, stackelem.first_visit)
        print label

        x, y = cell.exterior.xy
        ax.plot(x, y, 'r--', linewidth=2)

    pyplot.show()
