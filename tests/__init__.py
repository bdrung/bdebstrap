# Copyright (C) 2017-2021, Benjamin Drung <benjamin.drung@ionos.com>
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

"""Helper functions for testing."""

import inspect
import os
import unittest


def get_path(code_file: str) -> str:
    """Return relative or absolute path to given code file.

    During Debian package build, the current directory is
    changed to .pybuild/cpython3_*/build and the root directory
    is stored in the OLDPWD environment variable.
    """
    if os.path.exists(code_file):
        return code_file
    # The alternative path is needed for Debian's pybuild
    alternative = os.path.join(os.environ.get("OLDPWD", ""), code_file)
    if os.path.exists(alternative):
        return alternative
    return code_file


def get_source_files() -> list[str]:
    """Return a list of sources files/directories (to check with flake8/pylint)."""
    scripts = ["bdebstrap"]
    modules = ["tests"]
    py_files = ["setup.py"]

    files = []
    for code_file in scripts + modules + py_files:
        code_path = get_path(code_file)
        if code_file in scripts:
            with open(code_path, "rb") as script_file:
                shebang = script_file.readline().decode("utf-8")
            if "python" in shebang:
                files.append(code_path)
        else:
            files.append(code_path)
    return files


def unittest_verbosity() -> int:
    """
    Return the verbosity setting of the currently running unittest.

    If no test is running, return 0.
    """
    frame = inspect.currentframe()
    while frame:
        self = frame.f_locals.get("self")
        if isinstance(self, unittest.TestProgram):
            return self.verbosity
        frame = frame.f_back
    return 0  # pragma: no cover


class TestGetPath(unittest.TestCase):
    """Unittests for get_path function."""

    def test_get_path_exists(self) -> None:
        """Test get_path(__file__)."""
        path = get_path(__file__)
        self.assertEqual(path, __file__)

    def test_get_path_missing(self) -> None:
        """Test non-existing file for get_path()."""
        path = get_path(__file__ + "non-existing")
        self.assertEqual(path, __file__ + "non-existing")

    def test_get_path_pybuild(self) -> None:
        """Test changing current directory before calling get_path()."""
        relpath = os.path.relpath(__file__)
        oldpwd = os.environ.get("OLDPWD")
        curdir = os.getcwd()
        try:
            os.environ["OLDPWD"] = curdir
            os.chdir("/")
            path = get_path(relpath)
        finally:
            os.chdir(curdir)
            if oldpwd is not None:
                os.environ["OLDPWD"] = oldpwd
        self.assertEqual(os.path.normpath(path), __file__)
