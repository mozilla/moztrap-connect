This is a connector that can be used to communicate with
MozTrap.  This is an easier way for external automation tools to provide
results to Case Conductor than to use the REST API directly.

Documentation
-------------

http://readthedocs.org/docs/moztrap-connect/en/latest/


Authentication
--------------

You will need an API key from MozTrap to use this connector.  You may have a
user in MozTrap that is specifically an "automation bot" that uses this API
key to submit results, or it could be any other user, too.  Ask your MozTrap
admin to generate an API key and provide it to you.  If you ARE the MozTrap
admin, then use the /admin panel, and create an API key in the Core / ApiKeys
table for the user you want.


Installation
------------
This package can be installed using
    $ python setup.py install
or
    $ python setup.py develop

It is also pip installable by putting the following line in your requirements.txt file.
    git+https://github.com/camd/moztrap-connect.git

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

Running the tests:
-----------------------------
Running the tests for this project requires the following py.test flags:
    --test-mt-username
    --test-mt-apikey





