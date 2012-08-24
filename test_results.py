#!python

from mtconnect.connect import TestResults as TResults

class TestResults(object):

    def test_failure_can_be_added(self):
        collector = TResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        stepno = "3"
        bug = "786"
        collector.addfail(case_id, env_id, comment, stepno, bug)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": comment,
            "stepnumber": stepno,
            "bug": bug,
        }
        print collector.results
        assert expected in collector.results

    def test_pass_can_be_added(self):
        collector = TResults()
        env_id = "1"
        case_id = "1"
        collector.addpass(case_id, env_id)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "passed",
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_invalid_can_be_added(self):
        collector = TResults()
        env_id = "1"
        case_id = "1"
        comment = "first invalid"
        collector.addinvalid(case_id, env_id, comment)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "invalidated",
            "comment": comment,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_failure_can_overwrite_pass(self):
        collector = TResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        collector.addpass(case_id, env_id)
        collector.addfail(case_id, env_id, comment)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": comment,
            "bug": None,
            "stepnumber": 0,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_failure_can_overwrite_invalid(self):
        collector = TResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        collector.addinvalid(case_id, env_id, "first invalid")
        collector.addfail(case_id, env_id, comment)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": comment,
            "bug": None,
            "stepnumber": 0,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_failure_appends_failure(self):
        collector = TResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        collector.addfail(case_id, env_id, comment)
        collector.addfail(case_id, env_id, "second failure")

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": comment + "\nsecond failure",
            "bug": None,
            "stepnumber": 0,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_pass_cannot_overwrite_failure(self):
        collector = TResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        collector.addfail(case_id, env_id, comment)
        collector.addpass(case_id, env_id)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": comment,
            "bug": None,
            "stepnumber": 0,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_pass_can_overwrite_invalid(self):
        collector = TResults()
        env_id = "1"
        case_id = "1"
        comment = "first invalid"
        collector.addinvalid(case_id, env_id, comment)
        collector.addpass(case_id, env_id)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "passed",
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    # nobody cares if pass overwrites pass

    def test_invalid_cannot_overwrite_pass(self):
        collector = TResults()
        env_id = "1"
        case_id = "1"
        comment = "first invalid"
        collector.addpass(case_id, env_id)
        collector.addinvalid(case_id, env_id, comment)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "passed",
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_invalid_cannot_overwite_fail(self):
        collector = TResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        collector.addfail(case_id, env_id, comment)
        collector.addinvalid(case_id, env_id, "first invalid")

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": comment,
            "bug": None,
            "stepnumber": 0,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_invalid_appends_invalid(self):
        collector = TResults()
        env_id = "1"
        case_id = "1"
        comment = "first invalid"
        collector.addinvalid(case_id, env_id, comment)
        collector.addinvalid(case_id, env_id, "second invalid")

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "invalidated",
            "comment": comment + "\nsecond invalid",
        }
        assert expected in collector.results
        assert len(collector.results) == 1
