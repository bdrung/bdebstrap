# Copyright (C) 2019-2021 Benjamin Drung <bdrung@posteo.de>
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

"""Test configuration handling of bdebstrap."""

import logging
import os
import unittest

from bdebstrap import Config, dict_merge, parse_args

EXAMPLE_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
TEST_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "configs")


class TestArguments(unittest.TestCase):
    """
    This unittest class tests the argument parsing.
    """

    def test_debug(self):
        """Test --debug argument parsing."""
        args = parse_args(["--debug"])
        self.assertEqual(args.log_level, logging.DEBUG)

    def test_empty_args(self):
        """Test setting arguments to empty strings."""
        args = parse_args(
            [
                "--aptopt=",
                "--architectures=",
                "--cleanup-hook=",
                "--components=",
                "--config=",
                "--customize-hook=",
                "--dpkgopt=",
                "--essential-hook=",
                "--keyring=",
                "--mirrors=",
                "--packages=",
                "--setup-hook=",
            ]
        )
        self.assertDictContainsSubset(
            {
                "aptopt": [],
                "architectures": [],
                "cleanup_hook": [],
                "components": [],
                "config": [],
                "customize_hook": [],
                "dpkgopt": [],
                "essential_hook": [],
                "keyring": [],
                "mirrors": [],
                "packages": [],
                "setup_hook": [],
            },
            args.__dict__,
        )

    def test_no_args(self):
        """Test calling bdebstrap without arguments."""
        args = parse_args([])
        self.assertEqual(
            args.__dict__,
            {
                "aptopt": None,
                "architectures": None,
                "cleanup_hook": None,
                "components": None,
                "config": [],
                "customize_hook": None,
                "dpkgopt": None,
                "env": {},
                "essential_hook": None,
                "force": False,
                "hostname": None,
                "install_recommends": False,
                "keyring": None,
                "log_level": logging.WARNING,
                "mirrors": [],
                "mode": None,
                "name": None,
                "output_base_dir": ".",
                "output": None,
                "packages": None,
                "setup_hook": None,
                "simulate": False,
                "suite": None,
                "target": None,
                "tmpdir": None,
                "variant": None,
            },
        )

    def test_parse_env(self):
        """Test parsing --env parameters."""
        args = parse_args(["-e", "KEY=VALUE", "--env", "FOO=bar"])
        self.assertEqual(args.env, {"FOO": "bar", "KEY": "VALUE"})

    def test_malformed_env(self):
        """Test malformed --env parameter (missing equal sign)."""
        with self.assertRaises(SystemExit):
            parse_args(["--env", "invalid"])

    def test_mirrors_with_spaces(self):
        """Test --mirrors with leading/trailing spaces."""
        args = parse_args(
            [
                "--mirrors",
                "  deb http://deb.debian.org/debian unstable main\t ,  \t, "
                "deb http://deb.debian.org/debian unstable non-free\t",
                "--mirrors",
                "\tdeb http://deb.debian.org/debian unstable contrib ",
            ]
        )
        self.assertDictContainsSubset(
            {
                "mirrors": [
                    "deb http://deb.debian.org/debian unstable main",
                    "deb http://deb.debian.org/debian unstable non-free",
                    "deb http://deb.debian.org/debian unstable contrib",
                ],
            },
            args.__dict__,
        )

    def test_optional_args(self):
        """Test optional arguments (which also have positional ones)."""
        args = parse_args(
            [
                "--suite",
                "unstable",
                "--target",
                "unstable.tar",
                "--mirrors",
                "deb http://deb.debian.org/debian unstable main,"
                "deb http://deb.debian.org/debian unstable non-free",
                "--mirrors",
                "deb http://deb.debian.org/debian unstable contrib",
            ]
        )
        self.assertDictContainsSubset(
            {
                "mirrors": [
                    "deb http://deb.debian.org/debian unstable main",
                    "deb http://deb.debian.org/debian unstable non-free",
                    "deb http://deb.debian.org/debian unstable contrib",
                ],
                "suite": "unstable",
                "target": "unstable.tar",
            },
            args.__dict__,
        )

    def test_positional_args(self):
        """Test positional arguments (overwriting optional ones)."""
        args = parse_args(
            [
                "--suite",
                "bullseye",
                "--target",
                "bullseye.tar",
                "--mirrors",
                "deb http://deb.debian.org/debian unstable main,"
                "deb http://deb.debian.org/debian unstable non-free",
                "unstable",
                "unstable.tar",
                "deb http://deb.debian.org/debian unstable contrib",
            ]
        )
        self.assertDictContainsSubset(
            {
                "mirrors": [
                    "deb http://deb.debian.org/debian unstable main",
                    "deb http://deb.debian.org/debian unstable non-free",
                    "deb http://deb.debian.org/debian unstable contrib",
                ],
                "suite": "unstable",
                "target": "unstable.tar",
            },
            args.__dict__,
        )

    def test_split(self):
        """Test splitting comma and space separated values."""
        args = parse_args(
            [
                "--packages",
                "distro-info ionit,netconsole",
                "--include",
                "openssh-server,restricted-ssh-commands",
                "--components",
                "main,non-free contrib",
                "--architectures",
                "amd64,i386",
            ]
        )
        self.assertEqual(
            {
                k: v
                for k, v in args.__dict__.items()
                if k in {"architectures", "components", "packages"}
            },
            {
                "architectures": ["amd64", "i386"],
                "components": ["main", "non-free", "contrib"],
                "packages": [
                    "distro-info",
                    "ionit",
                    "netconsole",
                    "openssh-server",
                    "restricted-ssh-commands",
                ],
            },
        )


class TestConfig(unittest.TestCase):
    """
    This unittest class tests the Config object.
    """

    maxDiff = None

    def test_add_command_line_arguments(self):
        """Test Config.add_command_line_arguments()."""
        args = parse_args(
            [
                "-c",
                os.path.join(EXAMPLE_CONFIG_DIR, "Debian-unstable.yaml"),
                "--name",
                "Debian-unstable",
            ]
        )
        config = Config()
        config.add_command_line_arguments(args)
        self.assertEqual(
            config,
            {
                "mmdebstrap": {
                    "keyrings": ["/usr/share/keyrings/debian-archive-keyring.gpg"],
                    "mode": "unshare",
                    "suite": "unstable",
                    "target": "root.tar.xz",
                    "variant": "minbase",
                },
                "name": "Debian-unstable",
            },
        )

    def test_config_and_arguments(self):
        """Test Config.add_command_line_arguments() with config file and arguments."""
        args = parse_args(
            [
                "-c",
                os.path.join(EXAMPLE_CONFIG_DIR, "Debian-unstable.yaml"),
                "--name",
                "Debian-unstable",
                "--variant",
                "standard",
                "--mode",
                "root",
                "--aptopt",
                'Apt::Install-Recommends "0"',
                "--keyring",
                "/usr/share/keyrings",
                "--dpkgopt",
                "force-confdef",
                "--dpkgopt",
                "force-confold",
                "--include",
                "ionit,netconsole",
                "--components",
                "main,non-free",
                "--architectures",
                "i386",
                "--mirrors",
                "http://deb.debian.org/debian",
                "unstable",
                "unstable.tar",
            ]
        )
        config = Config()
        config.add_command_line_arguments(args)
        self.assertDictEqual(
            config,
            {
                "mmdebstrap": {
                    "aptopts": ['Apt::Install-Recommends "0"'],
                    "architectures": ["i386"],
                    "components": ["main", "non-free"],
                    "dpkgopts": ["force-confdef", "force-confold"],
                    "keyrings": [
                        "/usr/share/keyrings/debian-archive-keyring.gpg",
                        "/usr/share/keyrings",
                    ],
                    "mirrors": ["http://deb.debian.org/debian"],
                    "mode": "root",
                    "packages": ["ionit", "netconsole"],
                    "suite": "unstable",
                    "target": "unstable.tar",
                    "variant": "standard",
                },
                "name": "Debian-unstable",
            },
        )

    @staticmethod
    def test_check_example():
        """Test example unstable.yaml file."""
        config = Config()
        config.load(os.path.join(EXAMPLE_CONFIG_DIR, "Debian-unstable.yaml"))
        config["name"] = "Debian-unstable"
        config.check()

    @staticmethod
    def test_commented_packages():
        """Test commented-packages.yaml file."""
        config = Config()
        config.load(os.path.join(TEST_CONFIG_DIR, "commented-packages.yaml"))
        config.sanitize_packages()
        config.check()

    def test_env_items(self):
        """Test environment variables for example unstable.yaml."""
        config = Config()
        config.load(os.path.join(EXAMPLE_CONFIG_DIR, "Debian-unstable.yaml"))
        config["name"] = "Debian-unstable"
        self.assertEqual(
            config.env_items(),
            [
                ("BDEBSTRAP_NAME", "Debian-unstable"),
                ("BDEBSTRAP_OUTPUT_DIR", "/tmp/bdebstrap-output"),
            ],
        )

    def test_loading(self):
        """Test loading a YAML configuration file."""
        config = Config()
        config.load(os.path.join(EXAMPLE_CONFIG_DIR, "Debian-unstable.yaml"))
        self.assertEqual(
            config,
            {
                "mmdebstrap": {
                    "keyrings": ["/usr/share/keyrings/debian-archive-keyring.gpg"],
                    "mode": "unshare",
                    "suite": "unstable",
                    "target": "root.tar.xz",
                    "variant": "minbase",
                }
            },
        )

    def test_source_date_epoch(self):
        """Test getting and setting SOURCE_DATE_EPOCH."""
        config = Config()
        self.assertIsNone(config.source_date_epoch)
        with unittest.mock.patch("time.time", return_value=1581694618.0388665):
            config.set_source_date_epoch()
        self.assertEqual(config.source_date_epoch, 1581694618)

    def test_wrong_element_type(self):
        """Test error message for wrong list element type."""
        config = Config()
        config.load(os.path.join(TEST_CONFIG_DIR, "wrong-element-type.yaml"))
        with self.assertRaisesRegex(ValueError, "'customize-hooks' has type 'CommentedMap'"):
            config.check()


class TestDictMerge(unittest.TestCase):
    """Unittests for dict_merge function."""

    def test_merge_lists(self):
        """Test merging nested dicts."""
        items = {"A": ["A1", "A2", "A3"], "C": 4}
        dict_merge(items, {"A": ["A4", "A5"]})
        self.assertEqual(items, {"A": ["A1", "A2", "A3", "A4", "A5"], "C": 4})

    def test_merge_nested_dicts(self):
        """Test merging nested dicts."""
        items = {"A": {"A1": 0, "A4": 4}, "C": 4}
        dict_merge(items, {"A": {"A1": 1, "A5": 5}})
        self.assertEqual(items, {"A": {"A1": 1, "A4": 4, "A5": 5}, "C": 4})
