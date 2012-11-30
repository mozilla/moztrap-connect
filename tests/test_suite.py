#!python

import pytest
from datetime import datetime

from mtconnect.fixtures import SuiteFixture


class TestSuite:

    def test_list_suites(self, testmoztrap, suite_fixture, product_fixture):
        suites = SuiteFixture.list(testmoztrap.connect)
        found = False
        for suite in suites:
            print suite.__dict__
            if suite.name == suite_fixture.name:
                found = True
                # assert suite.product_id == product_fixture.id
                assert suite.description == suite_fixture.description
                assert suite.status == suite_fixture.status
        assert found, "suite %s not found" % suite_fixture.name

    def test_create_delete_suite(self, testmoztrap, product_fixture):
        dt_string = datetime.utcnow().isoformat()

        fields = {
            'name': 'test_create_delete_suite_%s' % dt_string,
            'description': 'test_create_delete_suite %s' % dt_string,
            'product': product_fixture.resource_uri,
            'status': 'active',
        }
        suite = SuiteFixture(testmoztrap.connect, fields)
        assert suite.name == fields['name']
        assert suite.description == fields['description']
        assert suite.product == product_fixture.resource_uri
        assert suite.status == fields['status']

        suites = SuiteFixture.list(testmoztrap.connect, name=suite.name)
        assert len(suites) == 1

        suite.delete()
        suites = SuiteFixture.list(testmoztrap.connect, name=suite.name)
        assert len(suites) == 0

    def test_edit_get_suite(self, testmoztrap, suite_fixture):
        dt_string = datetime.utcnow().isoformat()
        fields = { 
            'description': 'test_edit_get_suite %s' % dt_string,
            'status': 'draft',
            }
        suite_fixture.edit(fields)
        suite_fixture.get()
        assert suite_fixture.description == fields['description']
        assert suite_fixture.status == fields['status']

    def test_list_suites_by_name(self, testmoztrap, suite_fixture):
        suite_list = SuiteFixture.list(testmoztrap.connect, name=suite_fixture.name)
        assert len(suite_list) == 1
        suite = suite_list[0]
        assert suite.id == suite_fixture.id
        assert suite.description == suite_fixture.description
        assert suite.status == suite_fixture.status

    def test_suite_not_found_by_name(self, testmoztrap):
        suite_list = SuiteFixture.list(testmoztrap.connect, name="this product does not exist")
        assert suite_list == []

    def test_list_suites_by_product(self, testmoztrap, product_fixture, suite_fixture):
        suite_list = SuiteFixture.list(testmoztrap.connect, product=product_fixture.id)
        assert len(suite_list) == 1
        suite = suite_list[0]
        assert suite.id == suite_fixture.id
        assert suite.description == suite_fixture.description
        assert suite.status == suite_fixture.status
        assert suite.product == product_fixture.resource_uri

    def test_suite_not_found_by_product(self, testmoztrap):
        suite_list = SuiteFixture.list(testmoztrap.connect, product=9999999)
        assert suite_list == []