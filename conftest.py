#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from datetime import datetime

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
    group._addoption('--test-mt-protocol',
                     action='store',
                     dest='test_moztrap_protocol',
                     default='http',
                     help='http/https defaults to http')


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
    TestSetup.protocol = item.config.option.test_moztrap_protocol

    TestSetup.connect = Connect(
        TestSetup.protocol,
        TestSetup.url,
        TestSetup.username,
        TestSetup.apikey,
        DEBUG=True,
        )

@pytest.fixture()
def product_fixture(request, testmoztrap):
    from mtconnect.fixtures import ProductFixture

    dt_string = datetime.utcnow().isoformat()

    fields = {
        'name': 'TestProduct_fixture_%s' % dt_string,
        'description': 'TestProduct_fixture_ %s' % dt_string,
        'productversions': [{
            'version': 'test_create_product_%s' % dt_string,
        }]
    }
    product_fixture = ProductFixture(testmoztrap.connect, fields)

    def teardown():
        product_fixture.delete()

    request.addfinalizer(teardown)

    return product_fixture

@pytest.fixture()
def suite_fixture(request, testmoztrap, product_fixture):
    from mtconnect.fixtures import SuiteFixture

    dt_string = datetime.utcnow().isoformat()

    fields = {
        'name': 'TestSuite_fixture_%s' % dt_string,
        'status': 'active',
        'product': product_fixture.resource_uri,
        'description': 'TestSuite_fixture %s' % dt_string,
    }
    suite_fixture = SuiteFixture(testmoztrap.connect, fields)

    def teardown():
        suite_fixture.delete()

    request.addfinalizer(teardown)

    return suite_fixture


class TestSetup:
    '''
        This class is just used for monkey patching
    '''
    def __init__(self, request):
        self.request = request
