from shlex import split as shlex_split
from subprocess import PIPE, Popen, run
from unittest import TestCase

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class TestCLI(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        cls.session.mount('http://', HTTPAdapter(max_retries=retries))
        cls.session.mount('https://', HTTPAdapter(max_retries=retries))

    def test_simple_case(self):
        command = "fk-graph --demo --table=table_a --primary-key=1"
        # PIPE just stops stdout from printing to screen.
        process = Popen(shlex_split(command), stdout=PIPE)
        self.addCleanup(process.terminate)
        response = self.session.get("http://localhost:8050")
        # Because of the javascripty-nature of the app, we can
        # only really inspect the status code.
        self.assertEqual(response.status_code, 200)

    def test_errors_if_both_demo_and_connection_string_included(self):
        command = (
            "fk-graph"
            " --demo"
            " --connection-string=\"sqlite+pysqlite:///:memory:\""
            " --table=table_a"
            " --primary-key=1"
        )
        completed_process = run(
            shlex_split(command),
            capture_output=True,
            text=True,
            timeout=5
        )
        self.assertEqual(completed_process.returncode, 2)
        self.assertIn(
            "Exactly one of --demo and --connection-string should be used.",
            completed_process.stderr
        )

    def test_errors_if_neither_demo_or_connection_string_included(self):
        command = (
            "fk-graph"
            " --table=table_a"
            " --primary-key=1"
        )
        completed_process = run(
            shlex_split(command),
            capture_output=True,
            text=True,
            timeout=5
        )
        self.assertEqual(completed_process.returncode, 2)
        self.assertIn(
            "Exactly one of --demo and --connection-string should be used.",
            completed_process.stderr
        )
