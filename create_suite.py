#!python

import sys
import json
import csv
from mtconnect.connect import Connect


def create_suite(connect, name):
    """Create the specified suite"""

    body = {
        "description": "New test suite",
        "name": name,
        "product": "/api/v1/product/16/",
        "status": "active"
    }

    r = connect.do_post("suite", data_obj=body)
    if r:
        print r.text
        result = json.loads(r.text)
        return result["id"]
    else:
        "unknown error while posting"


def add_cases(connect, suite, cases):
    """Add all the cases to the specified suite"""

    order = 1
    for case in cases:

        body = {
            "suite": "/api/v1/suite/{0}/".format(suite),
            "order": order,
            "case": "/api/v1/case/{0}/".format(case)
        }

        r = connect.do_post("suitecase", data_obj=body)
        print r
        order += 1


def get_cases(filename):
    """Compile the list of case IDs to add"""

    cases = []
    with open(filename, "rbU") as f:
        reader = csv.DictReader(f)
        already_added = []
        for row in reader:
            case_id = row["case"]
            if not case_id in already_added:
                cases.append(case_id)
                already_added.append(case_id)
    return cases

def main():
    if len(sys.argv) == 5:
        suite_name = sys.argv[1]
        username = sys.argv[2]
        api_key = sys.argv[3]
        file_name = sys.argv[4]

        conn = Connect(
            "https",
            "moztrap.mozilla.org",
            # "http",
            # "localhost:8000",
            username,
            api_key,
            DEBUG=True,
            )

        suite = create_suite(conn, suite_name)
        cases = get_cases(file_name)
        add_cases(conn, suite=suite, cases=cases)

    else:
        print "Usage: create_suite <suitename> <username> <api_key> <filename.csv>"


if __name__ == "__main__":
    main()
