# Copyright (C) 2020-2021 Benjamin Drung <bdrung@posteo.de>
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

"""Test helper functions of bdebstrap."""

import os
import tempfile
import unittest
import unittest.mock

from bdebstrap import clamp_mtime, duration_str, escape_cmd, prepare_output_dir


class TestClampMtime(unittest.TestCase):
    """
    This unittest class tests the clamp_mtime function.
    """

    @staticmethod
    @unittest.mock.patch("os.stat")
    @unittest.mock.patch("os.utime")
    def test_clamp(utime_mock, stat_mock):
        """Test clamping the modification time."""
        stat_mock.return_value = os.stat_result(
            (33261, 16535979, 64769, 1, 1000, 1000, 17081, 1581451059, 1581451059, 1581451059)
        )
        clamp_mtime("/example", 1581433737)
        utime_mock.assert_called_once_with("/example", (1581433737, 1581433737))

    @staticmethod
    @unittest.mock.patch("os.stat")
    @unittest.mock.patch("os.utime")
    def test_not_clamping(utime_mock, stat_mock):
        """Test not clamping the modification time."""
        stat_mock.return_value = os.stat_result(
            (33261, 16535979, 64769, 1, 1000, 1000, 17081, 1581451059, 1581451059, 1581451059)
        )
        clamp_mtime("/example", 1581506399)
        utime_mock.assert_not_called()

    @staticmethod
    @unittest.mock.patch("os.stat")
    def test_no_source_date_epoch(stat_mock):
        """Test doing nothing if SOURCE_DATE_EPOCH is not set."""
        clamp_mtime("/example", None)
        stat_mock.assert_not_called()


class TestDuration(unittest.TestCase):
    """
    This unittest class tests the duration_str function.
    """

    def test_seconds(self):
        """Test calling duration_str(3.606104612350464)."""
        self.assertEqual(duration_str(3.606104612350464), "3.606 seconds")

    def test_minutes(self):
        """Test calling duration_str(421.88086652755737)."""
        self.assertEqual(duration_str(421.88086652755737), "7 min 1.881 s (= 421.881 s)")

    def test_hours(self):
        """Test calling duration_str(7397.447488069534)."""
        self.assertEqual(duration_str(7397.447488069534), "2 h 3 min 17.447 s (= 7397.447 s)")


class TestEscapeCmd(unittest.TestCase):
    """
    This unittest class tests the escape_cmd function.
    """

    def test_simple(self):
        """Test calling escape_cmd(["free"])."""
        self.assertEqual(escape_cmd(["free"]), "free")

    def test_spaces(self):
        """Test calling escape_cmd(["scp", "source", "a space"])."""
        self.assertEqual(escape_cmd(["scp", "source", "a space"]), 'scp source "a space"')

    def test_escape(self):
        """Test calling escape_cmd(["dpkg-query", r"-f=${Package}\t${Version}\n", "-W"])."""
        self.assertEqual(
            escape_cmd(["dpkg-query", r"-f=${Package}\t${Version}\n", "-W"]),
            r'dpkg-query "-f=\${Package}\t\${Version}\n" -W',
        )

    def test_customize_hook(self):
        """Test calling escape_cmd on mmdebstrap customize hook."""
        self.assertEqual(
            escape_cmd(
                [
                    "mmdebstrap",
                    '--customize-hook=chroot "$1" dpkg-query '
                    "-f='${Package}\\t${Version}\\n' -W > \"$1/tmp/bdebstrap/manifest\"",
                ]
            ),
            r'mmdebstrap "--customize-hook=chroot \"\$1\" dpkg-query '
            r"-f='${Package}\t${Version}\n' -W "
            r'> \"\$1/tmp/bdebstrap/manifest\""',
        )


class TestPrepareOutputDir(unittest.TestCase):
    """
    This unittest class tests the prepare_output_dir function.
    """

    TMP_PREFIX = "bdebstrap-"

    def test_dry_run(self):
        """Test that dry run does not create the directory."""
        with tempfile.TemporaryDirectory(prefix=self.TMP_PREFIX) as tmpdir:
            output_dir = os.path.join(tmpdir, "unstable")
            self.assertTrue(prepare_output_dir(output_dir, False, simulate=True))
            self.assertFalse(os.path.isdir(output_dir))

    def test_force(self):
        """Test replacing an existing output directory."""
        with tempfile.TemporaryDirectory(prefix=self.TMP_PREFIX) as tmpdir:
            output_dir = os.path.join(tmpdir, "unstable")
            os.makedirs(output_dir)
            os.mknod(os.path.join(output_dir, "root.tar"))

            self.assertTrue(prepare_output_dir(output_dir, True))
            self.assertTrue(os.path.isdir(output_dir))
            self.assertEqual(os.listdir(output_dir), [])

    def test_existing(self):
        """Test failure when output directory already exists."""
        with tempfile.TemporaryDirectory(prefix=self.TMP_PREFIX) as tmpdir:
            output_dir = os.path.join(tmpdir, "unstable")
            os.makedirs(output_dir)
            os.mknod(os.path.join(output_dir, "root.tar"))

            with self.assertLogs("bdebstrap", level="ERROR") as context_manager:
                self.assertFalse(prepare_output_dir(output_dir, False))
            self.assertIn("already exists and is not empty", context_manager.output[-1])
            self.assertTrue(os.path.isdir(output_dir))
            self.assertEqual(os.listdir(output_dir), ["root.tar"])

    def test_missing_output_dir(self):
        """Test creating the missing output directory."""
        with tempfile.TemporaryDirectory(prefix=self.TMP_PREFIX) as tmpdir:
            output_dir = os.path.join(tmpdir, "unstable")
            self.assertTrue(prepare_output_dir(output_dir, False))
            self.assertTrue(os.path.isdir(output_dir))
