import shapely
from shapely.geometry import Polygon, Point
from matplotlib import pyplot

# Let Python search for modules in the parent directory
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARENT_DIR)

from missionplanner import plan_complete_coverage_mission
import testfields

if __name__ == '__main__':
    testfield = testfields.test5 # choose any test available in
                                 # testfields.py
    visualization_data, mission = plan_complete_coverage_mission(
                                           testfield)

    #############################################################
    # The remaining code exists for visualization purposes only #
    #############################################################

    # Create local variables with the same names and values
    # as all the items in the visualization_data dict.
    for var, val in visualization_data.iteritems():
        locals()[var] = val

    rotate_point = Point(0, 0)

    fig = pyplot.figure(1, figsize=(5,5), dpi=90)
    ax = fig.add_subplot(111)

    # Display the exterior and interior edges of the polygon
    # (solid blue line)
    x, y = polygon.exterior.xy
    ax.plot(x, y, 'b', linewidth=2)
    for interior in polygon.interiors:
        x, y = interior.xy
        ax.plot(x, y, 'b', linewidth=2)

    for node in cells:
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

    ax.text(0, 0, "H", # Home point
            fontsize=10, verticalalignment='center',
            horizontalalignment='center')

    # Display chosen path for drone (solid green line, with
    # transitions between cells shown by thicker, cyan lines)
    for transition in path.transitions:
        ax.plot([waypoint.x for waypoint in transition.waypoints],
                [waypoint.y for waypoint in transition.waypoints],
                'c', linewidth=2)
    for cell_path in path.cells:
        ax.plot([waypoint.x for waypoint in cell_path.waypoints],
                [waypoint.y for waypoint in cell_path.waypoints],
                'g')

    # Print out the centroids of the cells, in the order that
    # they should be traversed according to the results of
    # celllinker.optimal()
    for stackelem in stack:
        cell = stackelem.polygon
        label = "({0:.2g}, {1:.2g})".format(cell.centroid.x,
                                            cell.centroid.y)
        print label

    pyplot.show()
