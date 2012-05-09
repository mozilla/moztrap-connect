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

    """
    def __init__(self, host, username, api_key, DEBUG=0):
        self.DEBUG = DEBUG
        self.host = host
        self.auth = {"username": username, "api_key": api_key}
        self.url_root = "http://{0}/api/v1".format(self.host)
        # ping the host to make sure it's valid?


    def get_params(self, dict={}):
        """
        Encode the dict of params and add the format param.
        It's always JSON.
        """

        dict["format"] = "json"
        dict.update(self.auth)
        return urlencode(dict)


    def get_url(self, url_part, params={}):
        return "{0}/{1}/?{2}".format(
            self.url_root, url_part, self.get_params(params))


    def do_get(self, url_part, params={}):
        return requests.get(self.get_url(url_part, params))


    def do_patch(self, url_part, data_obj, params={}):
        url = self.get_url(url_part, params)

        return requests.patch(
            url,
            data=dumps(data_obj),
            headers = {"content-type": "application/json"},
            )


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


    def get_environments(self, run_id):
        """
        Return a list of environments for the specified test run.

        """

        r = self.do_get("runenvironments/{0}".format(run_id))
        assert r.status_code == 200

        env_list = loads(r.text)["environments"]

        for env in env_list:
            env["elements"] = [x["name"] for x in env.pop("elements")]

        return env_list


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


    def get_testcases(self, run_id, environment_id):
        """
        Return a list of TestCase objects.  Pass/Fail/Invalid is set on each
        object in the list.  The list of environments is filtered by the
        environment, just as it would be in the UI of MozTrap.

        """
        params = {"caseversion__environments": environment_id, "run": run_id}
        r = self.do_get("runcaseversion", params)
        assert r.status_code == 200, r.text

        return [TestCase(x) for x in loads(r.text)["objects"]]


    def submit_results(self, testcase_list):
        """
        Submit the tests back to the system with results.
        Results are not required for any of the tests.

        """

        results = [x.result for x in testcase_list if x.result != None]

        r = self.do_patch(
            "result",
            data_obj={"objects": results},
            )

        assert r.status_code == 202, r.text
        return r


class TestCase(object):
    """
    A test case that can be given a result.

    It holds the data downloaded from the client, and
    provides methods for marking pass, fail, invalid

    @@@ Carl: with something like this, should it actually extend a dictionary
    and add the special methods in?

    results objects look like this:
    {
        "environment": 33,
        "runcaseversion": 2,
        "tester": 1,
        "status": "failed",
        "comment": "from connector",
        "stepnumber": 2,
        "bug": "",
    }

    """

    def __init__(self, data):
        self.data = data
        self.result = None


    def __str__(self):
        return "<TestCase - {0}, result: {1}".format(
            str(self.data),
            str(self.result),
        )


    def finishsucceed(self, tester, environment):
        self.result = {
            "environment": environment,
            "runcaseversion": self.data["id"],
            "tester": tester,
            "status": "passed",
        }


    def finishfail(self, tester, environment, comment, stepnumber, bug=None):
        self.result = {
            "environment": environment,
            "runcaseversion": self.data["id"],
            "tester": tester,
            "status": "failed",
            "comment": comment,
            "stepnumber": stepnumber,
            "bug": bug,
            }


    def finishinvalidate(self, tester, environment, comment):
        self.result = {
            "environment": environment,
            "runcaseversion": self.data["id"],
            "tester": tester,
            "status": "invalidated",
            "comment": comment,
            }



class EnvironmentDoesNotExistException(Exception):
    pass