# Let Python search for modules in the parent directory
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARENT_DIR)

from missionplanner import plan_complete_coverage_mission
import testfields
import visualize


if __name__ == '__main__':
    testfield = testfields.test1 # choose any test available in
                                 # testfields.py
    visualization_data, mission = plan_complete_coverage_mission(
                                           testfield)

    visualize.visualize(visualization_data);
