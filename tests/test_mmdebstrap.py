# Copyright (C) 2020 Benjamin Drung <bdrung@posteo.de>
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

import unittest

from bdebstrap import Mmdebstrap


class TestMmdebstrap(unittest.TestCase):
    """
    This unittest class tests the Mmdebstrap object.
    """

    def test_debian_example(self):
        """Test Mmdebstrap with Debian unstable config."""
        mmdebstrap = Mmdebstrap(
            {
                "mmdebstrap": {
                    "architectures": ["i386"],
                    "install-recommends": True,
                    "keyrings": ["/usr/share/keyrings/debian-archive-keyring.gpg"],
                    "mode": "unshare",
                    "suite": "unstable",
                    "target": "example.tar.xz",
                    "variant": "minbase",
                }
            }
        )
        self.assertEqual(
            mmdebstrap.construct_parameters("/output"),
            [
                "mmdebstrap",
                "-v",
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
        mmdebstrap = Mmdebstrap({"mmdebstrap": {"suite": "unstable", "target": "example.tar.xz"}})
        self.assertEqual(
            mmdebstrap.construct_parameters("/output", True),
            [
                "mmdebstrap",
                "-v",
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
            {
                "mmdebstrap": {
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
            }
        )
        self.assertEqual(
            mmdebstrap.construct_parameters("/output"),
            [
                "mmdebstrap",
                "-v",
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
            {
                "mmdebstrap": {
                    "aptopts": ['Acquire::http { Proxy "http://proxy:3128/"; }'],
                    "components": ["main", "non-free", "contrib"],
                    "dpkgopts": ["force-confdef", "force-confold"],
                    "packages": ["bash-completions", "vim"],
                    "suite": "unstable",
                    "target": "example.tar.xz",
                }
            }
        )
        self.assertEqual(
            mmdebstrap.construct_parameters("/output"),
            [
                "mmdebstrap",
                "-v",
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
