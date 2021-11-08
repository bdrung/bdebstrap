# Copyright (C) 2021, Benjamin Drung <bdrung@debian.org>
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

"""Run black code formatter in check mode."""

import subprocess
import sys
import unittest

from . import get_source_files, unittest_verbosity


class BlackTestCase(unittest.TestCase):
    """
    This unittest class provides a test that runs the black code
    formatter in check mode on the Python source code. The list of
    source files is provided by the get_source_files() function.
    """

    def test_black(self):
        """Test: Run black code formatter on Python source code."""

        cmd = ["black", "--check", "--diff", "-l", "99"] + get_source_files()
        if unittest_verbosity() >= 2:
            sys.stderr.write(f"Running following command:\n{' '.join(cmd)}\n")
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True
        ) as process:
            output = process.communicate()[0].decode()

        if process.returncode == 1:  # pragma: no cover
            self.fail(f"black found code that needs reformatting:\n{output.strip()}")
        if process.returncode != 0:  # pragma: no cover
            self.fail(f"black exited with code {process.returncode}:\n{output.strip()}")
