This is a collection of connectors that can be used to communicate with
Case Conductor.  This is an easier way for external automation tools to provide
results to Case Conductor than to use the REST API directly.

Notes:
~~~~~~
on cmd line specify:

* product version - need endpoint for all productversions for the product
* environment - need endpoint for all environments for the productversion
* tests submit (case_id, pass/fail/invalid, comment, step_number=1, bugurl=None)

TODO::

    * after submit results, return a link to the "view results" for that test run
    get list of test cases (product version, environment) with tags

    * return a results url for the run in moztrap




Authentication
--------------

You will need an API key from MozTrap to use this connector.  You may have a
user in MozTrap that is specifically an "automation bot" that uses this API
key to submit results, or it could be any other user, too.  Ask your MozTrap
admin to generate an API key and provide it to you.



