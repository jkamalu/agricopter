import parsepolygon
import decompose
import cellgrapher
import celllinker
import shapely
from shapely.geometry import Polygon
from matplotlib import pyplot

INPUT_FILE = "test_fields/test3.txt"

exterior = [(0, 0, 0), (0, 5, 0), (6, 6, 0), (5, -1, 0)]
interior = [(1, 1, 0), (2, 1, 0), (1.5, 3, 0)]
test_with_interior = Polygon(exterior, [interior])

if __name__ == '__main__':
    fig = pyplot.figure(1, figsize=(5,5), dpi=90)
    ax = fig.add_subplot(111)

    polygon = parsepolygon.parse_polygon(INPUT_FILE)
#    polygon = test_with_interior
    cells, angle, rotate_point = decompose.decompose(polygon)
    graph_meta = cellgrapher.build_graph(cells)
    stack = celllinker.optimal(graph_meta)

    for i in range(0, len(graph_meta.nodes)):
        # Rotate back to original orientation
        graph_meta.nodes[i].polygon = shapely.affinity.rotate(
            graph_meta.nodes[i].polygon, -angle,
            origin=rotate_point)

        # Label each cell with coordinates of its centroid
        cell = graph_meta.nodes[i].polygon
        label = "(%.2g, %.2g)"%(cell.centroid.x, cell.centroid.y)
        ax.text(cell.centroid.x-.4,
                cell.centroid.y,
                label, fontsize=8)

    # Print out the centroids of the cells, in the order that
    # they should be traversed according to the results of
    # celllinker.optimal()
    for cell in stack:
        label = "(%.2g, %.2g)"%(cell.polygon.centroid.x,
                                cell.polygon.centroid.y)
        print label
        x, y = cell.polygon.exterior.xy
        ax.plot(x, y, 'r', linewidth=1)

    # Visualize the generated path using matplotlib
    x, y = polygon.exterior.xy
    ax.plot(x, y, 'b', linewidth=2)
    for interior in polygon.interiors:
        x, y = interior.xy
        ax.plot(x, y, 'b', linewidth=2)
    pyplot.show()
