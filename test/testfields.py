# This module exports several hypothetical fields used by test.py to
# test the pathfinding algorithm. Fields are expressed in GPS
# coordinates (latitude/longitude in WGS 84 format).

test1 = {
    "home": { "lat": 30.0001, "lon": 43.0001 },
    "exterior": [
        { "lat": 30.0000, "lon": 43.0000 },
        { "lat": 30.0008, "lon": 43.0000 },
        { "lat": 30.0004, "lon": 43.0002 },
        { "lat": 30.0010, "lon": 43.0002 },
        { "lat": 30.0009, "lon": 43.0000 },
        { "lat": 30.0014, "lon": 43.0000 },
        { "lat": 30.0014, "lon": 43.0006 },
        { "lat": 30.0008, "lon": 43.0010 },
        { "lat": 30.0000, "lon": 43.0006 }
    ],
    "obstacles": [],
    "alt": 3,
    "radius": 2
}

# ISEP coordinates
test2 = {
    "home": { "lat": 48.82485, "lon": 2.2804 },
    "exterior": [
        { "lat": 48.82528574178794, "lon": 2.2797945141792297 },
        { "lat": 48.82464773544975, "lon": 2.2808338701725006 },
        { "lat": 48.82417977652902, "lon": 2.2806595265865326 },
        { "lat": 48.82440280806693, "lon": 2.2793278098106384 }
    ],
    "obstacles": [],
    "alt": 3,
    "radius": 2
}

# H-shaped field
test3 = {
    "home": { "lat": 40.0001, "lon": 30.0001 },
    "exterior": [
        { "lat": 40.0000, "lon": 30.0000 },
        { "lat": 40.0006, "lon": 30.0000 },
        { "lat": 40.0006, "lon": 30.0012 },
        { "lat": 40.0012, "lon": 30.0012 },
        { "lat": 40.0012, "lon": 30.0000 },
        { "lat": 40.0018, "lon": 30.0000 },
        { "lat": 40.0015, "lon": 30.0015 },
        { "lat": 40.0018, "lon": 30.0030 },
        { "lat": 40.0012, "lon": 30.0030 },
        { "lat": 40.0012, "lon": 30.0018 },
        { "lat": 40.0006, "lon": 30.0018 },
        { "lat": 40.0006, "lon": 30.0030 },
        { "lat": 40.0000, "lon": 30.0030 },
        { "lat": 40.0003, "lon": 30.0015 }
    ],
    "obstacles": [],
    "alt": 3,
    "radius": 2
}

# Very ugly, complex field
test4 = {
    "home": { "lat": 30.00031, "lon": 40.00009 },
    "exterior": [
        { "lat": 30.0000, "lon": 40.000000 },
        { "lat": 30.0006, "lon": 40.000200 },
        { "lat": 30.0000, "lon": 40.000400 },
        { "lat": 30.0006, "lon": 40.000600 },
        { "lat": 30.0008, "lon": 40.000390 },
        { "lat": 30.0008, "lon": 40.000805 },
        { "lat": 30.0012, "lon": 40.000600 },
        { "lat": 30.0012, "lon": 40.001010 },
        { "lat": 30.0000, "lon": 40.001420 },
        { "lat": 30.0000, "lon": 40.002830 },
        { "lat": 30.0004, "lon": 40.001610 },
        { "lat": 30.0028, "lon": 40.001610 },
        { "lat": 30.0004, "lon": 40.001420 },
        { "lat": 30.0028, "lon": 40.001190 },
        { "lat": 30.0026, "lon": 40.000210 }
    ],
    "obstacles": [],
    "alt": 3,
    "radius": 2
}

# Field with obstacle in it
test5 = {
    "home": { "lat": 30.00005, "lon": 40.0001 },
    "exterior": [
        { "lat": 30.0000 , "lon": 40.0000 },
        { "lat": 30.0000 , "lon": 40.0010 },
        { "lat": 30.0012 , "lon": 40.0012 },
        { "lat": 30.0010 , "lon": 39.9998 }
    ],
    "obstacles": [
        [
            { "lat": 30.0002, "lon": 40.0002 },
            { "lat": 30.0005, "lon": 40.0002 },
            { "lat": 30.0003, "lon": 40.0006 }
        ]
    ],
    "alt": 3,
    "radius": 2
}
