# Copyright (C) 2021-2022, Benjamin Drung <bdrung@posteo.de>
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

"""Run shellcheck on Shell code."""

import subprocess
import sys
import unittest

from . import get_path, unittest_verbosity

SHELL_SCRIPTS = ["hooks/disable-units", "hooks/enable-units"]


class ShellcheckTestCase(unittest.TestCase):
    """
    This unittest class provides a test that runs the shellcheck
    on Shell source code.
    """

    def test_flake8(self):
        """Test: Run shellcheck on Shell source code."""
        cmd = ["shellcheck"] + [get_path(s) for s in SHELL_SCRIPTS]
        if unittest_verbosity() >= 2:
            sys.stderr.write(f"Running following command:\n{' '.join(cmd)}\n")
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True
        ) as process:
            out, err = process.communicate()

        if process.returncode != 0:  # pragma: no cover
            msgs = []
            if err:
                msgs.append(
                    f"shellcheck exited with code {process.returncode} "
                    f"and has unexpected output on stderr:\n{err.decode().rstrip()}"
                )
            if out:
                msgs.append(f"shellcheck found issues:\n{out.decode().rstrip()}")
            if not msgs:
                msgs.append(
                    f"shellcheck exited with code {process.returncode} "
                    "and has no output on stdout or stderr."
                )
            self.fail("\n".join(msgs))
