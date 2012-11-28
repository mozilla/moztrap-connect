#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import pytest

from mtconnect.connect import Connect

pytest_plugins = 'pytester'


def pytest_funcarg__testmoztrap(request):
    return TestSetup(request)


def pytest_addoption(parser):
    # required
    group = parser.getgroup('test-moztrap', 'test-moztrap')
    group._addoption('--test-mt-username',
                     action='store',
                     dest='test_moztrap_username',
                     metavar='str',
                     help='moztrap username')
    group._addoption('--test-mt-url',
                     action='store',
                     dest='test_moztrap_url',
                     default='moztrap.allizom.org',
                     metavar='str',
                     help='test run name')
    group._addoption('--test-mt-apikey',
                     action='store',
                     dest='test_moztrap_apikey',
                     metavar='str',
                     help="Ask your MozTrap admin to generate an API key "
                     "in the Core / ApiKeys table and provide it to you.")


def pytest_sessionstart(session):
    config = session.config

    if not config.option.test_moztrap_apikey and \
           config.option.test_moztrap_username:

        raise pytest.UsageError("--test-mt-username and --test-mt-apikey "
        "are required.")


def pytest_runtest_setup(item):
    TestSetup.username = item.config.option.test_moztrap_username
    TestSetup.apikey = item.config.option.test_moztrap_apikey
    TestSetup.url = item.config.option.test_moztrap_url

    TestSetup.connect = Connect(
        "https",
        TestSetup.url,
        TestSetup.username,
        TestSetup.apikey,
        )


class TestSetup:
    '''
        This class is just used for monkey patching
    '''
    def __init__(self, request):
        self.request = request
