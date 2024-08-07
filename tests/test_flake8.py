# Copyright (C) 2017-2018, Benjamin Drung <bdrung@debian.org>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Run flake8 check."""

import os
import subprocess
import sys
import unittest

from . import get_source_files, unittest_verbosity


class Flake8TestCase(unittest.TestCase):
    """
    This unittest class provides a test that runs the flake8 code
    checker (which combines pycodestyle and pyflakes) on the Python
    source code. The list of source files is provided by the
    get_source_files() function.
    """

    @unittest.skipIf(os.environ.get("SKIP_LINTERS"), "requested via SKIP_LINTERS env variable")
    def test_flake8(self) -> None:
        """Test: Run flake8 on Python source code."""
        cmd = [sys.executable, "-m", "flake8", "--max-line-length=99"] + get_source_files()
        if unittest_verbosity() >= 2:
            sys.stderr.write(f"Running following command:\n{' '.join(cmd)}\n")
        process = subprocess.run(cmd, capture_output=True, check=False, text=True)

        if process.returncode != 0:  # pragma: no cover
            msgs = []
            if process.stderr:
                msgs.append(
                    f"flake8 exited with code {process.returncode} and has"
                    f" unexpected output on stderr:\n{process.stderr.rstrip()}"
                )
            if process.stdout:
                msgs.append(f"flake8 found issues:\n{process.stdout.rstrip()}")
            if not msgs:
                msgs.append(
                    f"flake8 exited with code {process.returncode} "
                    "and has no output on stdout or stderr."
                )
            self.fail("\n".join(msgs))
