# A union Filesystem in Userspace

[![build badge](https://github.com/theobori/unionfs/actions/workflows/build.yml/badge.svg)](https://github.com/theobori/unionfs/actions/workflows/build.yml)

[![built with nix](https://builtwithnix.org/badge.svg)](https://builtwithnix.org)

This GitHub repository is a [KISS](https://en.wikipedia.org/wiki/KISS_principle) project that contains Python project containing a library and a CLI. The library provides Python code that communicates with [FUSE](https://www.kernel.org/doc/html/next/filesystems/fuse.html) to export a file system to the Linux kernel, a server to manage the global mount table in memory, and functions to communicate with that server. The CLI is a Python application that allows you to manage the mount points of the virtual file system and manipulate the global mount table.

The file system operations are inspired by https://1e.iwp9.org/cready/unfs.pdf.

## How it works

Below are the main components of the project.

### Mount Table

The mount table is a Python object that manages a hash map, where each key is a path corresponding to a mount point, and each value is a custom data structure designed to manage the mounted directories. It has a time complexity of O(1) for each required operation.

### Daemon

This is a server that must be started before mounting the filesystem. It is responsible for managing the global mount table in memory and handling mount and bind requests.

### Mount Points

These export the filesystem to Linux using FUSE. While running, they communicate with the daemon to update their bound directories.

## Project Progress

The project is not entirely finished; there are still areas for improvement to explore and tasks to complete. However, it remains functional.

## Contribute

If you'd like to contribute to the project, please follow the instructions provided in the [CONTRIBUTING.md](./CONTRIBUTING.md) file.
