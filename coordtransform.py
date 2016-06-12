# This module transforms GPS coordinates in WGS 84 format to
# coordinates in meters, relative to a specified point. It achieves
# an approximate transformation using a conversion from WGS 84 to
# UTM coordinates, which are measured in meters and approximately
# map the Earth's surface to a Euclidean plane over small areas.
# The coordinate transformation depends on the utm package
# (https://pypi.python.org/pypi/utm), available through pip.

# TODO: verify whether this conversion will work near boundaries
# between UTM zones

import utm

def latlon_to_meters(coord_list, origin):
    # Convert coord_list to UTM
    coord_list[:] = [utm.from_latlon(*coord) for coord in coord_list]

    # Convert origin to UTM
    origin = utm.from_latlon(*origin)

    # Convert coord_list to meters relative to origin
    coord_list[:] = [(coord[0] - origin[0], coord[1] - origin[1])
                     for coord in coord_list]
