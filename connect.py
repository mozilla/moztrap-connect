import requests
from urllib import urlencode
from json import loads

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

    """
    def __init__(self, host, username, password, DEBUG=0):
        self.DEBUG = DEBUG
        self.host = host
        self.auth = (username, password)
        # ping the host to make sure it's valid?


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


        r = requests.get(
            "http://{0}/api/v1/run?format=json&{1}".format(
                self.host,
                urlencode(params),
                ))
        return loads(r.text)


    def get_environments(self, run_id):
        """
        Return a list of environments for the specified test run.

        """

        r = requests.get(
            "http://{0}/api/v1/runenvironments/{1}?format=json".format(
                self.host,
                run_id,
                ))
        assert r.status_code == 200

        return loads(r.text)["environments"]


    def get_environment_id(self, run_id, element_list):
        """
        Return a single environment id for the specified test run that
        matches the element_list of strings.

        @@@ This is probably more efficiently handled on the server in a
        different endpoint
        """

        envs = self.get_environments(run_id)
        exp_env = set(element_list)

        try:
            env_id = next(item["id"] for item in envs if
                exp_env == set(item["environment"]))

        except:
            raise EnvironmentDoesNotExistException(
                "Run with id {0} does not have environment: {1}".format(
                    run_id,
                    element_list,
                    ))

        return env_id

    def get_tests(self, run_id):
        """
        Return a list of TestCase objects.  Pass/Fail/Invalid is set on each
        object in the list.

        """

        r = requests.get("http://{0}/api/v1/runcases/{1}?format=json".format(
            self.host,
            run_id,
            ))
        assert r.status_code == 200

        return [TestCase(x) for x in loads(r.text)["cases"]]


    def post_results(self, test_cases, environment, auth):
        """
        Submit the tests back to the system with results.
        Results are not required for any of the tests.

        """

        data = {"cases": test_cases,
                "environment": environment,
                }

        if DEBUG:
            print "host={0}".format(self.host)

        r = requests.post(
            "http://{0}/api/v1/runresults/{1}?format=json".format(
                self.host,
                run_id,
                ),
            data=loads(data), auth=auth,
        )
        assert r.status_code == 200



class TestCase(object):
    FAIL = "fail"
    PASS = "pass"
    INVALID = "invalid"
    PENDING = "pending"

    def __init__(self, data):
        self.name = data["name"]
        self.id = data["id"]
        self.prefix_id = data["prefix_id"]
        self.description = data["description"]
        self.state = {"result": TestCase.PENDING}


    def __str__(self):
        return "<TestCase - name: {0}, id: {1}, prefix_id: {2}, description: {3}, state: {4}".format(
            self.name,
            str(self.id),
            str(self.prefix_id),
            self.description,
            str(self.state),
        )


    def markpass(self):
        self.state = {"result": TestCase.PASS}


    def markfail(self, comment, bug_url=None):
        self.state = {
            "result": TestCase.FAIL,
            "comment": comment,
            "bug_url": bug_url,
            }

    def markinvalid(self, comment):
        self.state = {
            "result": TestCase.INVALID,
            "comment": comment,
            }

class EnvironmentDoesNotExistException(Exception):
    pass