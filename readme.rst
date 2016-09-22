findempty
=========

Python 3 library and CLI utilities for finding, and optionally deleting, empty
filesystem directories.

Copyright (c) 2016 Jim Boswell.  Licensed under the Expat MIT license.  See the
file LICENSE for the full text.

TODO
----

Proper docs!

CLI Usage
---------

usage: findempty [-h] [-c PATH] [-d] [-v] [--debug] [-0] [--no-config]
                 [--no-env] [--show-default-config]
                 [FOLDERS [FOLDERS ...]]

Find empty folders

positional arguments:
  FOLDERS               Root folders to check for emptiness.

optional arguments:
  -h, --help            show this help message and exit
  -c PATH, --config PATH
                        Read configuration from ``PATH``. A configuration file can
                        specify names to ignore and/or preserve, optionally
                        using wildcards. If a file or folder matches an
                        ``ignore`` name, it will not be counted when considering
                        whether a folder is empty. Thus a folder which only
                        contains ignorable files or folders will be considered
                        empty. Ignored folders will not have their contents
                        examined. If a folder matches a ``preserve`` name, it
                        will not be deleted even if it would be considered
                        empty. Preserved folders will also not have their
                        contents examined. Note the concept of ``preserve`` only
                        applies to folders. If this option is not provided,
                        the environment variable ``FINDEMPTY_CONFIG``, if present,
                        will be used, and failing that, a default config will
                        be used.
  -d, --delete          Delete empty folders as they are discovered. This will
                        include any ignored contents.
  -v, --verbose         Prints the paths of empty folders as they are
                        discovered. This is the default unless -d/--delete is
                        specified. Specify twice to also print the ignored
                        contents of empty folders, if any.
  --debug               Print debugging information to stderr.
  -0, --print0          Use null characters (\\0) instead of newlines (\\n) when
                        printing names via the -v/--verbose option.
  --no-config           Suppress configuration loading entirely. No files or
                        folders will be ignored, and no folders will be
                        preserved.
  --no-env              Do not read environment variables when searching for a
                        config path.
  --show-default-config
                        Prints the default config to stdout.
