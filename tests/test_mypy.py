# Copyright (C) 2023, Benjamin Drung <bdrung@ubuntu.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""Run mypy to check static typing of the Python code."""

import subprocess
import sys
import unittest

import ruamel.yaml

from . import get_source_files, unittest_verbosity


class MypyTestCase(unittest.TestCase):
    """
    This unittest class provides a test that runs mypy to check static
    typing of the Python code. The list of source files is provided by
    the get_source_files() function.
    """

    def test_mypy(self) -> None:
        """Test: Run mypy on Python source code."""
        if [int(x) for x in ruamel.yaml.__version__.split(".")] < [0, 18]:
            self.skipTest("false positives with ruamel.yaml < 0.18")
        cmd = ["mypy", "--strict"] + get_source_files()
        if unittest_verbosity() >= 2:
            sys.stderr.write(f"Running following command:\n{' '.join(cmd)}\n")
        process = subprocess.run(cmd, capture_output=True, check=False, text=True)

        if process.returncode != 0:  # pragma: no cover
            msgs = []
            if process.stderr:
                msgs.append(
                    f"mypy exited with code {process.returncode} and has"
                    f" unexpected output on stderr:\n{process.stderr.rstrip()}"
                )
            if process.stdout:
                msgs.append(f"mypy found issues:\n{process.stdout.rstrip()}")
            if not msgs:
                msgs.append(
                    f"mypy exited with code {process.returncode} "
                    "and has no output on stdout or stderr."
                )
            self.fail("\n".join(msgs))
