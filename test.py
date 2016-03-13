import shapely
from shapely.geometry import Polygon
from matplotlib import pyplot

import parsepolygon
from missionplanner import plan_complete_coverage_mission

INPUT_FILE = "test_fields/test3.txt"
DRONE_RADIUS = .00002
DRONE_ELEVATION = 10

exterior = [(0,0,0),(0,.001,0),(.0012,.0012,0),(.001,-.0002,0)]
interior = [(.0002,.0002,0),(.0005,.0002,0),(.0003,.0006,0)]
test_with_interior = Polygon(exterior, [interior])

if __name__ == '__main__':
    polygon = parsepolygon.parse_polygon(INPUT_FILE)
    polygon = test_with_interior

    visualization_data, mission = plan_complete_coverage_mission(
                                           polygon, DRONE_RADIUS,
                                           DRONE_ELEVATION)
    mission.export_to_file('test_output.waypoints')


    #############################################################
    # The remaining code exists for visualization purposes only #
    #############################################################

    # Create local variables with the same names and values
    # as all the items in the visualization_data dict.
    for var, val in visualization_data.iteritems():
        locals()[var] = val

    waypoints = visualization_data['waypoints']
    graph_nodes = visualization_data['graph_nodes']
    stack = visualization_data['stack']

    fig = pyplot.figure(1, figsize=(5,5), dpi=90)
    ax = fig.add_subplot(111)

    # Display the exterior and interior edges of the polygon
    # (solid blue line)
    x, y = polygon.exterior.xy
    ax.plot(x, y, 'b', linewidth=2)
    for interior in polygon.interiors:
        x, y = interior.xy
        ax.plot(x, y, 'b', linewidth=2)

    for node in graph_nodes:
        # Rotate cells back to original orientation
        node.polygon = shapely.affinity.rotate(node.polygon,
                                     -angle, origin=rotate_point)

        # Display the edges of each cell (dashed red line)
        cell = node.polygon
        x, y = cell.exterior.xy
        ax.plot(x, y, 'r--', linewidth=2)

        # Label each cell with coordinates of its centroid
        label = "(%.2g, %.2g)"%(cell.centroid.x,
                                cell.centroid.y)
        ax.text(cell.centroid.x, cell.centroid.y, label,
                fontsize=8, verticalalignment='center',
                horizontalalignment='center')

    ax.text(waypoints[0].x, waypoints[0].y, "X",
            fontsize=10, verticalalignment='center',
            horizontalalignment='center')

    # Display chosen path for drone (solid green line)
    for i in xrange(0, len(path.cells)):
        if len(path.cells[i].waypoints) > 0:
            path.cells[i].transition.insert(
                0, path.cells[i].waypoints[-1])

        if i < len(path.cells) - 1:
            if len(path.cells[i+1].waypoints) > 0:
                path.cells[i].transition.append(
                    path.cells[i+1].waypoints[0])
            else:
                path.cells[i].transition.append(
                    path.cells[i+1].transition[0])

    for cell_path in path.cells:
        ax.plot([waypoint.x for waypoint in cell_path.transition],
                [waypoint.y for waypoint in cell_path.transition],
                'c', linewidth=2)
    for cell_path in path.cells:
        ax.plot([waypoint.x for waypoint in cell_path.waypoints],
                [waypoint.y for waypoint in cell_path.waypoints],
                'g')

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

    pyplot.show()
