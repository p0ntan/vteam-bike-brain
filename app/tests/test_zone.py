#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Module for testing the class Zone and CityZone """

from src.zone import Zone, CityZone

# Has speed limit 0
forbidden_zone = {
    'geometry': {
        'coordinates': [
            [
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
            ]
        ]
    },
    'speed_limit': 0
}

# Has no speed limit
parking_zone = {
    'geometry': {
        'coordinates': [
            [
                [
                    13.501333394186332,
                    59.38095474359335
                ],
                [
                    13.501267500001347,
                    59.38072700257973
                ],
                [
                    13.501676985295944,
                    59.38071261888538
                ],
                [
                    13.501705225660515,
                    59.38094275726101
                ],
                [
                    13.501333394186332,
                    59.38095474359335
                ]
            ]
        ]
    }
}

# Point in restricted zone
point_in_zone = [
    13.503079028643214,
    59.380789631247524
]

# Point in city but in parking_zone
point_in_parking_zone = [
    13.501555455372227,
    59.38081819570931
]

# Point just outside restricted zone
point_barely_outside_zone = [
    13.504416913808058,
    59.38210294152472
]

city_zone_data = {
    'geometry': {
        'coordinates': [
            [
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
            ]
        ]
    },
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
    assert zone.point_in_zone(point_barely_outside_zone) is False


def test_city_zone():
    """ Test if a point is inside a city and outside a restricted zone. """
    city_zone = CityZone(city_zone_data)
    zone = Zone(forbidden_zone)
    city_zone.add_zone(zone)

    assert city_zone.get_speed_limit(point_outside_city) == 0
    assert city_zone.get_speed_limit(point_barely_outside_zone) == city_zone.speed_limit
    assert city_zone.get_speed_limit(point_in_zone) == 0


def test_city_zones_with_speed():
    """ Test if a point is in a parking zone with speed limit set with own optional argument. """
    city_zone = CityZone(city_zone_data)
    zones = [Zone(forbidden_zone), Zone(parking_zone, 15)]  # Adding speed limit as argument
    city_zone.add_zones_list(zones)

    assert city_zone.get_speed_limit(point_in_parking_zone) == 15
    assert city_zone.get_speed_limit(point_in_zone) == 0
    assert city_zone.get_speed_limit(point_barely_outside_zone) == 20


def test_city_zones_without_speed():
    """ Test if a point is in a parking zone with speed limit without speed limit. """
    city_zone = CityZone(city_zone_data)
    zones = [Zone(forbidden_zone), Zone(parking_zone)]  # Adding speed limit as argument
    city_zone.add_zones_list(zones)

    assert city_zone.get_speed_limit(point_in_parking_zone) == 20  # Default value
    assert city_zone.get_speed_limit(point_in_zone) == 0
    assert city_zone.get_speed_limit(point_barely_outside_zone) == 20
