This is a collection of connectors that can be used to communicate with
Case Conductor.  This is an easier way for external automation tools to provide
results to Case Conductor than to use the REST API directly.

Authentication
--------------

- Login::

    login(username, password)

- Logout::

    logout(username, password)


GET
---

- List of Test Runs::

    get_runs(product, product_version)

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

    get_cases(run_id)

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

- Environments for specific test run::

    get_environments(run_id)

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
        },
        {
            "environment": [
                "Chrome",
                "Linux",
                "Mandarin"
            ],
            "id": 3
        },
        {
            "environment": [
                "English",
                "OS X",
                "Safari"
            ],
            "id": 45
        }
    ],
    "id": "1",
    "name": "Alpha 1",
    "resource_uri": "/api/v1/runenvironments/1/"

}

POST
----

- Clone existing run::

    clone_run(run_id, new_name)

- Submit test results::

    submit_results(case_list)

