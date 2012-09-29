#!python

from mtconnect.connect import Connect, TestResults
import json
import datetime


def jstr(obj):
    return json.dumps(obj, sort_keys=True, indent=4)


def getters():

    connect = Connect("http", "localhost:8000", "camd", "abc123", DEBUG=True)


    products = connect.get_products()
    print jstr(products)

    products = connect.get_products(name="MozTrap")
    print jstr(products)

    runs = connect.get_runs(productversion_id=7)
    print jstr(runs)

    env = connect.get_run_environments(run_id=1)
    print jstr(env)

    penv = connect.get_product_environments(productversion_id=7)

    pcases = connect.get_product_cases(productversion_id=7, environment_id=62)

    rcases = connect.get_run_cases(run_id=1, environment_id=22)


"""

Get a list of runs
pick the run, and get a list of cases for that run
set results for each case
post those results

"""


def submit_results_ui_way():

    connect = Connect("http", "localhost:8000", "camd", "abc123", DEBUG=True)


    runs = connect.get_runs()
    print jstr(runs)

    # here pick the run you want
    run_id = runs[0]["id"]

    envs = connect.get_run_environments(run_id=run_id)
    print jstr(envs)

    # here pick the env you want
    env_id = envs[22]["id"]

    tests = connect.get_run_cases(run_id=run_id, environment_id=env_id)
    print jstr(tests)


    results = TestResults()

    results.addpass(
        case_id=tests[0]["caseversion"]["case"]["id"],
        environment_id=env_id,
    )

    results.addinvalid(
        case_id=tests[1]["caseversion"]["case"]["id"],
        environment_id=env_id,
        comment="why u no make sense??"
    )

    results.addfail(
        case_id=tests[2]["caseversion"]["case"]["id"],
        environment_id=env_id,
        comment="why u no pass?",
        bug="http://www.deathvalleydogs.com",
        stepnumber=1,
    )

    r = connect.submit_results(run_id=run_id, testresults=results)
    print r.text


def submit_results_auto_way():
    connect = Connect("http", "localhost:8000", "camd", "abc123", DEBUG=True)

    products = connect.get_products(name="Zurago")
    print(jstr(products))

    pv_id = products[0]["productversions"][0]["id"]

    envs = connect.get_product_environments(productversion_id=pv_id)
    print(jstr(envs))

    lin_id = envs[0]["id"]
    win_id = envs[1]["id"]
    span_id = envs[2]["id"]

    spancases = connect.get_product_cases(
        productversion_id=pv_id, environment_id=span_id)
    wincases = connect.get_product_cases(
        productversion_id=pv_id, environment_id=win_id)
    lincases = connect.get_product_cases(
        productversion_id=pv_id, environment_id=lin_id)
    print(jstr(wincases))

    results = TestResults()


    for caseversion in spancases:
        results.addinvalid(
            case_id=caseversion["case"]["id"],
            environment_id=span_id,
            comment="what the hellfire?"
            )

    for caseversion in wincases:
        results.addpass(
            case_id=caseversion["case"]["id"],
            environment_id=win_id,
            )

    for caseversion in lincases:
        results.addfail(
            case_id=caseversion["case"]["id"],
            environment_id=lin_id,
            comment="dang thing..."
            )

    res = connect.submit_run(
        "first run: {0}".format(datetime.datetime.now()),
        "a description",
        productversion_id=pv_id,
        testresults=results,
        )
    print(res)


getters()
submit_results_ui_way()
submit_results_auto_way()
