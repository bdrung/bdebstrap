bdebstrap 0.4.0 (2021-12-10)
============================

* tests: Catch and check output on stderr
* tests: Replace deprecated `assertDictContainsSubset`
* Add `disable-units` and `enable-units` hooks

bdebstrap 0.3.0 (2021-11-08)
============================

* Fix issues found by pylint 2.11.1
  (fixes [Debian bug #998591](https://bugs.debian.org/998591)):
  * tests: Use `with for subprocess.Popen` calls
  * Save YAML configuration files explicitly as UTF-8
  * Replace `.format()` with f-strings
* Make YAML files free of complaints from yamllint
* Produce YAML files that are yamllint clean
* Add example configurations for Raspberry Pis (version 3 and Zero W)
* Set root password for Debian live example to `debian`

bdebstrap 0.2.0 (2021-06-08)
============================

This release changes the default output verbosity to align with mmdebstrap. To
restore the previous default behavior, call bdebstrap with `--verbose`.

* Fix `KeyError: 'target'` if no target was specified
* Fix passing `--target=-` ([Debian bug #989452](https://bugs.debian.org/989452))
* Add `--silent` as alias for `--quiet`
* Align log levels with mmdebstrap ([Debian bug #989450](https://bugs.debian.org/989450)):
  * Change the default log level from info to warning
  * Add a `--verbose` option to change the log level to info again
  * Pass down `--quiet` and `--debug` to mmdebstrap
* Fix `PermissionError` exception when clamping mtime

bdebstrap 0.1.2 (2021-05-27)
============================

* examples: Install init instead of systemd-sysv
* Check import definition order with isort
* Format Python code with black
* Add test case for black code formatter
* Correct license claim from MIT to ISC
* Fix examples for non-amd64 architectures (fixes #2):
  * Drop architectures from minimal examples
  * Drop mirrors from minimal Ubuntu example
  * Match also vmlinux* in Debian live example
* Update Debian live system example to bullseye

bdebstrap 0.1.1 (2020-06-18)
============================

* Strip leading/trailing spaces/tabs from mirrors specified with `--mirrors`
* Fix complaints from flake8 3.8.3
* Check if type of list elements are strings in YAML configuration

bdebstrap 0.1 (2020-06-03)
==========================

* Initial release
