# Copyright (C) 2010, Stefano Rivera <stefanor@debian.org>
# Copyright (C) 2017-2018, Benjamin Drung <bdrung@debian.org>
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

"""Run pylint."""

import os
import re
import subprocess
import sys
import unittest

from . import get_source_files, unittest_verbosity

CONFIG = os.path.join(os.path.dirname(__file__), "pylint.conf")


class PylintTestCase(unittest.TestCase):
    """
    This unittest class provides a test that runs the pylint code check
    on the Python source code. The list of source files is provided by
    the get_source_files() function and pylint is purely configured via
    a config file.
    """

    def test_pylint(self):
        """Test: Run pylint on Python source code."""

        cmd = [sys.executable, "-m", "pylint", "--rcfile=" + CONFIG, "--"] + get_source_files()
        if unittest_verbosity() >= 2:
            sys.stderr.write(f"Running following command:\n{' '.join(cmd)}\n")
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True
        ) as process:
            out, err = process.communicate()

        if process.returncode != 0:  # pragma: no cover
            # Strip trailing summary (introduced in pylint 1.7). This summary might look like:
            #
            # ------------------------------------
            # Your code has been rated at 10.00/10
            #
            out = re.sub(
                "^(-+|Your code has been rated at .*)$", "", out.decode(), flags=re.MULTILINE
            ).rstrip()

            # Strip logging of used config file (introduced in pylint 1.8)
            err = re.sub("^Using config file .*\n", "", err.decode()).rstrip()

            msgs = []
            if err:
                msgs.append(
                    f"pylint exited with code {process.returncode} "
                    f"and has unexpected output on stderr:\n{err}"
                )
            if out:
                msgs.append(f"pylint found issues:\n{out}")
            if not msgs:
                msgs.append(
                    f"pylint exited with code {process.returncode} "
                    "and has no output on stdout or stderr."
                )
            self.fail("\n".join(msgs))
