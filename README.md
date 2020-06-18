bdebstrap
=========

bdebstrap is an alternative to debootstrap and a wrapper around
[mmdebstrap](https://gitlab.mister-muffin.de/josch/mmdebstrap/) to support
YAML based configuration files. It inherits all benefits from mmdebstrap. The
support for configuration allows storing all customization in a YAML file
instead of having to use a very long one-liner call to mmdebstrap. It also
layering multiple customizations on top of each other, e.g. to support flavors
of an image.

Usage examples
==============

Minimal Debian unstable tarball
-------------------------------

This example shows how to use a small YAML configuration to build a minimal
Debian unstable tarball. Assume following configuration is stored in
*examples/Debian-unstable.yaml*:

```yaml
mmdebstrap:
  architectures:
  - amd64
  keyrings:
  - /usr/share/keyrings/debian-archive-keyring.gpg
  mode: unshare
  suite: unstable
  target: root.tar.xz
  variant: minbase
```

Then the tarball can be generated by running

```sh
$ bdebstrap -c examples/Debian-unstable.yaml --name example1
$ ls example1/
config.yaml  manifest  root.tar.xz
```

Debian live system
------------------

This example shows how to use a YAML configuration to build a Debian 10
(buster) live system. Assume following configuration is stored in
*examples/Debian-buster-live.yaml*:

```yaml
mmdebstrap:
  architectures:
  - amd64
  cleanup-hooks:
  - cp /dev/null "$1/etc/hostname"
  - if test -f "$1/etc/resolv.conf"; then cp /dev/null "$1/etc/resolv.conf"; fi
  customize-hooks:
  - cp --preserve=timestamps -v "$1"/boot/vmlinuz* "$1${BDEBSTRAP_OUTPUT_DIR?}/vmlinuz"
  - cp --preserve=timestamps -v "$1"/boot/initrd.img* "$1${BDEBSTRAP_OUTPUT_DIR?}/initrd.img"
  - mkdir -p "$1/root/.ssh"
  - upload ~/.ssh/id_rsa.pub /root/.ssh/authorized_keys
  # Create a proper root password entry with "openssl passwd -6 $password"
  - chroot "$1" usermod -p '$6$gxPiEmowud.yY/mT$SE1TTiHkw9mW3YtECxyluZtNPHN7IYPa.vRlWZZVtC8L6qG2PzGpwGIlgMDY79vucWD577fZm/EcA4LS3Koob0' root
  keyrings:
  - /usr/share/keyrings/debian-archive-keyring.gpg
  mode: unshare
  packages:
  - iproute2
  - less
  - libpam-systemd # recommended by systemd and needed to not run into https://bugs.debian.org/751636
  - linux-image-cloud-amd64
  - live-boot
  - locales
  - openssh-server
  - systemd-sysv # Use systemd as init system (otherwise /sbin/init would be missing)
  suite: buster
  target: root.squashfs
  variant: minbase
```

This example assumes that *~/.ssh/id_rsa.pub* exists, because it will be
copied into the image to */root/.ssh/authorized_keys* to allow SSH access
using the user's SSH key.

The squashfs image can be generated by running

```sh
$ bdebstrap -c examples/Debian-buster-live.yaml --name example2
$ ls example2/
config.yaml  initrd.img  manifest  root.squashfs  vmlinuz
```

The kernel and initrd are copied out of the squashfs image using customize
hooks to allow them to be used directly by QEMU. To launch this image locally
with QEMU, the *root.squashfs* image needs to be provided by a HTTP server:

```sh
$ python3 -m http.server -b localhost --directory example2 8080
```

This command exposes the generated image via HTTP on localhost on port 8080.
QEMU can be started passing the TCP traffic on port 8080 to the webserver:

```sh
$ cd example2
$ qemu-system-x86_64 -machine accel=kvm -m 1G -device virtio-net-pci,netdev=net0 -monitor vc \
    -netdev user,id=net0,hostfwd=tcp::2222-:22,guestfwd=tcp:10.0.2.252:8080-tcp:localhost:8080,hostname=debian-live \
    -kernel ./vmlinuz -initrd ./initrd.img -append "boot=live fetch=http://10.0.2.252:8080/root.squashfs quiet"
```

To print the output on the launching terminal, add *-nographic -serial stdio*
to the QEMU command line and *console=ttyS0* to the *-append* parameter. Once
the virtual machine is started, it can be accessed via SSH:

```sh
$ ssh -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no -p 2222 root@localhost
```

Prerequisites
=============

* Python >= 3
* Python modules:
  * ruamel.yaml
* mmdebstrap (>= 0.6.0)
* pandoc (to generate the man page)
* squashfs-tools-ng (>= 0.8) for building squashfs images. Older versions of
  squashfs-tools-ng throw errors
  ([bug #31](https://github.com/AgentD/squashfs-tools-ng/issues/31)) and loose
  the security capabilities
  ([bug #32](https://github.com/AgentD/squashfs-tools-ng/issues/32)).


The test cases have additional Python module requirements:

* flake8
* pylint

Thanks
======

I like to thank Johannes Schauer for developing
[mmdebstrap](https://gitlab.mister-muffin.de/josch/mmdebstrap/) and for quickly
responding to all my bug reports and feature requests.

Contributing
============

Contributions are welcome. The source code has some test coverage, which should
be preserved. So please provide a test case for each bugfix and one or more
test cases for each new feature. Please follow
[How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)
for writing good commit messages.

Creating releases
=================

To create a release, increase the version in `setup.py`, document the
noteworthy changes in `NEWS`, and commit the change. Tag the release:

```
git tag v$(./setup.py --version)
```

The xz-compressed release tarball can be generated by running:
```
name="bdebstrap-$(./setup.py --version)"
git archive --prefix="$name/" HEAD | xz -c9 > "../$name.tar.xz"
gpg --output "../$name.tar.xz.asc" --armor --detach-sign "../$name.tar.xz"
```