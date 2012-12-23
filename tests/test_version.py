#!python

import pytest

from mtconnect.fixtures import ProductVersionFixture
from base import Base


class TestVersion(Base):

    def test_create_delete_productversion(self, testmoztrap, product_fixture):
        dt_string = self.timestamp

        # before create
        vers = ProductVersionFixture.list(testmoztrap.connect, 
            product=product_fixture.id)
        assert len(vers) == 1

        # do create
        fields = {
            'version': 'test_create_product_version_%s' % dt_string,
            'codename': 'test_create_product_version_%s' % dt_string,
            'product': product_fixture.resource_uri,
            }

        version = ProductVersionFixture(testmoztrap.connect, fields)

        vers = ProductVersionFixture.list(testmoztrap.connect, 
            product=product_fixture.id)
        assert len(vers) == 2

        # do delete
        version.delete()

        vers = ProductVersionFixture.list(testmoztrap.connect,
            product=product_fixture.id)
        assert len(vers) == 1

    def test_edit_get_productversion(self, testmoztrap, product_fixture):
        dt_string = self.timestamp

        version = ProductVersionFixture.list(testmoztrap.connect,
            product=product_fixture.id)[0]

        fields = { 
            'version': 'test_edit_productversion %s' % dt_string,
            'codename': 'test_edit_productversion %s' % dt_string,
            }
        version.edit(fields)
        version.get()
        assert version.version == fields['version']
        assert version.codename == fields['codename']

    def test_list_productversions_by_product_name_only(self, testmoztrap, product_fixture):
        vers = ProductVersionFixture.list(testmoztrap.connect,
            product=product_fixture.id)
        version = product_fixture.productversions[0]['version']
        found = False
        print "versions:\n%s" % vers
        for ver in vers:
            if ver.version == version:
                found = True
        assert found, "product version %s not found in %s" % (version, vers)

    def test_list_productversions_by_version_name(self, 
            testmoztrap, product_fixture):
        version = product_fixture.productversions[0]['version']
        vers = ProductVersionFixture.list(testmoztrap.connect,
            version=version)
        found = False
        print "versions:\n%s" % vers
        for ver in vers:
            if ver.version == version:
                found = True
        assert found, "product version %s not found in %s" % (version, vers)

    def test_list_productversions_by_product_name_and_version_name(self, 
            testmoztrap, product_fixture):
        version = product_fixture.productversions[0]['version']
        vers = ProductVersionFixture.list(testmoztrap.connect,
            product=product_fixture.id, 
            version=version)
        print "versions:\n%s" % vers
        assert len(vers) == 1
        ver = vers[0]
        assert ver.id == product_fixture.productversions[0]['id'], vers

    def test_productversion_not_found_by_name(self, testmoztrap):
        versions = ProductVersionFixture.list(testmoztrap.connect, 
            version="this productversion does not exist")
        assert versions == []

