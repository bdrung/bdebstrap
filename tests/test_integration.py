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

import os
import shutil
import subprocess
import unittest

from bdebstrap import main

BUILDS_DIR = os.path.join(os.path.dirname(__file__), "builds")
EXAMPLE_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")


@unittest.skipIf(
    not os.environ.get("USE_INTERNET", False),
    "Needs Internet access. Set environment variable USE_INTERNET to run it.",
)
class TestIntegration(unittest.TestCase):
    """
    This unittest class implements integration tests that need Internet connection.
    """

    def tearDown(self):
        shutil.rmtree(BUILDS_DIR)

    @staticmethod
    def test_reproducible():
        """Test building Debian unstable reproducible."""
        config = os.path.join(EXAMPLE_CONFIG_DIR, "Debian-unstable.yaml")
        # Build Debian unstable once.
        main(["-c", config, "-b", BUILDS_DIR, "-n", "unstable"])
        config = os.path.join(BUILDS_DIR, "unstable", "config.yaml")
        # Rebuild Debian unstable again.
        main(["-c", config, "-o", os.path.join(BUILDS_DIR, "unstable-rebuild")])
        subprocess.check_call(
            [
                "diffoscope",
                os.path.join(BUILDS_DIR, "unstable"),
                os.path.join(BUILDS_DIR, "unstable-rebuild"),
            ]
        )
