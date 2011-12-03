import requests

class CCConnect:
    def __init__(self, host, username, password):
        self.host = host
        self.auth = (username, password)
        # ping the host to make sure it's valid?


    """params are text name values of objects
        Sample return JSON:
        {"productId": 6,
         "testCycleId": 14,
         "testRunId": 3,
         "tests": [
             {"testCaseId": 10, "testResultId": 25, "testCaseName": "Special Test 1", "result": "pending"},
             {"testCaseId": 11, "testResultId": 26, "testCaseName": "Special Test 2", "result": "pending"},
             {"testCaseId": 12, "testResultId": 27, "testCaseName": "Special Test 3", "result": "pending"}
         ]}

    """
    def get_tests(self, product, test_cycle, test_run):
        '''Return a list of test result objects.  Pass/Fail can be applied to them'''
    
        # may need to do individual calls to fetch the ids of the product, cycle and run?
    
        get_tests_url = "%s/included_test_results?product=%s&cycle=%s&run=%s" % ("host", "product", "test_cycle", "test_run")

        r = requests.get(get_tests_url, auth=self.auth)
        assert r.status_code == 200
    
        return r.content
    
    """
        Sample submission values:
        {"productId": 6,
         "testCycleId": 14,
         "testRunId": 3,
         "tests": [
             {"testCaseId": 10, "testResultId": 25, "testCaseName": "Special Test 1", "result": "pending"},
             {"testCaseId": 11, "testResultId": 26, "testCaseName": "Special Test 2", "result": "pending"},
             {"testCaseId": 12, "testResultId": 27, "testCaseName": "Special Test 3", "result": "pending"}
         ],
         "environment": {"category1": "value1", "category2": "value2", "category3": "value3"}
         }
        """
    def set_results(self, tests, environment):
        '''Submit the tests back to the system with results.  Results are not required for any of the tests.  '''
        test_result_list
        set_results_url = "%s/submit_results?product=%s&cycle=%s&run=%s" % (self.host, product, test_cycle, test_run)
    
        r = requests.post(get_tests_url, data=tests, auth=self.auth)
        assert r.status_code == 200
    