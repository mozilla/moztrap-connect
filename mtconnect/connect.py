import sys
import requests
from urllib import urlencode
from json import loads, dumps


class Connect:
    """
    Connect to MozTrap to run tests and submit results.

    You can either fetch tests for an existing run and submit results for it,
    or you can get tests for a productversion and create a new run with the
    new results.

    """


    def __init__(self, protocol, host, username, api_key, limit=100, DEBUG=False):
        self.DEBUG = DEBUG
        self.protocol = protocol
        self.host = host
        self.auth = {"username": username, "api_key": api_key}
        self.url_root = "{0}://{1}".format(protocol, self.host)
        self.uri_root = "api/v1"
        self.limit = limit


    def get_params(self, dict={}):
        """
        Encode the dict of params and add the format and limit params.
        It's always JSON.
        """

        dict["format"] = "json"
        dict["limit"] = self.limit
        dict.update(self.auth)
        return urlencode(dict)


    def get_uri(self, resource_name, id=None):
        uri = "/{0}/{1}/".format(self.uri_root, resource_name)
        if id:
            uri = "{0}{1}/".format(uri, id)
        return uri


    def get_url(self, uri, params={}):
        url = "{0}{1}?{2}".format(
            self.url_root, uri, self.get_params(params))
        if self.DEBUG:
            print "URL: {0}".format(url)

        return url


    def do_get(self, resource, id=None, params={}):
        if self.DEBUG:
            sys.stdout.write("GET ")

        url = self.get_url(self.get_uri(resource, id), params)

        try:
            res = requests.get(url)
            res.raise_for_status()
            return res
        except:
            print res.text


    def do_patch(self, resource, data_obj, params={}):
        if self.DEBUG:
            sys.stdout.write("PATCH ")

        url = self.get_url(self.get_uri(resource), params)

        if self.DEBUG:
            sys.stdout.write("data = ")
            print(dumps(data_obj, sort_keys=True, indent=4))

        try:
            res = requests.patch(
                url,
                data=dumps(data_obj),
                headers = {"content-type": "application/json"},
                )
            res.raise_for_status()
            return res
        except:
            print res.text
            return res


    def do_put(self, resource, id, params={}):
        if self.DEBUG:
            sys.stdout.write("PUT ")

        url = self.get_url(self.get_uri(resource, id))

        if self.DEBUG:
            sys.stdout.write("params = ")
            print(dumps(params, sort_keys=True, indent=4))

        try:
            res = requests.put(
                url,
                data=dumps(params),
                headers = {"content-type": "application/json"},
                )
            res.raise_for_status()
            return res
        except:
            print res.text

    def do_post(self, resource, data_obj, params={}):
        if self.DEBUG:
            sys.stdout.write("POST ")

        url = self.get_url(self.get_uri(resource), params)

        if self.DEBUG:
            sys.stdout.write("data = ")
            print(dumps(data_obj, sort_keys=True, indent=4))

        try:
            res = requests.post(
                url,
                data=dumps(data_obj),
                headers = {"content-type": "application/json"},
                )
            res.raise_for_status()
            return res
        except:
            print res.text

    def do_delete(self, resource, id, params=None):
        if self.DEBUG:
            sys.stdout.write("DELETE ")

        url = self.get_url(self.get_uri(resource, id), params=params)

        try:
            res = requests.delete(url)
            res.raise_for_status()
            return res
        except:
            print res

    #######################################
    # connector APIs for creating a new run
    #######################################


    def get_products(self, name=None):
        """
        Return a list of Products with their productversions.

        name - Filter by Product name

        """
        params = {}
        if name:
            params["name"] = name

        r = self.do_get("product", params=params)
        return loads(r.text)["objects"]


    def get_productversions(self, product=None, version=None, version_id=None):
        """
        Return a list of Product Versions.

        ::Args::
        product - Filter by Product name.
        version - Filter by Version name.
        version_id - Filter by Version id.

        ::Raises::
        InvalidFilterParamsException if neither version_id nor product are 
        provided.

        """
        if not version_id and not product:
            raise InvalidFilterParamsException("Either version_id or product is required.")

        products = self.get_products(name=product)

        productversions = []
        for product in products:
            pvs = [x for x in product["productversions"] \
                if (version and x["version"] == version) \
                or (version_id and x["id"] == str(version_id)) \
                or (not version and not version_id)]
            productversions.extend(pvs)
        return productversions  # may be empty if the filters were not found


    def get_product_environments(self, productversion_id):
        """
        Return a list of environments for the specified product version.

        """
        r = self.do_get("productversionenvironments", id=productversion_id)

        return loads(r.text)["environments"]


    def get_product_cases(self, productversion_id, environment_id=None):
        """
        Return a list of test cases for the specified product version and
        environment (optional).

        """
        params = {"productversion": productversion_id}
        if environment_id:
            params["environments"] = environment_id

        r = self.do_get("caseversion", params=params)

        return loads(r.text)["objects"]


    def submit_run(self, name, description, productversion_id, testresults):
        """
        Create a new, active run with results.

        Pass in a TestResults object with test results for case ids that match
        cases in MozTrap.  This object can contain results for multiple
        environments.  So you could run the cases over several environments and
        build a whole test run that shows coverage for all of that.

        Results are not required for any of the tests.

        """

        env_uris = [self.get_uri("environment", x) for x
                    in set(testresults.environments)]

        data_obj = {
            "productversion": self.get_uri("productversion", productversion_id),
            "name": name,
            "description": description,
            "environments": env_uris,
            "runcaseversions": testresults.results,
            "status": "active",
            }

        res = self.do_post("run", data_obj=data_obj)
        return res


    ####################################
    # connector APIs for an existing run
    ####################################


    def get_runs(self, 
        product=None, 
        version=None, 
        productversion=None, 
        name=None, 
        run_id=None):
        """
        Return a list of test runs.

        ::Args::
        product - Filter by product name
        version - Filter by product version name
        productversion - Filter by product version id
        name - Filter by run name
        run_id - Filter by run id

        ::Raises::
        InvalidFilterParamsException if neither run_id nor productversion_id 
        nor product and version are provided.

        """
        r = None
        if not run_id:
            if not productversion:
                if product and version:
                    productversions = self.get_productversions(
                        product=product, 
                        version=version)
                    if len(productversions) < 1:
                        raise ProductVersionDoesNotExistException(
                            "No productversion found matching "
                        "product=%s and version=%s." % (product, version))
                    productversion = productversions[0]['id']
                else:
                    raise InvalidFilterParamsException(
                        "Either run_id or productversion or "
                    "product and version are required.")

            r = self.do_get("run", 
                params={'productversion': productversion})
        else:  # run_id is unique to filter by
            r = self.do_get("run")

        runs = loads(r.text)["objects"]
        # TODO: update when API allows filtering by these parameters
        if name or run_id:
            for run in runs:
                if run['name'] == name:
                    return [run]
                if run['id'] == run_id:
                    return [run]
            return [] # no matches found
        return runs


    def get_run_environments(self, run_id, name=None):
        """
        Return a list of environments for the specified test run.

        ::Args::
        - run_id - run id
        - name - environment name

        """
        r = self.do_get("run", id=run_id)
        run_envs = loads(r.text)["environments"]
        # TODO: update when API allows filtering by this parameter
        if name:
            for env in run_envs:
                for element in env['elements']:
                    if element['name'] == name:
                        return [env]
        return run_envs


    def get_run_cases(self, run_id, environment_id):
        """
        Return a list of TestCase objects.  Pass/Fail/Invalid is set on each
        object in the list.  The list of environments is filtered by the
        environment, just as it would be in the UI of MozTrap.

        """
        params = {"caseversion__environments": environment_id, "run": run_id}
        r = self.do_get("runcaseversion", params=params)

        return loads(r.text)["objects"]


    def submit_results(self, run_id, testresults):
        """
        Submit the results for an existing run.

        Pass in a TestResults object with test results for case ids that match
        cases in MozTrap.  This object can contain results for multiple
        environments.  So you could run the cases over several environments and
        build a whole test run that shows coverage for all of that.

        Results are not required for any of the tests.

        """

        results = testresults.results
        for item in results:
            item["run_id"] = run_id

        res = self.do_patch("result", data_obj={"objects": results})

        return res



class TestResults(object):
    """A holder for results of all tests that will be submitted."""


    def __init__(self):
        self.results = []
        self.environments = []


    def addpass(
            self,
            case_id,
            environment_id,
            ):
        """Submit a passing result for a test case."""

        self.environments.append(environment_id)
        self.results.append({
            "environment": environment_id,
            "case": case_id,
            "status": "passed",
            })


    def addfail(
            self,
            case_id,
            environment_id,
            comment,
            stepnumber=0,
            bug=None,
            ):
        """Submit a failing result for a test case."""

        self.environments.append(environment_id)
        self.results.append({
            "environment": environment_id,
            "case": case_id,
            "status": "failed",
            "comment": comment,
            "stepnumber": stepnumber,
            "bug": bug,
            })


    def addinvalid(
            self,
            case_id,
            environment_id,
            comment,
            ):
        """Submit a result for a test case that is invalid or unclear."""

        self.environments.append(environment_id)
        self.results.append({
            "environment": environment_id,
            "case": case_id,
            "status": "invalidated",
            "comment": comment,
            })



class InvalidFilterParamsException(Exception):
    pass



class ProductVersionDoesNotExistException(Exception):
    pass


class EnvironmentDoesNotExistException(Exception):
    pass
