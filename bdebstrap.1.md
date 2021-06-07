---
date: 2020-05-26
footer: bdebstrap
header: "bdebstrap's Manual"
layout: page
license: 'Licensed under the ISC license'
section: 1
title: BDEBSTRAP
---

# NAME

bdebstrap - YAML config based multi-mirror Debian chroot creation tool

# SYNOPSIS

**bdebstrap** [**-h**|**\--help**] [**-c**|**\--config** *CONFIG*]
[**-n**|**\--name** *NAME*] [**-e**|**\--env** *ENV*]
[**-s**|**\--simulate**|**\--dry-run**]
[**-b**|**\--output-base-dir** *OUTPUT_BASE_DIR*]
[**-o**|**\--output** *OUTPUT*]
[**-q**|**\--quiet**|**\--silent**|**-v**|**\--verbose**|**\--debug**]
[**-f**|**\--force**] [**-t**|**\--tmpdir** *TMPDIR*]
[**\--variant** {*extract*,*custom*,*essential*,*apt*,*required*,*minbase*,*buildd*,*important*,*debootstrap*,*-*,*standard*}]
[**\--mode** {*auto*,*sudo*,*root*,*unshare*,*fakeroot*,*fakechroot*,*proot*,*chrootless*}]
[**\--aptopt** *APTOPT*] [**\--keyring** *KEYRING*] [**\--dpkgopt** *DPKGOPT*]
[**\--hostname** *HOSTNAME*] [**\--install-recommends**]
[**\--packages**|**\--include** *PACKAGES*] [**\--components** *COMPONENTS*]
[**\--architectures** *ARCHITECTURES*]
[**\--setup-hook** *COMMAND*] [**\--essential-hook** *COMMAND*]
[**\--customize-hook** *COMMAND*] [**\--cleanup-hook** *COMMAND*]
[**\--suite** *SUITE*] [**\--target** *TARGET*] [**\--mirrors** *MIRRORS*]
[*SUITE* [*TARGET* [*MIRROR*...]]]

# DESCRIPTION

**bdebstrap** creates a Debian chroot of *SUITE* into *TARGET* from one or more
*MIRROR*s and places meta-data in the *OUTPUT* directory: A *config.yaml*
containing the configuration for the build (useful for rebuilds) and a
*manifest* listing all installed packages and versions. If *TARGET* is just a
filename (and not include the path), it will be placed in the *OUTPUT*
directory as well. **bdebstrap** extents mmdebtrap to make it configurable via
YAML configuration files for more complex builds.

The configuration parameters can be passed to **bdebstrap** as command line
arguments or in one or more configuration YAML files. The content of YAML files
will be merged by appending lists and recursively merging maps. Arguments
specified on the command line will take precedence over values provided in the
YAML configuration file. The final merged parameters will be stored in the
output directory as *config.yaml*.

# OPTIONS

**-h**, **\--help**
:   Show a help message and exit

**-c** *CONFIG*, **\--config** *CONFIG*
:   Configuration YAML file. See YAML CONFIGURATION below for the expected
    structure of this file. This parameter can be specified multiple times. The
    content of YAML files will be merged by appending lists and recursively
    merging maps.

**-n** *NAME*, **\--name** *NAME*
:   name of the generated golden image. If no output directory is specified,
    the golden image will be placed in *OUTPUT_BASE_DIR*/*NAME*.

**-e** *ENV*, **\--env** *ENV*
:   Add an additional environment variable. These environment variable will be
    set when calling the hooks.

**-s**, **\--simulate**, **\--dry-run**
:   Run apt-get with **\--simulate**. Only the package cache is initialized
    but no binary packages are downloaded or installed. Use this option to
    quickly check whether a package selection within a certain suite and
    variant can in principle be installed as far as their dependencies go. If
    the output is a tarball, then no output is produced. If the output is a
    directory, then the directory will be left populated with the skeleton
    files and directories necessary for apt to run in it.

**-b** *OUTPUT_BASE_DIR*, **\--output-base-dir** *OUTPUT_BASE_DIR*
:   output base directory. By default it is the current directory.

**-o** *OUTPUT*, **\--output** *OUTPUT*
:   output directory (default: output-base-dir/name)

**-q**, **\--quiet**, **\--silent**
:   Do not write anything to standard error except errors. If used together
    with **\--verbose** or **\--debug**, only the last option will take effect.

**-v**, **\--verbose**
:   Write informational messages (about configuration files, environment
    variables, mmdebstrap call, etc.) to standard error. Instead of progress
    bars, **mmdebstrap** writes the dpkg and apt output directly to standard
    error. If used together with **\--quiet** or **\--debug**, only the last
    option will take effect.

**\--debug**
:   In addition to the output produced by **\--verbose**, write detailed
    debugging information to standard error. Errors of **mmdebstrap** will
    print a backtrace. If used together with **\--quiet** or **\--verbose**,
    only the last option will take effect.

**-f**, **\--force**
:   Remove existing output directory before creating a new one

**-t** *TMPDIR*, **\--tmpdir** *TMPDIR*
:   Temporary directory for building the image (default: /tmp)

**\--variant** {*extract*,*custom*,*essential*,*apt*,*required*,*minbase*,*buildd*,*important*,*debootstrap*,*-*,*standard*}
:   Choose which package set to install.

**\--mode** {*auto*,*sudo*,*root*,*unshare*,*fakeroot*,*fakechroot*,*proot*,*chrootless*}
:   Choose how to perform the chroot operation and create a filesystem with
    ownership information different from the current user.

**\--aptopt** *APTOPT*
:   Pass arbitrary options or configuration files to apt.

**\--keyring** *KEYRING*
:   Change the default keyring to use by apt.

**\--dpkgopt** *DPKGOPT*
:   Pass arbitrary options or configuration files to dpkg.

**\--hostname** *HOSTNAME*
:   Write the given *HOSTNAME* into */etc/hostname* in the target chroot.

**\--install-recommends**
:   Consider recommended packages as a dependency for installing.

**\--packages** *PACKAGES*, **\--include** *PACKAGES*
:   Comma or whitespace separated list of packages which will be installed in
    addition to the packages installed by the specified variant.

**\--components** *COMPONENTS*
:   Comma or whitespace separated list of components like main, contrib and
    non-free which will be used for all URI-only *MIRROR* arguments.

**\--architectures** *ARCHITECTURES*
:   Comma or whitespace separated list of architectures. The first
    architecture is the native architecture inside the chroot.

**\--setup-hook** *COMMAND*
:   Execute arbitrary *COMMAND* right after initial setup (directory creation,
    configuration of apt and dpkg, ...) but before any packages are downloaded
    or installed. At that point, the chroot directory does not contain any
    executables and thus cannot be chroot-ed into. This option can be specified
    multiple times.

**\--essential-hook** *COMMAND*
:   Execute arbitrary *COMMAND* after the Essential:yes packages have been
    installed, but before installing the remaining packages. This option can be
    specified multiple times.

**\--customize-hook** *COMMAND*
:   Execute arbitrary *COMMAND* after the chroot is set up and all packages got
    installed but before final cleanup actions are carried out. This option can
    be specified multiple times.

**\--cleanup-hook** *COMMAND*
:   Execute arbitrary *COMMAND* after all customize hooks have been executed.
    This option can be specified multiple times.

**\--suite** *SUITE*, *SUITE*
:   The suite may be a valid release code name (eg, sid, stretch, jessie) or
    a symbolic name (eg, unstable, testing, stable, oldstable).

**\--target** *TARGET*, *TARGET*
:   The optional target argument can either be the path to a directory, the
    path to a tarball filename, the path to a squashfs image or *-*.

**\--mirrors** *MIRRORS*, *MIRRORS*
:   Comma separated list of mirrors. If no mirror option is provided,
    http://deb.debian.org/debian is used.

# YAML CONFIGURATION

This section describes the expected data-structure hierarchy of the YAML
configuration file(s). The top-level structure is expected to be a mapping.
The top-level mapping may contain following keys:

### env

mapping of environment variables names to their values. Environment variables
can be overridden by specifying them with **\--env** using the same name. These
environment variable are set before calling the hooks.

### name

String. Name of the generated golden image. Can be overridden by **\--name**.

### mmdebstrap

mapping. The values here are passed to mmdebstrap(1). Following keys might
be specified:

**aptopts**
:   list of arbitrary options or configuration files (string) to apt.
    Additional apt options can be specified with **\--aptopt**.

**architectures**
:   list of architectures (string). The first architecture is the native
    architecture inside the chroot. Additional architectures can be specified
    with **\--architectures**.

**components**
:   list of components (string) like main, contrib and non-free which will be
    used for all URI-only *MIRROR* arguments. Additional components can be
    specified with **\--components**.

**dpkgopts**
:   list of arbitrary options or configuration files (string) to dpkg.
    Additional dpkg options can be specified with **\--dpkgopt**.

**hostname**
:   String. If specified, write the given *hostname* into */etc/hostname* in
    the target chroot. This parameter does not exist in **mmdebstrap** and is
    implemented as customize hook for **mmdebstrap**. Can be overridden by
    **\--hostname**.

**install-recommends**
:   Boolean. If set to *True*, the APT option *Apt::Install-Recommends "true"*
    is passed to **mmdebstrap** via **\--aptopt**. Can be overridden by
    **\--install-recommends**.

**keyrings**
:   list of default keyring to use by apt. Additional keyring files can be
    specified with **\--keyring**.

**mirrors**
:   list of mirrors (string). Additional mirrors can be specified with
    **\--mirrors**.

**mode**
:   Choose how to perform the chroot operation and create a filesystem with
    ownership information different from the current user. It needs to be one
    of *auto*, *sudo*, *root*, *unshare*, *fakeroot*, *fakechroot*, *proot*, or
    *chrootless*. See mmdebstrap(1) for details. Can be overridden by
    **\--mode**.

**packages**
:   list of packages (string) which will be installed in addition to the
    packages installed by the specified variant. Additional packages can be
    specified with **\--packages** or **\--include**. This setting is passed to
    **mmdebstrap** using the **\--include** parameter.

**setup-hooks**
:   list of setup hooks (string). Execute arbitrary commands right after
    initial setup (directory creation, configuration of apt and dpkg, ...) but
    before any packages are downloaded or installed. At that point, the chroot
    directory does not contain any executables and thus cannot be chroot-ed
    into. See **HOOKS** in mmdebstrap(1) for more information and examples.
    Additional setup hooks can be specified with **\--setup-hook**.

**essential-hooks**
:   list of essential hooks (string). Execute arbitrary commands after the
    Essential:yes packages have been installed, but before installing the
    remaining packages. See **HOOKS** in mmdebstrap(1) for more information and
    examples. Additional essential hooks can be specified with
    **\--essential-hook**.

**customize-hooks**
:   list of customize hooks (string). Execute arbitrary commands after the
    chroot is set up and all packages got installed but before final cleanup
    actions are carried out. See **HOOKS** in mmdebstrap(1) for more
    information and examples. Additional customize hooks can be specified with
    **\--customize-hook**.

**cleanup-hooks**
:   list of cleanup hooks (string). Cleanup hooks are just hooks that are run
    directly after all other customize hooks. See **customize-hooks** above.
    Additional cleanup hooks can be specified with **\--cleanup-hook**.

**suite**
:   String. The suite may be a valid release code name (eg, sid, stretch,
    jessie) or a symbolic name (eg, unstable, testing, stable, oldstable). Can
    be overridden by **\--suite**.

**target**
:   String. The target argument can either be the path to a directory, the path
    to a tarball filename, the path to a squashfs image or *-*. Can be
    overridden by **\--target**.

**variant**
:   Choose which package set to install. It needs to be one of *extract*,
    *custom*, *essential*, *apt*, *required*, *minbase*, *buildd*, *important*,
    *debootstrap*, *-*, *standard*. See mmdebstrap(1) for details. Can be
    overridden by **\--variant**.

# HOOKS

**bdebstrap** enhances the hooks provided by **mmdebstrap**. Hooks can use the
environment variables specified via the *env* configuration option or the
**\--env** parameter. **bdebstrap** sets following environment variables by
default to be consumed by the hooks:

**BDEBSTRAP_NAME**
:   name of the generated golden image which is set via the **name**
    configuration option of the **\--name** parameter.

**BDEBSTRAP_OUTPUT_DIR**
:   Path of a temporary directory inside the chroot. Files and directories
    that are placed inside this directory will be copied out of the image into
    the output directory. This temporary directory will be removed in a final
    cleanup hook.

# EXAMPLES

### Minimal Debian unstable tarball

This example shows how to use a small YAML configuration to build a minimal
Debian unstable tarball. Assume following configuration is stored in
*unstable.yaml*:

```yaml
mmdebstrap:
  keyrings:
  - /usr/share/keyrings/debian-archive-keyring.gpg
  mode: unshare
  suite: unstable
  target: root.tar.xz
  variant: minbase
```

Then the tarball can be generated by running

```
$ bdebstrap -c unstable.yaml --name example1
$ ls example1/
config.yaml  manifest  root.tar.xz
```

### Debian live system

This example shows how to use a YAML configuration to build a Debian 11
(bullseye) live system. Assume following configuration is stored in *live.yaml*:

```yaml
mmdebstrap:
  architectures:
  - amd64
  cleanup-hooks:
  - cp /dev/null "$1/etc/hostname"
  - if test -f "$1/etc/resolv.conf"; then cp /dev/null "$1/etc/resolv.conf"; fi
  customize-hooks:
  - cp --preserve=timestamps -v "$1"/boot/vmlinu* "$1${BDEBSTRAP_OUTPUT_DIR?}/vmlinuz"
  - cp --preserve=timestamps -v "$1"/boot/initrd.img* "$1${BDEBSTRAP_OUTPUT_DIR?}/initrd.img"
  - mkdir -p "$1/root/.ssh"
  - upload ~/.ssh/id_rsa.pub /root/.ssh/authorized_keys
  keyrings:
  - /usr/share/keyrings/debian-archive-keyring.gpg
  mode: unshare
  packages:
  - init
  - iproute2
  - less
  - libpam-systemd
  - linux-image-cloud-amd64
  - live-boot
  - locales
  - openssh-server
  suite: bullseye
  target: root.squashfs
  variant: minbase
```

This example assumes that *~/.ssh/id_rsa.pub* exists, because it will be
copied into the image to */root/.ssh/authorized_keys* to allow SSH access
using the user's SSH key.

The squashfs image can be generated by running

```
$ bdebstrap -c live.yaml --name example2
$ ls example2/
config.yaml  initrd.img  manifest  root.squashfs  vmlinuz
```

The kernel and initrd are copied out of the squashfs image using customize
hooks to allow them to be used directly by QEMU. To launch this image locally
with QEMU, the *root.squashfs* image needs to be provided by a HTTP server:

```
$ python3 -m http.server -b localhost --directory example2 8080
```

This command exposes the generated image via HTTP on localhost on port 8080.
QEMU can be started passing the TCP traffic on port 8080 to the webserver:

```
$ cd example2
$ qemu-system-x86_64 -machine accel=kvm -m 1G -device virtio-net-pci,netdev=net0 -monitor vc \
    -netdev user,id=net0,hostfwd=tcp::2222-:22,guestfwd=tcp:10.0.2.252:8080-tcp:localhost:8080,hostname=debian-live \
    -kernel ./vmlinuz -initrd ./initrd.img -append "boot=live fetch=http://10.0.2.252:8080/root.squashfs quiet"
```

To print the output on the launching terminal, add *-nographic -serial stdio*
to the QEMU command line and *console=ttyS0* to the *-append* parameter. Once
the virtual machine is started, it can be accessed via SSH:

```
$ ssh -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no -p 2222 root@localhost
```

# SEE ALSO

mmdebstrap(1), debootstrap(8)

# AUTHOR

Benjamin Drung <bdrung@posteo.de>
