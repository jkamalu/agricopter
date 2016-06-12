# This module exports several hypothetical fields used by test.py to
# test the pathfinding algorithm. Fields are expressed in GPS
# coordinates (latitude/longitude in WGS 84 format).

test1 = {
    "home": { "lat": 30.0000, "lon": 43.0000 },
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
    "radius": 3
}

# ISEP coordinates
test2 = {
    "home": { "lat": 48.82528574178794, "lon": 2.2797945141792297 },
    "exterior": [
        { "lat": 48.82528574178794, "lon": 2.2797945141792297 },
        { "lat": 48.82464773544975, "lon": 2.2808338701725006 },
        { "lat": 48.82417977652902, "lon": 2.2806595265865326 },
        { "lat": 48.82440280806693, "lon": 2.2793278098106384 }
    ],
    "obstacles": [],
    "alt": 3,
    "radius": 3
}

# H-shaped field
test3 = {
    "home": { "lat": 0.0000, "lon": 0.0000 },
    "exterior": [
        { "lat": 0.0000, "lon": 0.0000 },
        { "lat": 0.0006, "lon": 0.0000 },
        { "lat": 0.0006, "lon": 0.0012 },
        { "lat": 0.0012, "lon": 0.0012 },
        { "lat": 0.0012, "lon": 0.0000 },
        { "lat": 0.0018, "lon": 0.0000 },
        { "lat": 0.0015, "lon": 0.0015 },
        { "lat": 0.0018, "lon": 0.0030 },
        { "lat": 0.0012, "lon": 0.0030 },
        { "lat": 0.0012, "lon": 0.0018 },
        { "lat": 0.0006, "lon": 0.0018 },
        { "lat": 0.0006, "lon": 0.0030 },
        { "lat": 0.0000, "lon": 0.0030 },
        { "lat": 0.0003, "lon": 0.0015 }
    ],
    "obstacles": [],
    "alt": 3,
    "radius": 3
}

# Very ugly, complex field
test4 = {
    "home": { "lat": 0.0000, "lon": 0.000000 },
    "exterior": [
        { "lat": 0.0000, "lon": 0.000000 },
        { "lat": 0.0006, "lon": 0.000210 },
        { "lat": 0.0000, "lon": 0.000390 },
        { "lat": 0.0006, "lon": 0.000600 },
        { "lat": 0.0008, "lon": 0.000390 },
        { "lat": 0.0008, "lon": 0.000805 },
        { "lat": 0.0012, "lon": 0.000600 },
        { "lat": 0.0012, "lon": 0.001010 },
        { "lat": 0.0000, "lon": 0.001420 },
        { "lat": 0.0000, "lon": 0.002830 },
        { "lat": 0.0004, "lon": 0.001610 },
        { "lat": 0.0028, "lon": 0.001610 },
        { "lat": 0.0004, "lon": 0.001420 },
        { "lat": 0.0028, "lon": 0.001190 },
        { "lat": 0.0026, "lon": 0.000210 }
    ],
    "obstacles": [],
    "alt": 3,
    "radius": 3
}

# Field with obstacle in it
test5 = {
    "home": { "lat": 30.0000, "lon": 40.0000 },
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
    "radius": 3
}
