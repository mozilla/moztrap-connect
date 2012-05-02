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

    def get_tests(self, run_id, environment_id):
        """
        Return a list of TestCase objects.  Pass/Fail/Invalid is set on each
        object in the list.  The list of environments is filtered by the
        environment, just as it would be in the UI of MozTrap.

        """

        r = requests.get("http://{0}/api/v1/runcases/{1}?format=json&environment_id={2}".format(
            self.host,
            run_id,
            environment_id
            ))
        assert r.status_code == 200

        return [TestCase(x, environment_id) for x in loads(r.text)["cases"]]


    def post_results(self, test_cases, auth):
        """
        Submit the tests back to the system with results.
        Results are not required for any of the tests.

        """

        data = {"results": [x.result for x in test_cases]}

        r = requests.post(
            "http://{0}/api/v1/results/?format=json&run_id={1}".format(
                self.host,
                run_id,
                ),
            data=loads(data),
            auth=auth,
            )
        assert r.status_code == 200



class TestCase(object):

    def __init__(self, data, environment_id):
        self.name = data["name"]
        self.id = data["id"]
        self.prefix_id = data["prefix_id"]
        self.description = data["description"]
        self.result = TestResult(self.id, environment_id)


    def __str__(self):
        return "<TestCase - name: {0}, id: {1}, prefix_id: {2}, description: {3}, result: {4}".format(
            self.name,
            str(self.id),
            str(self.prefix_id),
            self.description,
            str(self.result),
        )


    def markpass(self):
        self.result.markpass()


    def markfail(self, comment, bug_url=None):
        self.result.markfail(comment, bug_url)


    def markinvalid(self, comment):
        self.result.markinvalid(comment)



class TestResult(object):
    FAIL = "failed"
    PASS = "passed"
    INVALID = "invalidated"
    PENDING = "pending"


    def __init__(self, caseversion_id, state=self.PENDING, comment=None, bug_url=None):
        self.caseversion_id = caseversion_id
        self.environment_id = environment_id
        self.state = state
        self.comment = comment
        self.bug_url = bug_url


    def markpass(self):
        self.state = TestCase.PASS
        self.comment = None
        self.bug_url = None


    def markfail(self, comment, bug_url=None):
        self.state = TestCase.FAIL
        self.comment = comment
        self.bug_url = bug_url


    def markinvalid(self, comment):
        self.state = TestCase.INVALID
        self.comment = comment
        self.bug_url = None



class EnvironmentDoesNotExistException(Exception):
    pass