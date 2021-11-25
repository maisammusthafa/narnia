# narnia

A curses-based console client for aria2 download manager, written in Python.

![screenshot](/screenshot.png?raw=true)

### Prerequisites

[aria2](https://aria2.github.io/) must be installed and configured properly. Refer to aria2's documentation on how to get started.

### Building & Installing

Clone the repo to your local machine and cd into the folder.

```
git clone https://github.com/maisammusthafa/narnia.git
cd narnia
```

Build the client manually. Executable script can be found in `build/scripts-3.x/narnia`.

```
python setup.py build
```

For Arch Linux, a PKGBUILD and Makefile is provided to build and install using the package manager.

```
make install
```

### Configuring

narnia must be configured properly before running. Copy the default [config](https://github.com/maisammusthafa/narnia/blob/narnia2/doc/config/config) and [profiles](https://github.com/maisammusthafa/narnia/blob/narnia2/doc/config/profiles) to `~/.config/narnia/`, and configure accordingly.

### Running

Can be run directly from the executable script, or `narnia` if installed on the system. For available command-line options, run with the help flag.

```
narnia --help
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
