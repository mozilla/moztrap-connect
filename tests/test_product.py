#!python

import pytest

from mtconnect.fixtures import ProductFixture
from mtconnect.connect import Connect
from base import Base


class TestProduct(Base):

    def test_create_delete_product(self, testmoztrap):
        dt_string = self.timestamp

        fields = ProductFixture.fixture_data()
        product = ProductFixture(testmoztrap.connect, fields)
        prods = ProductFixture.list(testmoztrap.connect, name=product.name)
        assert len(prods) == 1
        product.delete()
        prods = ProductFixture.list(testmoztrap.connect, name=product.name)
        assert len(prods) == 0

    def test_edit_get_product(self, testmoztrap, product_fixture):
        dt_string = self.timestamp
        fields = { 'description': 'test_edit_product %s' % dt_string}
        product_fixture.edit(fields)
        product_fixture.get()
        assert product_fixture.description == fields['description']

    def test_list_products(self, testmoztrap, product_fixture):
        prods = ProductFixture.list(testmoztrap.connect)
        found = False
        for prod in prods:
            if prod.name == product_fixture.name:
                found = True
                assert prod.productversions == product_fixture.productversions
                assert prod.description == product_fixture.description
        assert found, "product %s not found" % product_fixture.name


    def test_list_product_by_name(self, testmoztrap, product_fixture):
        prod = ProductFixture.list(testmoztrap.connect, name=product_fixture.name)[0]
        assert prod.id == product_fixture.id
        assert prod.description == product_fixture.description
        assert prod.productversions == product_fixture.productversions

    def test_product_not_found_by_name(self, testmoztrap):
        prod_list = ProductFixture.list(testmoztrap.connect, name="this product does not exist")
        assert prod_list == []

    def test_list_pagination(self, testmoztrap):
        # create 5 products 
        for i in range(5):
            ProductFixture(testmoztrap.connect, ProductFixture.fixture_data())

        # use connect with limit=1
        connect = Connect(
            testmoztrap.protocol,
            testmoztrap.url,
            testmoztrap.username,
            testmoztrap.apikey,
            limit=1,
            )
        # verify results has five products
        products = ProductFixture.list(connect)
        assert len(products) >= 5