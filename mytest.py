import parsepolygon
import decompose
import cellgrapher
import celllinker
from shapely.geometry import Polygon
from matplotlib import pyplot

INPUT_FILE = "test_fields/test1.txt"

if __name__ == '__main__':
    polygon = parsepolygon.parse_polygon(INPUT_FILE)
    cells, angle, rotate_point = decompose.decompose(polygon)
    graph_meta = cellgrapher.build_graph(cells)
    stack = celllinker.optimal(graph_meta)
    for cell in stack:
        print cell.polygon.centroid

    # Visualize the generated path using matplotlib
    fig = pyplot.figure(1, figsize=(5,5), dpi=90)
    ax = fig.add_subplot(111)
    x, y = polygon.exterior.xy
    ax.plot(x, y, 'b', linewidth=2)
    for interior in polygon.interiors:
        x, y = interior.xy
        ax.plot(x, y, 'b', linewidth=2)
    pyplot.show()