# Copyright (C) 2020-2022 Benjamin Drung <bdrung@posteo.de>
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

"""Test Mmdebstrap class of bdebstrap."""

import logging
import os
import unittest
import unittest.mock

from bdebstrap import Config, Mmdebstrap, __script_name__


class TestMmdebstrap(unittest.TestCase):
    """
    This unittest class tests the Mmdebstrap object.
    """

    maxDiff = None

    def setUp(self):
        logging.getLogger(__script_name__).setLevel(logging.WARNING)

    def test_debian_example(self):
        """Test Mmdebstrap with Debian unstable config."""
        mmdebstrap = Mmdebstrap(
            Config(
                mmdebstrap={
                    "architectures": ["i386"],
                    "install-recommends": True,
                    "keyrings": ["/usr/share/keyrings/debian-archive-keyring.gpg"],
                    "mode": "unshare",
                    "suite": "unstable",
                    "target": "example.tar.xz",
                    "variant": "minbase",
                }
            )
        )
        self.assertEqual(
            mmdebstrap.construct_parameters("/output"),
            [
                "mmdebstrap",
                "--variant=minbase",
                "--mode=unshare",
                "--keyring=/usr/share/keyrings/debian-archive-keyring.gpg",
                "--architectures=i386",
                '--essential-hook=mkdir -p "$1/tmp/bdebstrap-output"',
                '--aptopt=Apt::Install-Recommends "true"',
                "--customize-hook=chroot \"$1\" dpkg-query -f='${Package}\\t${Version}\\n' -W "
                '> "$1/tmp/bdebstrap-output/manifest"',
                '--customize-hook=sync-out "/tmp/bdebstrap-output" "/output"',
                '--customize-hook=rm -rf "$1/tmp/bdebstrap-output"',
                "unstable",
                "example.tar.xz",
            ],
        )

    def test_dry_run(self):
        """Test Mmdebstrap with dry run set."""
        mmdebstrap = Mmdebstrap(
            Config(mmdebstrap={"suite": "unstable", "target": "example.tar.xz"})
        )
        self.assertEqual(
            mmdebstrap.construct_parameters("/output", True),
            [
                "mmdebstrap",
                "--simulate",
                '--essential-hook=mkdir -p "$1/tmp/bdebstrap-output"',
                "--customize-hook=chroot \"$1\" dpkg-query -f='${Package}\\t${Version}\\n' -W "
                '> "$1/tmp/bdebstrap-output/manifest"',
                '--customize-hook=sync-out "/tmp/bdebstrap-output" "/output"',
                '--customize-hook=rm -rf "$1/tmp/bdebstrap-output"',
                "unstable",
                "example.tar.xz",
            ],
        )

    def test_hooks(self):
        """Test Mmdebstrap with custom hooks."""
        mmdebstrap = Mmdebstrap(
            Config(
                mmdebstrap={
                    "cleanup-hooks": ['rm -f "$0/etc/udev/rules.d/70-persistent-net.rules"'],
                    "customize-hooks": [
                        'chroot "$0" update-alternatives --set editor /usr/bin/vim.basic'
                    ],
                    "essential-hooks": ["copy-in /etc/bash.bashrc /etc"],
                    "hostname": "example",
                    "setup-hooks": [],
                    "suite": "buster",
                    "target": "buster.tar.xz",
                }
            )
        )
        self.assertEqual(
            mmdebstrap.construct_parameters("/output"),
            [
                "mmdebstrap",
                '--essential-hook=mkdir -p "$1/tmp/bdebstrap-output"',
                "--essential-hook=copy-in /etc/bash.bashrc /etc",
                '--customize-hook=chroot "$0" update-alternatives --set editor /usr/bin/vim.basic',
                '--customize-hook=rm -f "$0/etc/udev/rules.d/70-persistent-net.rules"',
                '--customize-hook=echo "example" > "$1/etc/hostname"',
                "--customize-hook=chroot \"$1\" dpkg-query -f='${Package}\\t${Version}\\n' -W "
                '> "$1/tmp/bdebstrap-output/manifest"',
                '--customize-hook=sync-out "/tmp/bdebstrap-output" "/output"',
                '--customize-hook=rm -rf "$1/tmp/bdebstrap-output"',
                "buster",
                "buster.tar.xz",
            ],
        )

    def test_extra_opts(self):
        """Test Mmdebstrap with extra options."""
        mmdebstrap = Mmdebstrap(
            Config(
                mmdebstrap={
                    "aptopts": ['Acquire::http { Proxy "http://proxy:3128/"; }'],
                    "components": ["main", "non-free", "contrib"],
                    "dpkgopts": ["force-confdef", "force-confold"],
                    "format": "tar",
                    "packages": ["bash-completions", "vim"],
                    "suite": "unstable",
                    "target": "example.tar.xz",
                }
            )
        )
        self.assertEqual(
            mmdebstrap.construct_parameters("/output"),
            [
                "mmdebstrap",
                "--format=tar",
                '--aptopt=Acquire::http { Proxy "http://proxy:3128/"; }',
                "--dpkgopt=force-confdef",
                "--dpkgopt=force-confold",
                "--include=bash-completions,vim",
                "--components=main,non-free,contrib",
                '--essential-hook=mkdir -p "$1/tmp/bdebstrap-output"',
                "--customize-hook=chroot \"$1\" dpkg-query -f='${Package}\\t${Version}\\n' -W "
                '> "$1/tmp/bdebstrap-output/manifest"',
                '--customize-hook=sync-out "/tmp/bdebstrap-output" "/output"',
                '--customize-hook=rm -rf "$1/tmp/bdebstrap-output"',
                "unstable",
                "example.tar.xz",
            ],
        )

    @unittest.mock.patch("os.path.exists", unittest.mock.MagicMock(return_value=True))
    @unittest.mock.patch("os.stat")
    @unittest.mock.patch("os.utime")
    def test_clamp_mtime(self, utime_mock, stat_mock):
        """Test clamping mtime of output files/directories."""
        stat_mock.return_value = os.stat_result(
            (33261, 16535979, 64769, 1, 1000, 1000, 17081, 1581451059, 1581451059, 1581451059)
        )
        config = Config(
            env={"SOURCE_DATE_EPOCH": 1581433737}, mmdebstrap={"target": "/output/test.tar"}
        )
        mmdebstrap = Mmdebstrap(config)
        mmdebstrap.clamp_mtime("/output")
        self.assertEqual(utime_mock.call_count, 3)

    @unittest.mock.patch("os.path.exists", unittest.mock.MagicMock(return_value=True))
    @unittest.mock.patch("os.stat")
    @unittest.mock.patch("os.utime")
    def test_clamp_mtime_permission(self, utime_mock, stat_mock):
        """Test permission error when clamping mtime of output files/directories."""
        stat_mock.return_value = os.stat_result(
            (33261, 16535979, 64769, 1, 1000, 1000, 17081, 1581451059, 1581451059, 1581451059)
        )
        utime_mock.side_effect = PermissionError(1, "Operation not permitted")
        config = Config(
            env={"SOURCE_DATE_EPOCH": 1581433737}, mmdebstrap={"target": "/output/test.tar"}
        )
        mmdebstrap = Mmdebstrap(config)
        with self.assertLogs("bdebstrap", level="ERROR") as context_manager:
            mmdebstrap.clamp_mtime("/output")
            self.assertEqual(utime_mock.call_count, 3)
            self.assertEqual(
                [
                    "ERROR:bdebstrap:Failed to change modification time of '/output/manifest': "
                    "[Errno 1] Operation not permitted",
                    "ERROR:bdebstrap:Failed to change modification time of '/output/test.tar': "
                    "[Errno 1] Operation not permitted",
                    "ERROR:bdebstrap:Failed to change modification time of '/output': "
                    "[Errno 1] Operation not permitted",
                ],
                context_manager.output,
            )

    def test_log_level_debug(self):
        """Test Mmdebstrap with log level debug."""
        logging.getLogger(__script_name__).setLevel(logging.DEBUG)
        mmdebstrap = Mmdebstrap(Config())
        self.assertEqual(
            mmdebstrap.construct_parameters("/output")[0:2], ["mmdebstrap", "--debug"]
        )

    def test_log_level_error(self):
        """Test Mmdebstrap with log level error."""
        logging.getLogger(__script_name__).setLevel(logging.ERROR)
        mmdebstrap = Mmdebstrap(Config())
        self.assertEqual(mmdebstrap.construct_parameters("/output")[0:2], ["mmdebstrap", "-q"])

    def test_log_level_info(self):
        """Test Mmdebstrap with log level info."""
        logging.getLogger(__script_name__).setLevel(logging.INFO)
        mmdebstrap = Mmdebstrap(Config())
        self.assertEqual(mmdebstrap.construct_parameters("/output")[0:2], ["mmdebstrap", "-v"])

    def test_log_level_warning(self):
        """Test Mmdebstrap with log level warning."""
        logging.getLogger(__script_name__).setLevel(logging.WARNING)
        mmdebstrap = Mmdebstrap(Config())
        self.assertEqual(
            mmdebstrap.construct_parameters("/output")[0:2],
            ["mmdebstrap", '--essential-hook=mkdir -p "$1/tmp/bdebstrap-output"'],
        )
