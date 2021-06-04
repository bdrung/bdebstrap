# Copyright (C) 2021 Benjamin Drung <bdrung@posteo.de>
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

"""Test main function of bdebstrap."""

import os
import subprocess
import unittest
import unittest.mock

from bdebstrap import main

EXAMPLE_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")


class TestMain(unittest.TestCase):
    """
    This unittest class tests the main function.
    """

    @unittest.mock.patch("bdebstrap.Config.save")
    @unittest.mock.patch("bdebstrap.prepare_output_dir")
    @unittest.mock.patch("bdebstrap.Mmdebstrap.call")
    def test_debian_example(self, mmdebstrap_call_mock, prepare_output_dir_mock, config_save_mock):
        """Test Debian unstable example."""
        args = [
            "-c",
            os.path.join(EXAMPLE_CONFIG_DIR, "Debian-unstable.yaml"),
            "--name",
            "Debian-unstable",
        ]
        with self.assertLogs("bdebstrap", level="INFO") as context_manager:
            self.assertEqual(main(args), 0)
            self.assertIn("Execution time", context_manager.output[-1])
        config_save_mock.assert_called_once_with("./Debian-unstable/config.yaml", False)
        mmdebstrap_call_mock.assert_called_once_with("./Debian-unstable", False)
        prepare_output_dir_mock.assert_called_once_with("./Debian-unstable", False, False)

    @unittest.mock.patch("bdebstrap.Config.save")
    @unittest.mock.patch("bdebstrap.prepare_output_dir")
    @unittest.mock.patch("bdebstrap.Mmdebstrap.call")
    def test_failed_mmdebstrap(
        self, mmdebstrap_call_mock, prepare_output_dir_mock, config_save_mock
    ):
        """Test failure of mmdebstrap call."""
        mmdebstrap_call_mock.side_effect = subprocess.CalledProcessError(42, "mmdebstrap")
        args = [
            "-c",
            os.path.join(EXAMPLE_CONFIG_DIR, "Debian-unstable.yaml"),
            "--name",
            "foobar",
        ]
        with self.assertLogs("bdebstrap", level="ERROR") as context_manager:
            self.assertEqual(main(args), 1)
            self.assertEqual(
                ["ERROR:bdebstrap:mmdebstrap failed with exit code 42. See above for details."],
                context_manager.output,
            )
        config_save_mock.assert_called_once_with("./foobar/config.yaml", False)
        mmdebstrap_call_mock.assert_called_once_with("./foobar", False)
        prepare_output_dir_mock.assert_called_once_with("./foobar", False, False)

    @unittest.mock.patch("bdebstrap.Config.save")
    @unittest.mock.patch("bdebstrap.prepare_output_dir")
    @unittest.mock.patch("bdebstrap.Mmdebstrap.call")
    def test_empty_target(self, mmdebstrap_call_mock, prepare_output_dir_mock, config_save_mock):
        """Test keeping target empty."""
        with self.assertLogs("bdebstrap", level="INFO"):
            self.assertEqual(main(["--name", "empty-target", "unstable"]), 0)
        config_save_mock.assert_called_once_with("./empty-target/config.yaml", False)
        mmdebstrap_call_mock.assert_called_once_with("./empty-target", False)
        prepare_output_dir_mock.assert_called_once_with("./empty-target", False, False)
