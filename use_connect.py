#!python

from connect import Connect
import json

def jstr(obj):
    return json.dumps(obj, sort_keys=True, indent=4)

"""

Get a list of runs
pick the run, and get a list of cases for that run
set results for each case
post those results

"""



connect = Connect("localhost:8000", "camd", "camd")


runs = connect.get_runs(product="MozTrap")
print jstr(runs)


env = connect.get_environments(run_id=1)
print jstr(env)


env_id = connect.get_environment_id(
    run_id=1,
    element_list=["Chrome", "Mandarin", "Windows"],
    )
print "\nenv_id: {0}".format(env_id)

#results = connect.get_results(1, 33)
#print jstr(results.text)

tests = connect.get_testcases(run_id=1, environment_id=env_id)
print jstr([x.data for x in tests])


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

#print "\n".join([str((x.data["name"], str(x.result.state))) for x in tests])

r = connect.submit_results(tests)
print r.text
