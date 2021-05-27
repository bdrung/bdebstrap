#!/usr/bin/python3

# Copyright (C) 2019-2021, Benjamin Drung <bdrung@posteo.de>
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

import distutils.cmd
import distutils.command.build
import distutils.command.clean
import os
import subprocess

from setuptools import setup

MAN_PAGES = ["bdebstrap.1"]


class DocCommand(distutils.cmd.Command):
    """A custom command to build the documentation using pandoc."""

    description = "run pandoc to generate man pages"
    user_options = []

    def initialize_options(self):
        """Set default values for options."""

    def finalize_options(self):
        """Post-process options."""

    def run(self):
        """Run pandoc."""
        for man_page in MAN_PAGES:
            command = ["pandoc", "-s", "-t", "man", man_page + ".md", "-o", man_page]
            self.announce("running command: %s" % " ".join(command), level=distutils.log.INFO)
            subprocess.check_call(command)


class BuildCommand(distutils.command.build.build):
    """Custom build command (calling doc beforehand)."""

    def run(self):
        self.run_command("doc")
        distutils.command.build.build.run(self)


class CleanCommand(distutils.command.clean.clean):
    """Custom clean command (removing generated man pages)."""

    def run(self):
        for man_page in MAN_PAGES:
            if os.path.exists(man_page):
                self.announce("removing %s" % (man_page), level=distutils.log.INFO)
                os.remove(man_page)
        distutils.command.clean.clean.run(self)


if __name__ == "__main__":
    with open("README.md", "r", encoding="utf-8") as fh:
        LONG_DESCRIPTION = fh.read()

    setup(
        name="bdebstrap",
        version="0.1.2",
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
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
        ],
        cmdclass={"doc": DocCommand, "build": BuildCommand, "clean": CleanCommand},
        install_requires=["ruamel.yaml"],
        scripts=["bdebstrap"],
        py_modules=[],
        data_files=[("/usr/share/man/man1", MAN_PAGES)],
    )
