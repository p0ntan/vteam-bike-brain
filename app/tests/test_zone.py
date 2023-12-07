#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Module for testing the class Zone and CityZone """

import pytest
from src.zone import Zone, CityZone

forbidden_zone = {
    'coordinates': [
        [
            13.499330851455909,
            59.37930900702122
        ],
        [
            13.504219371828242,
            59.37920902684962
        ],
        [
            13.504406313333249,
            59.38209405047175
        ],
        [
            13.500489888790298,
            59.38217974048908
        ],
        [
            13.499919717198594,
            59.38111812110745
        ],
        [
            13.501798479330176,
            59.381065753371786
        ],
        [
            13.50178913225426,
            59.38052778922446
        ],
        [
            13.499349545606123,
            59.380561114685236
        ],
        [
            13.499330851455909,
            59.37930900702122
        ]
    ],
    'speed_limit': 0
}

point_in_zone = [
    13.503079028643214,
    59.380789631247524
]
point_outside_zone = [
    13.501555455372227,
    59.38081819570931
]
point_barely_outside_zone = [
    13.504416913808058,
    59.38210294152472
]

city_zone_coords = {
    'coordinates':[
        [
            13.498068850544314,
            59.378897877374186
        ],
        [
            13.505640230756597,
            59.37877685583828
        ],
        [
            13.505798627831581,
            59.38266546517127
        ],
        [
            13.498417324110278,
            59.382746136991926
        ],
        [
            13.498068850544314,
            59.378897877374186
        ]
    ],
    'speed_limit': 20
}

point_outside_city = [
    13.506555699194905,
    59.382188484555655
]

def test_zone():
    """ Test if a point is inside a zone. """
    zone = Zone(forbidden_zone)

    assert zone.point_in_zone(point_in_zone) is True
    assert zone.point_in_zone(point_outside_zone) is False
    assert zone.point_in_zone(point_barely_outside_zone) is False

def test_city_zone():
    """ Test if a point is inside a city and outside a restricted zone. """
    city_zone = CityZone(city_zone_coords)
    zone = Zone(forbidden_zone)
    city_zone.add_zone(zone)

    assert city_zone.get_speed_limit(point_outside_city) == 0
    assert city_zone.get_speed_limit(point_outside_zone) == city_zone.speed_limit
    assert city_zone.get_speed_limit(point_in_zone) == 0
