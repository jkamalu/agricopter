# This script reads a mission specification from stdin in JSON format
# and outputs the calculated list of waypoints, also in JSON.

import json
from sys import stdin, stdout

from missionplanner import plan_complete_coverage_mission

if __name__ == '__main__':
    params = json.load(stdin)
    viz_data, mission_spec = plan_complete_coverage_mission(params)
    json.dump(mission_spec, stdout, sort_keys=True, indent=4,
              separators=(',', ': '))
