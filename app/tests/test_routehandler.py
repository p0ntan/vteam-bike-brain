#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Module for testing the class RouteHandler """

import os
import pytest
from src.routehandler import RouteHandler


def test_init_routehandler():
    """
    Init routehandler from file in folder containing other files.
    Should only load jsonfiles.
    """
    base_dir = os.path.dirname(__file__)
    test_directory = os.path.join(base_dir, 'test-data')
    rhandler = RouteHandler(test_directory)

    # pylint: disable=protected-access
    assert rhandler._interval == 10
    assert isinstance(rhandler.routes, dict)


def test_init_rhandler_wrong_file():
    """ Init routehandler from file with wrong name (not an int) """
    base_dir = os.path.dirname(__file__)
    test_directory = os.path.join(base_dir, 'test-data/wrong-files')
    with pytest.raises(ValueError):
        RouteHandler(test_directory)


def test_right_distance_50():
    """ Test to see if right amout of extra coords are added.

    There are two routes in the testfile, both with only two coordinates.
    First is 500 m and second is 200m.
    """
    base_dir = os.path.dirname(__file__)
    test_directory = os.path.join(base_dir, 'test-data')
    interval_in_seconds = 50  # High interval will not need to add many points
    rhandler = RouteHandler(test_directory, interval_in_seconds)
    routes = rhandler.routes

    # First route should have one more point, second stay the same.
    assert len(routes[100]['trips'][0]['coords']) == 3
    assert len(routes[100]['trips'][1]['coords']) == 2


def test_right_distance_10():
    """ Test to see if right amout of extra coords are added.

    There are two routes in the testfile, both with only two coordinates.
    First is 500 m and second is 200m.
    """
    base_dir = os.path.dirname(__file__)
    test_directory = os.path.join(base_dir, 'test-data')
    interval_in_seconds = 10  # Same as default
    rhandler = RouteHandler(test_directory, interval_in_seconds)
    routes = rhandler.routes

    assert len(routes[100]['trips'][0]['coords']) == 11
    assert len(routes[100]['trips'][1]['coords']) == 5


def test_right_distance_5():
    """ Test to see if right amout of extra coords are added.

    There are two routes in the testfile, both with only two coordinates.
    First is 500 m and second is 200m.
    """
    base_dir = os.path.dirname(__file__)
    test_directory = os.path.join(base_dir, 'test-data')
    interval_in_seconds = 5
    rhandler = RouteHandler(test_directory, interval_in_seconds)
    routes = rhandler.routes

    assert len(routes[100]['trips'][0]['coords']) == 20
    assert len(routes[100]['trips'][1]['coords']) == 9
