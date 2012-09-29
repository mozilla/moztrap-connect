#!python

import pytest

from mtconnect.connect import Connect
from mtconnect.connect import InvalidFilterParamsException
from mtconnect.connect import ProductVersionDoesNotExistException


class TestConnect:


    # constructor
    def test_connect_limits(self, testmoztrap):
        unlimited = testmoztrap.connect.get_products()
        limited = Connect(
            "https",
            testmoztrap.url,
            testmoztrap.username,
            testmoztrap.apikey,
            limit=3
        ).get_products()
        assert len(limited) == 3
        assert len(unlimited) > len(limited)


    # get_products
    def test_get_products_no_filter(self, testmoztrap):
        prods = testmoztrap.connect.get_products()
        print "products:\n%s" % prods
        found = False
        for prod in prods:
            if prod['name'] == 'Macaron':
                found = True
        assert found, "product Macaron not found in %s" % prods


    def test_get_products_filter_by_name(self, testmoztrap):
        prods = testmoztrap.connect.get_products(name="Macaron")
        print "products:\n%s" % prods
        assert len(prods) == 1
        assert prods[0]['id'] == '15'


    # get_productversions
    def test_get_productversions_by_version_id(self, testmoztrap):
        vers = testmoztrap.connect.get_productversions(version_id="33")
        print "versions:\n%s" % vers
        assert len(vers) == 1
        assert vers[0]['version'] == "1", vers


    def test_get_productversions_by_product_name_only(self, testmoztrap):
        vers = testmoztrap.connect.get_productversions(product="Macaron")
        found = False
        print "versions:\n%s" % vers
        for ver in vers:
            if ver['version'] == "1":
                found = True
        assert found, "product version 1 not found in %s" % vers


    def test_get_productversions_by_product_name_and_version_name(self, 
            testmoztrap):
        vers = testmoztrap.connect.get_productversions(product="Macaron", 
            version="1")
        print "versions:\n%s" % vers
        assert len(vers) == 1
        assert vers[0]['id'] == "33", vers


    def test_get_productversions_by_version_name_only_throws_exception(self, 
            testmoztrap):
        with pytest.raises(InvalidFilterParamsException) as e:
            vers = testmoztrap.connect.get_productversions(version="1")

        assert "Either version_id or product is required." in e.exconly()


    # get_product_environments
    def test_get_product_environments_by_productversion_id(self, testmoztrap):
        envs = testmoztrap.connect.get_product_environments(
            productversion_id="33")
        print "environments:\n%s" % envs
        found = False
        for env in envs:
            for element in env['elements']:
                if element['name'] == "OS X 10.5":
                    found = True

        assert found, "OS X 10.5 was not found in %s" % envs


    # get_runs
    def test_get_runs_filter_by_id(self, testmoztrap):
        runs = testmoztrap.connect.get_runs(run_id="25")
        print "runs:\n%s" % runs
        run_names = [r['name'] for r in runs]
        assert "Vanilla mousse" in run_names


    def test_get_runs_filter_by_just_name_raises_exception(self, testmoztrap):
        with pytest.raises(InvalidFilterParamsException) as e:
            runs = testmoztrap.connect.get_runs(name="Vanilla mousse")

        assert "Either run_id or productversion_id or product "
        "and version are required." in e.exconly()


    def test_get_runs_filter_by_just_product_name_raises_exception(self, 
            testmoztrap):
        with pytest.raises(InvalidFilterParamsException) as e:
           runs = testmoztrap.connect.get_runs(product="Macaron")

        assert "Either run_id or productversion_id or product and "
        "version are required." in e.exconly()


    def test_get_runs_filter_by_just_version_name_raises_exception(self, 
            testmoztrap):
        with pytest.raises(InvalidFilterParamsException) as e:
            runs = testmoztrap.connect.get_runs(version="0.1a")

        assert "Either run_id or productversion_id or product and "
        "version are required." in e.exconly()


    def test_get_runs_filter_by_productversion_id(self, testmoztrap):
        runs = testmoztrap.connect.get_runs(productversion_id=31)
        print "runs:\n%s" % runs
        run_names = [r['name'] for r in runs]
        assert "Vanilla mousse" in run_names


    def test_get_runs_filter_by_product_and_version(self, testmoztrap):
        runs = testmoztrap.connect.get_runs(
            product="pytest_moztrap", version="0.1a", )
        print "runs:\n%s" % runs
        run_names = [r['name'] for r in runs]
        assert "this_is_a_test" in run_names


    def test_get_runs_filter_by_product_and_version_and_name(self, testmoztrap):
        runs = testmoztrap.connect.get_runs(
            product="pytest_moztrap", version="0.1a", name="this_is_a_test")
        print "runs:\n%s" % runs
        assert len(runs) == 1
        assert runs[0]['id'] == "47"


    def test_get_runs_no_product_version_match_throws_exception(self, 
            testmoztrap):
        with pytest.raises(ProductVersionDoesNotExistException) as e:
            runs = testmoztrap.connect.get_runs(
                product="nonexistant product", 
                version="nonexistant version", 
                name="nonexistant run")
        assert "No productversion found matching product=nonexistant product "
        "and version=nonexistant version." in str(e.exconly())


    # get_run_environments
    def test_get_run_environments_by_run_id(self, testmoztrap):
        runs = testmoztrap.connect.get_runs(
            product="Macaron", version="1", name="Vanilla mousse")
        print "runs:\n%s" % runs
        run_id = runs[0]['id']
        run_envs = testmoztrap.connect.get_run_environments(run_id)
        print "environments:\n%s" % run_envs
        found = False
        for env in run_envs:
            for element in env['elements']:
                if element['name'] == "OS X 10.5":
                    found = True
        assert True, "OS X 10.5 not found in %s" % run_envs


    def test_get_run_environments_by_run_id_and_name(self, testmoztrap):
        runs = testmoztrap.connect.get_runs(
            product="Macaron", version="1", name="Vanilla mousse")
        print "runs:\n%s" % runs
        run_id = runs[0]['id']
        run_envs = testmoztrap.connect.get_run_environments(run_id, "OS X 10.5")
        print "environments:\n%s" % run_envs
        assert len(run_envs) == 1
        assert run_envs[0]['id'] == "108"


    # get_run_cases
    def test_get_run_cases(self, testmoztrap):
        runs = testmoztrap.connect.get_runs(
            product="Macaron", version="1", name="Vanilla mousse")
        print "runs:\n%s" % runs
        run_id = runs[0]['id']
        run_envs = testmoztrap.connect.get_run_environments(run_id, "OS X 10.5")
        print "environments:\n%s" % run_envs
        env_id = run_envs[0]['id']

        cases = testmoztrap.connect.get_run_cases(run_id, env_id)
        print "cases:\n%s" % cases
        assert cases[0]['caseversion']['case']['id'] == "278"


    # test other stuff
    @pytest.mark.xfail(reason="not implemented yet")
    def test_submit_in_two_parts(self, testmoztrap):
        """
        Test that you can submit for a user/run/env the first 3 results, then
        submit just the second 3 results and not have it blow away the first.

        Existing results should be downloaded with test cases, if they already
        exist.
        """
        assert False, "test not yet implemented"
