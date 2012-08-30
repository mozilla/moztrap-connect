#!python

import pytest

from mtconnect.connect import Connect
#from mock import Mock, patch


class TestConnect:
    def setup(self):
        self.connect = Connect("https", "moztrap.allizom.org", "klrmn", "3150247f-0a62-4662-ab26-1bcb01238f5f")

    # get_products
    def test_get_products_no_filter(self):
        prods = self.connect.get_products()
        print "products:\n%s" % prods
        found = False
        for prod in prods:
            if prod['name'] == 'Macaron':
                found = True
        assert found, "product Macaron not found in %s" % prods

    def test_get_products_filter_by_name(self):
        prods = self.connect.get_products(name="Macaron")
        print "products:\n%s" % prods
        assert len(prods) == 1
        assert prods[0]['id'] == '15'

    # get_product_environments
    def test_get_product_environments_by_productversion_id(self):
        envs = self.connect.get_product_environments(productversion_id="33")
        print "environments:\n%s" % envs
        found = False
        for env in envs:
            for element in env['elements']:
                if element['name'] == "OS X 10.5":
                    found = True

        assert found, "OS X 10.5 was not found in %s" % envs

    # get_runs
    def test_get_runs_filter_by_product_id(self):
        runs = self.connect.get_runs(product_id=15)
        print "runs:\n%s" % runs
        run_names = [r['name'] for r in runs]
        assert "Vanilla mousse" in run_names

    def test_get_runs_filter_by_product_name(self):
        runs = self.connect.get_runs(product="Macaron")
        print "runs:\n%s" % runs
        run_names = [r['name'] for r in runs]
        assert "Vanilla mousse" in run_names

    def test_get_runs_filter_by_productversion_id(self):
        runs = self.connect.get_runs(productversion_id=31)
        print "runs:\n%s" % runs
        run_names = [r['name'] for r in runs]
        assert "Vanilla mousse" in run_names

    def test_get_runs_filter_by_product_and_version(self):
        runs = self.connect.get_runs(product="pytest_moztrap", version="0.1a", )
        print "runs:\n%s" % runs
        run_names = [r['name'] for r in runs]
        assert "this_is_a_test" in run_names

    # get_run_environments
    def test_get_run_environments_by_run_id(self):
        runs = self.connect.get_runs(product="Macaron", version="1")
        print "runs:\n%s" % runs
        run_id = runs[0]['id']
        run_envs = self.connect.get_run_environments(run_id)
        print "environments:\n%s" % run_envs
        assert run_envs[0]['elements'][0]['name'] != ""

    # get_run_cases
    def test_get_run_cases(self):
        runs = self.connect.get_runs(product="Macaron", version="1")
        print "runs:\n%s" % runs
        run_id = runs[0]['id']
        run_envs = self.connect.get_run_environments(run_id)
        print "environments:\n%s" % run_envs
        env_id = run_envs[0]['id']

        cases = self.connect.get_run_cases(run_id, env_id)
        print "cases:\n%s" % cases
        assert cases[0]['caseversion']['case']['id'] > "0"

    # test other stuff
    @pytest.mark.xfail(reason="not implemented yet")
    def test_submit_in_two_parts(self):
        """
        Test that you can submit for a user/run/env the first 3 results, then
        submit just the second 3 results and not have it blow away the first.

        Existing results should be downloaded with test cases, if they already
        exist.
        """
        assert False, "test not yet implemented"