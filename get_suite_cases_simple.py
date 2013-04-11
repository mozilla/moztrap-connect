#!/usr/bin/env python

import csv
import httplib
import json
import sys
import urllib


def concatenate_list(items, delimiter):
    # Sanitizes the items to utf-8 and joins them.
    utf8_items = []
    for item in items:
        utf8_item = item.encode("utf-8", "replace")
        utf8_items.append(utf8_item)
    return delimiter.join(utf8_items)


def make_case_row(version, suite):
    # Requested target fields.
    # Note the encode("utf-8") anywhere you use data from the json object.
    # csv may not play nice w/ unicode, so this standardizes down.

    # Test case key (empty per request)
    case_id = version["case_id"]

    # Summary (name)
    summary = version["name"].encode("utf-8")

    # Tags (concatenate tags)
    tags = concatenate_list([tag["name"] for tag in version["tags"]], ", ")

    created_by = version["created_by"]
    if created_by:
        created_by = created_by["username"]
    else:
        created_by = "None"

    row = (case_id, summary, tags, created_by)

    return row


def main():
    # consts
    #  @@@ Need to make these sys.argv's. for now, modify these values:
    api_key = "foo"
    username = "usr"
    productversion_id = "-1"


    server = "moztrap.mozilla.org"
    url = ("/api/v1/caseselection/?format=json&limit=100&productversion={0}&"
           "username={1}&api_key={2}").format(
               productversion_id,
               username,
               api_key,
               )

    # Suite provided? If so, add to the url
    suite = None
    if len(sys.argv) > 1:
        suite = sys.argv[1]
        url += "&case__suites__in=%s" % (urllib.quote_plus(suite))


    # Results are paginated, so we're going to page through until done.
    end_of_set = False
    first_row = True

    while not end_of_set:
        # Get the data, check for success
        conn = httplib.HTTPSConnection(server)
        conn.request("GET", url)
        response = conn.getresponse()

        if response.status != 200:
            print "Could not connect to mozTrap. Status=%d, Reason=%s" % \
                  (response.status, response.reason)
            sys.exit()

        # Translate the JSON
        moztrap_data = json.load(response)

        # Handle pagination -- if we're not at the end of the set, the data
        # helpfully gives us the next URL to call to get the next page.
        end_of_set = moztrap_data["meta"]["next"] is None
        if not end_of_set:
            url = moztrap_data["meta"]["next"]

        moztrap_case_versions = moztrap_data["objects"]

        # No data back probably means a bad suite name
        if len(moztrap_case_versions) == 0:
            print ("Did not find any cases for '{0}'. Must use a valid"
                   " suite id").format(suite)
            sys.exit()

        # First time here? If so, we have some initializing to do. Didn't want
        # to do this up top because it doesn't make sense for empty responses.
        if first_row:
            writer = csv.writer(sys.stdout, dialect="excel")
            writer.writerow(("case_id", "summary",
                             "tags", "author"))
            first_row = False

        # Translate each row from the JSON data to a tuple and write it out
        for version in moztrap_case_versions:
            writer.writerow(make_case_row(version, suite))

if __name__ == "__main__":
    main()
