# Module for visualizing the output of the agricopter algorithm

import shapely
from shapely.geometry import Point
from matplotlib import pyplot

def visualize(data):
    """
    Visualize the algorithm output using the data returned by
    plan_complete_coverage_mission()
    """
    rotate_point = Point(0, 0)

    fig = pyplot.figure(1, figsize=(5,5), dpi=90)
    ax = fig.add_subplot(111)

    # Display the exterior and interior edges of the polygon
    # (solid blue line)
    x, y = data["polygon"].exterior.xy
    ax.plot(x, y, 'b', linewidth=2)
    for interior in data["polygon"].interiors:
        x, y = interior.xy
        ax.plot(x, y, 'b', linewidth=2)

    for node in data["cells"]:
        # Rotate cells back to original orientation
        node.polygon = shapely.affinity.rotate(node.polygon,
                            -data["angle"], origin=rotate_point)

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

    ax.text(0, 0, "H", # Home point
            fontsize=10, verticalalignment='center',
            horizontalalignment='center')

    # Display chosen path for drone (solid green line, with
    # transitions between cells shown by thicker, cyan lines)
    for transition in data["path"].transitions:
        ax.plot([waypoint.x for waypoint in transition.waypoints],
                [waypoint.y for waypoint in transition.waypoints],
                'c', linewidth=2)
    for cell_path in data["path"].cells:
        ax.plot([waypoint.x for waypoint in cell_path.waypoints],
                [waypoint.y for waypoint in cell_path.waypoints],
                'g')

    # Print out the centroids of the cells, in the order that
    # they should be traversed according to the results of
    # celllinker.optimal()
    for stackelem in data["stack"]:
        cell = stackelem.polygon
        label = "({0:.2g}, {1:.2g})".format(cell.centroid.x,
                                            cell.centroid.y)

    pyplot.show()
