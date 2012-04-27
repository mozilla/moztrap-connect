#!python

from connect import Connect
#from mock import Mock, patch
#from requests import Response

#def test_get_runs(self):

connect = Connect("localhost:8000", "camd", "camd")
#print connect.get_runs(product="Firefox")
#print [str(x) for x in connect.get_tests(run_id=1)]
tests = connect.get_tests(run_id=1)
tests[0].markpass()
tests[1].markfail("why u no pass?", "http://deathvalleydogs.com")
tests[2].markinvalid("why u no make sense?")

print "\n".join([str((x.name, str(x.state))) for x in tests])

#print connect.get_environments(run_id=1)
print "id: {0}".format(connect.get_environment_id(run_id=1, element_list=["Chrome", "Mandarin", "OS dX"]))
