# This script reads a mission specification from stdin in JSON format
# and outputs the calculated list of waypoints, also in JSON.

import json
from sys import stdin, stdout

from missionplanner import plan_complete_coverage_mission
import visualize

if __name__ == '__main__':
    params = json.load(stdin)
    visualization_data, mission_spec = plan_complete_coverage_mission(params)
    json.dump(mission_spec, stdout)
    print
    stdout.flush()

    visualize.visualize(visualization_data);
