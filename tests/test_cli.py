import subprocess
import sys
import unittest

from tidyid import is_valid_id


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "tidyid", *arguments],
        check=False,
        capture_output=True,
        encoding="utf-8",
    )


class CliTests(unittest.TestCase):
    def test_generates_default_and_custom_size_ids(self) -> None:
        default = run_cli()
        self.assertEqual(default.returncode, 0)
        self.assertTrue(is_valid_id(default.stdout.strip(), 32))

        sized = run_cli("--size", "16")
        self.assertEqual(sized.returncode, 0)
        self.assertTrue(is_valid_id(sized.stdout.strip(), 16))

        short = run_cli("-s", "3")
        self.assertEqual(short.returncode, 0)
        self.assertTrue(is_valid_id(short.stdout.strip(), 3))

        uppercase = run_cli("--allow-uppercase", "--size", "64")
        self.assertEqual(uppercase.returncode, 0)
        self.assertTrue(is_valid_id(uppercase.stdout.strip(), 64, True))

        short_uppercase = run_cli("-u", "-s", "3")
        self.assertEqual(short_uppercase.returncode, 0)
        self.assertTrue(is_valid_id(short_uppercase.stdout.strip(), 3, True))

    def test_reports_metadata_and_rejects_invalid_arguments(self) -> None:
        self.assertEqual(run_cli("--version").stdout.strip(), "2.1.0")
        self.assertIn("--size", run_cli("--help").stdout)
        self.assertIn("--allow-uppercase", run_cli("--help").stdout)

        invalid_size = run_cli("--size", "2")
        self.assertEqual(invalid_size.returncode, 1)
        self.assertIn("between 3 and 256", invalid_size.stderr)

        missing_size = run_cli("--size")
        self.assertEqual(missing_size.returncode, 1)
        self.assertIn("between 3 and 256", missing_size.stderr)

        for value in ("3_0", "3.0", "0x10", "٣"):
            with self.subTest(value=value):
                malformed_size = run_cli("--size", value)
                self.assertEqual(malformed_size.returncode, 1)
                self.assertIn("between 3 and 256", malformed_size.stderr)

        unknown = run_cli("--unknown")
        self.assertEqual(unknown.returncode, 1)
        self.assertIn("Unknown argument --unknown", unknown.stderr)


if __name__ == "__main__":
    unittest.main()
