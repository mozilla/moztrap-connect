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
    def __init__(self, protocol, host, username, api_key, DEBUG=False):
        self.DEBUG = DEBUG
        self.protocol = protocol
        self.host = host
        self.auth = {"username": username, "api_key": api_key}
        self.url_root = "{0}://{1}".format(protocol, self.host)
        self.uri_root = "api/v1"

    def get_params(self, dict={}):
        """
        Encode the dict of params and add the format param.
        It's always JSON.
        """

        dict["format"] = "json"
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
        url = self.get_url(self.get_uri(resource, id), params)

        try:
            res = requests.get(url)
            res.raise_for_status()
            return res
        except:
            print res.text


    def do_patch(self, resource, data_obj, params={}):
        url = self.get_url(self.get_uri(resource), params)

        if self.DEBUG:
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


    def do_post(self, resource, data_obj, params={}):
        url = self.get_url(self.get_uri(resource), params)

        if self.DEBUG:
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


    #######################################
    # connector APIs for creating a new run
    #######################################


    def get_runs(self, **kwargs):
        """
        Return a list of test runs.  This can be filtered by productversion_id.

        """

        r = self.do_get("run", params=kwargs)
        return loads(r.text)["objects"]


    def get_run_environments(self, run_id):
        """
        Return a list of environments for the specified test run.

        """
        r = self.do_get("run", id=run_id)
        return loads(r.text)["environments"]


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
    """
    A holder for results of all tests that can be submitted.

    results objects look like this on upload:
    {
        "environment": 33,
        "case": 2,
        "status": "failed",
        "comment": "from connector",
        "stepnumber": 2,
        "bug": "",
    }

    """

    def __init__(self):
        self.results = []
        self.environments = []


    def addpass(
            self,
            case_id,
            environment_id,
            ):

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

        self.environments.append(environment_id)
        self.results.append({
            "environment": environment_id,
            "case": case_id,
            "status": "invalidated",
            "comment": comment,
            })



class EnvironmentDoesNotExistException(Exception):
    pass