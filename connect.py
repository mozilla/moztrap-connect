import requests
from urllib import urlencode
from json import loads, dumps

class Connect:
    """
    Connect to MozTrap to fetch runs, cases and environments, and submit
    test results for them

    @@@ If there is a test that is different for two different environments,
        then there will be separate test case IDs.  This is fine for manual
        runs, but in the case of automation, it may need some other way to
        determine the case it applies to.  Will the test script itself need
        to keep track of which case id applies to which env?  Perhaps the
        only option.

        Best approach is that the test framework, when executing a test that is
        different for two different environments, should map the environment
        they're executing in to the case id they expect.

    @@@ TODO Talk to Dave Hunt about how he wants to use the connector
        1. What info would he like to have
        2. Would he like to create a testrun on the fly based on just a list of
           test cases?
        3. Is the current list of methods good?


    @@@ TODO Need to be able to create TestCase objects with just a case ID
        Then add that to a list and submit that in a testrun that never
        existed in MozTrap before.  The server will just take that list of
        cases, build a set of runcaseversions on a new run out of it and take
        in the results.
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
        res = requests.get(url)
        print(res.text)
        res.raise_for_status()
        return res


    def do_patch(self, resource, data_obj, params={}):
        url = self.get_url(self.get_uri(resource), params)

        res = requests.patch(
            url,
            data=dumps(data_obj),
            headers = {"content-type": "application/json"},
            )
        res.raise_for_status()
        return res


    def do_post(self, resource, data_obj, params={}):
        url = self.get_url(self.get_uri(resource), params)

        print(dumps(data_obj, sort_keys=True, indent=4))

        res = requests.post(
            url,
            data=dumps(data_obj),
            headers = {"content-type": "application/json"},
            )
        print res.text
        res.raise_for_status()
        return res


    #######################
    # connector APIs
    #######################

    def get_products(self, name=None):
        """
        Return a list of Products with their productversions.

        name - Filter by Product name

        """
        params = {}
        if name:
            params["name"] = name

        r = self.do_get(self.get_uri("product"), params=params)
        return loads(r.text)



    def get_runs(self, **kwargs):
        """
        Return a list of test runs.  This can be filtered by product or
        productversion.

        """

        params = {}
        if "product" in kwargs:
            params["productversion__product__name"] = kwargs.pop("product")

        if "productversion" in kwargs:
            params["productversion__version"] = kwargs.pop("productversion")


        r = self.do_get("run", params=params)
        return loads(r.text)


    def get_run_environments(self, run_id):
        """
        Return a list of environments for the specified test run.

        """
        r = self.do_get("run", id=run_id)

        env_list = loads(r.text)["environments"]

        for env in env_list:
            env["elements"] = [x["name"] for x in env.pop("elements")]

        return env_list


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


    def get_environment_id(self, element_list, run_id=None, env_list=None):
        """
        Return a single environment id.

        You have two options for getting this:

        1. supply a run_id and no env_list, and this will call
        the client to find this for you
        2. supply an env_list and no run_id and this will search through the
        env_list for the environment you're seeking

        """

        if not env_list:
            assert run_id, "You must supply either a run_id, or an env_list."
            env_list = self.get_environments(run_id)

        exp_env = set(element_list)

        try:
            env_id = next(item["id"] for item in env_list if
                exp_env == set(item["elements"]))

        except:
            raise EnvironmentDoesNotExistException(
                "Run with id {0} does not have environment: {1}".format(
                    run_id,
                    element_list,
                    ))

        return env_id


    def get_run_cases(self, run_id, environment_id):
        """
        Return a list of TestCase objects.  Pass/Fail/Invalid is set on each
        object in the list.  The list of environments is filtered by the
        environment, just as it would be in the UI of MozTrap.

        """
        params = {"caseversion__environments": environment_id, "run": run_id}
        r = self.do_get("runcaseversion", params)

        return [TestCase(x) for x in loads(r.text)["objects"]]


    def get_results(self, testcase_list):
        return [x.result for x in testcase_list if x.result != None]


    def submit_results(self, testcase_list=None, result_list=None):
        """
        Submit the tests back to the system with results.
        Results are not required for any of the tests.

        You must supply either a testcase_list OR a result_list.  If both
        are supplied, it will use the result_list and ignore the testcase_list.

        """

        (assertresult_list or testcase_list,
            "You must supply either a result_list or a testcase_list")

        if not result_list:
            result_list = self.get_results(testcase_list)


        res = self.do_patch("result", data_obj={"objects": result_list})

        return res


    def submit_run(self, name, description, productversion_id, testresults):
        """
        Creates a new testrun based on the productversion and TestResults.

        Pass in a TestResult object with test results for case ids that match
        cases in MozTrap.  This can be a list of objects that are a environment
        and a list of results.  So you could run the cases over several
        environments and build a whole test run that shows coverage for all of
        that.


        "productversion": 3,
        "name": "my run name",
        "description": "my run desc",
        "results": [
            {
            "environment": 3,
            "case": 1,
            "status": "failed",
            "comment": "from connector",
            "stepnumber": 2,
            "bug": "http://bugzilla.mozilla.org/432432",
            },
            {
            "environment": 3,
            "case_id": 2,
            "status": "failed",
            "comment": "from connector",
            "stepnumber": 2,
            "bug": "http://bugzilla.mozilla.org/432432",
            }]},
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




class TestResults(object):
    """
    A holder for results of each test.

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