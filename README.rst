This is a collection of connectors that can be used to communicate with
Case Conductor.  This is an easier way for external automation tools to provide
results to Case Conductor than to use the REST API directly.

Authentication
--------------

- Login::

    ```login(username, password)```

- Logout::

    ```logout(username, password)```


GET
---

- List of Test Runs::

    ```get_runs(product, product_version)```

- Test cases for specific test run::

    ```get_cases(run_id, verbose)```

  - **return**::

      {
          "run_id": run_id,
          "cases: [
            "id": id,
            "summary": test_case_summary,
            "status": status
            ]
          }

POST
----

- Clone existing run::

    ```clone_run(run_id)```

- Submit test results::

    ```submit_results(case_list)```

