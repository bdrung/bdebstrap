#!/usr/bin/python3

# Copyright (C) 2019-2022, Benjamin Drung <bdrung@posteo.de>
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

"""Setup for bdebstrap"""

import logging
import os
import subprocess

from setuptools import Command, setup

try:
    from setuptools.command.build import build
except ImportError:
    # Fallback for setuptools < 60 and Python < 3.12
    from distutils.command.build import build  # pylint: disable=deprecated-module

HOOKS = ["hooks/disable-units", "hooks/enable-units"]
MAN_PAGES = ["bdebstrap.1"]


class DocCommand(Command):
    """A custom command to build the documentation using pandoc."""

    description = "run pandoc to generate man pages"
    user_options: list[tuple[str, str, str]] = []

    def initialize_options(self) -> None:
        """Set default values for options."""

    def finalize_options(self) -> None:
        """Post-process options."""

    # pylint: disable-next=no-self-use
    def run(self) -> None:
        """Run pandoc."""
        logger = logging.getLogger(__name__)
        for man_page in MAN_PAGES:
            command = ["pandoc", "-s", "-t", "man", man_page + ".md", "-o", man_page]
            logger.info("running command: %s", " ".join(command))
            subprocess.check_call(command)


class BuildCommand(build):
    """Custom build command (calling doc beforehand)."""

    def run(self) -> None:
        self.run_command("doc")
        super().run()


class CleanCommand(Command):
    """Custom clean command (removing generated man pages)."""

    description = "remove generated man pages"
    user_options = [("all", "a", "remove all build output, not just temporary by-products")]
    boolean_options = ["all"]

    def initialize_options(self) -> None:
        """Set default values for options."""

    def finalize_options(self) -> None:
        """Post-process options."""

    # pylint: disable-next=no-self-use
    def run(self) -> None:
        """Clean build artefacts from doc command."""
        logger = logging.getLogger(__name__)
        for man_page in MAN_PAGES:
            if os.path.exists(man_page):
                logger.info("removing %s", man_page)
                os.remove(man_page)


if __name__ == "__main__":
    with open("README.md", "r", encoding="utf-8") as fh:
        LONG_DESCRIPTION = fh.read()

    setup(
        name="bdebstrap",
        version="0.6.1",
        description="Benjamin's multi-mirror Debian chroot creation tool",
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        author="Benjamin Drung",
        author_email="bdrung@posteo.de",
        url="https://github.com/bdrung/bdebstrap",
        project_urls={"Bug Tracker": "https://github.com/bdrung/bdebstrap/issues"},
        license="ISC",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "License :: OSI Approved :: ISC License (ISCL)",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
        ],
        cmdclass={"doc": DocCommand, "build": BuildCommand, "clean": CleanCommand},
        install_requires=["ruamel.yaml"],
        scripts=["bdebstrap"],
        py_modules=[],
        data_files=[("/usr/share/man/man1", MAN_PAGES), ("/usr/share/bdebstrap/hooks", HOOKS)],
    )
