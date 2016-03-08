import parsepolygon
from pathgenerator import generate_path
from shapely.geometry import Polygon
from matplotlib import pyplot

INPUT_FILE = "test_fields/test1.txt"
DRONE_RADIUS = .1

exterior = [(0, 0, 0), (0, 5, 0), (6, 6, 0), (5, -1, 0)]
interior = [(1, 1, 0), (2, 1, 0), (1.5, 3, 0)]
test_with_interior = Polygon(exterior, [interior])

if __name__ == '__main__':
    polygon = parsepolygon.parse_polygon(INPUT_FILE)
    # polygon = test_with_interior

    waypoints, mission = generate_path(polygon, DRONE_RADIUS)

    mission.export_to_file('test_output.waypoints')

    # Visualize the generated path using matplotlib
    fig = pyplot.figure(1, figsize=(5,5), dpi=90)
    ax = fig.add_subplot(111)
    x, y = polygon.exterior.xy
    ax.plot(x, y, 'b', linewidth=2)
    for interior in polygon.interiors:
        x, y = interior.xy
        ax.plot(x, y, 'b', linewidth=2)

    ax.plot([waypoint.x for waypoint in waypoints],
            [waypoint.y for waypoint in waypoints], 'r')
    
    pyplot.show()


    # nodes = generate_path(polygon, DRONE_RADIUS)
    # for node in nodes:
    #     print len(node.edges)
