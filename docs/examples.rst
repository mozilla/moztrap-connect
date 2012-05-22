Examples
========

New Run
-----------------------------

Create a new Run with results

Commonly, an automated test will know the test case IDs that each
test applies to, and will want to execute those tests, and create
a run on the fly for those results.

Example::

        from mtconnect.connect import Connect, TestResults
        import json

        connect = Connect("http", "localhost:8000", "camd", "abc123", DEBUG=True)

        # get the product of "Zurago" and its product versions

        products = connect.get_products(name="Zurago")
        pv_id = products[0]["productversions"][0]["id"]

        envs = connect.get_product_environments(productversion_id=pv_id)

        # get the environment ids for the envs we care about

        env_id = envs[0]["id"]

        # get the cases for each env for the product version

        cases = connect.get_product_cases(
            productversion_id=pv_id, environment_id=env_id)

        # repository for the results we will be collecting

        results = TestResults()

        # submit tests for each case / env.  It's possible to
        # submit results for the same case for multiple environments
        # with the same results object.

        results.addpass(case_id=243, environment_id=env_id)
        results.addfail(
                case_id=244,
                environment_id=env_id,
                comment="dang thing..."
                stepnumber=3,
                bug="https://bugzilla.mycompany.com"
                )
        results.addinvalid(
                case_id=245,
                environment_id=env_id,
                comment="what the?"
                )

        # submit those results back to MozTrap

        res = connect.submit_run(
            "Smoke tests for build: {0}".format(build_id),
            "The awesome smoketests",
            productversion_id=pv_id,
            testresults=results,
            )


Existing Run
------------

Submit results for an existing Run.

If a test run already exists that you would like to submit results
for, then this example is for you.

Example::

        from mtconnect.connect import Connect, TestResults
        import json

        connect = Connect("http", "localhost:8000", "camd", "abc123", DEBUG=True)
        runs = connect.get_runs()

        # run you want
        run_id=runs[0]["id"]

        envs = connect.get_run_environments(run_id=run_id)

        # env you want
        env_id=envs[22]["id"]

        tests = connect.get_run_cases(run_id=run_id, environment_id=env_id)
        print jstr(tests)

        # the object to accumulate all your test results

        results = TestResults()

        results.addpass(case_id=243, environment_id=env_id)
        results.addfail(
                case_id=244,
                environment_id=env_id,
                comment="dang thing..."
                stepnumber=3,
                bug="https://bugzilla.mycompany.com"
                )
        results.addinvalid(
                case_id=245,
                environment_id=env_id,
                comment="what the?"
                )

        r = connect.submit_results(run_id=run_id, testresults=results)

