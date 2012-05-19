This is a collection of connectors that can be used to communicate with
Case Conductor.  This is an easier way for external automation tools to provide
results to Case Conductor than to use the REST API directly.

Notes:
on cmd line specify:
product,
product version - need endpoint for all productversions for the product
environment - need endpoint for all environments for the productversion
tests submit (case_id, pass/fail/invalid, comment, step_number=1, bugurl=None)

after submit results, return a link to the "view results" for that test run
get list of test cases (product version, environment) with tags

create a new testrun for these tests per environment.  don't need to blend them
for multiple environments

return a results url for the run in moztrap




Authentication
--------------

You will need an API key from MozTrap to use this connector.  You may have a
user in MozTrap that is specifically an "automation bot" that uses this API
key to submit results, or it could be any other user, too.  Ask your MozTrap
admin to generate an API key and provide it to you.

GET
---

- List of Products with their productversions.  Filterable by Product
name::

    get_products(name)


- List of Environments for a Product Version::

    get_product_environments(productversion_id)


- List of CaseVersions for a Product Version and environment::

    get_product_cases(productversion_id, environment_id)


- List of Test Runs::

    get_runs(productversion_id)

    - **return**::

        {
            "meta": {
                "limit": 20,
                "next": null,
                "offset": 0,
                "previous": null,
                "total_count": 3
            },
            "objects": [
                {
                    "description": "test run description",
                    "id": "1",
                    "name": "Alpha 1",
                    "resource_uri": "/api/v1/run/1/"
                },
            ]
        }

- Test cases for specific test run::

    get_run_cases(run_id)

    - **return**::

        {

            "cases": [
                {
                    "description": "A user can log in to the app.",
                    "id": 1,
                    "name": "Can log in.",
                    "prefix_id": 1
                },
                {
                    "description": "A new user can register for the app.\r\n**C:\\\\Users\\\\{your user name}\\\\**",
                    "id": 2,
                    "name": "Can register.",
                    "prefix_id": "abc-xyz-2"
                }
            ],
            "description": "test run description",
            "id": "1",
            "name": "Alpha 1",
            "product_name": "MozTrap",
            "productversion_version": "0.8",
            "resource_uri": "/api/v1/runcases/1/"
        }

- Environments for a test run::

    get_run_environments(run_id)

    - **return**::

    {

        "description": "test run description",
        "environments": [
            {
                "environment": [
                    "Chrome",
                    "Mandarin",
                    "Windows"
                ],
                "id": 1
            },
            {
                "environment": [
                    "Chrome",
                    "Mandarin",
                    "OS X"
                ],
                "id": 2
            }
        ],
        "id": "1",
        "name": "Alpha 1",
        "resource_uri": "/api/v1/runenvironments/1/"

    }

POST
----

- Submit test results::

    submit_new_run_results(productversion_id, environment_id, result_list)

