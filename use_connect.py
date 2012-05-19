#!python

from connect import Connect, TestResults
import json
import datetime

def jstr(obj):
    return json.dumps(obj, sort_keys=True, indent=4)


def getters():

    connect = Connect("http", "localhost:8000", "camd", "abc123", DEBUG=True)


    runs = connect.get_runs(product="MozTrap")
    print jstr(runs)

    env = connect.get_environments(run_id=1)
    #print jstr(env)


    env_id = connect.get_environment_id(
        run_id=1,
        element_list=["Chrome", "Mandarin", "Windows"],
        )
    #print "\nenv_id: {0}".format(env_id)


"""

Get a list of runs
pick the run, and get a list of cases for that run
set results for each case
post those results

"""

def submit_results_ui_way():

    connect = Connect("localhost:8000", "camd", "abc123", DEBUG=True)


    runs = connect.get_runs(product="MozTrap")
    #print jstr(runs)

    env = connect.get_environments(run_id=1)
    #print jstr(env)


    env_id = connect.get_environment_id(
        run_id=1,
        element_list=["Chrome", "Mandarin", "Windows"],
        )
    print "\nenv_id: {0}".format(env_id)



    tests = connect.get_testcases(run_id=1, environment_id=env_id)
    #print jstr([x.data for x in tests])

    tests[0].finishsucceed(
        tester=1,
        environment=env_id,
        )
    tests[1].finishfail(
        tester=1,
        environment=env_id,
        comment="why u no pass?",
        bug="http://deathvalleydogs.com",
        stepnumber=1,
        )
    tests[2].finishinvalidate(
        tester=1,
        environment=env_id,
        comment="why u no make sense?",
        )



    result_list = connect.get_results(tests)
    print (jstr(result_list))

    r = connect.submit_results(result_list=result_list, testcase_list=tests)
    print r.text

    r = connect.submit_results(testcase_list=tests)
    print r.text


def submit_results_auto_way():
    connect = Connect("http", "localhost:8000", "camd", "abc123", DEBUG=True)

#    products = connect.get_products(name="Zurago")
#    print(jstr(products))
#
#    envs = connect.get_product_environments(productversion_id=7)
#    print(jstr(envs))

    spancases = connect.get_product_cases(
        productversion_id=7, environment_id=63)
    wincases = connect.get_product_cases(
        productversion_id=7, environment_id=62)
    lincases = connect.get_product_cases(
        productversion_id=7, environment_id=61)
    print(jstr(wincases))

    results = TestResults()


    for caseversion in spancases:
        results.addinvalid(
            case_id=caseversion["case"]["id"],
            environment_id=63,
            comment="what the hellfire?"
            )

    for caseversion in wincases:
        results.addpass(
            case_id=caseversion["case"]["id"],
            environment_id=62,
            )

    for caseversion in lincases:
        results.addfail(
            case_id=caseversion["case"]["id"],
            environment_id=61,
            comment="dang thing..."
            )

    res = connect.submit_run(
        "first run: {0}".format(datetime.datetime.now()),
        "a description",
        productversion_id=7,
        testresults=results,
        )
    print(res)

submit_results_auto_way()
#getters()