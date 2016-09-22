import findempty.config

from argparse import ArgumentParser
import os.path
import sys


CONFIG_PATH_ENVIRONMENT_KEY = "FINDEMPTY_CONFIG"


def get_arg_parser():
    p = ArgumentParser(description="Find empty folders")

    p.add_argument("folders", nargs="*",
        metavar="FOLDERS",
        help="""Root folders to check for emptiness.""")

    p.add_argument("-c", "--config",
        metavar="PATH",
        default=None,
        help="""Read configuration from %(metavar)s. A configuration file
        can specify names to ignore and/or preserve, optionally using wildcards.
        If a file or folder matches an `ignore` name, it will not be counted
        when considering whether a folder is empty. Thus a folder which only
        contains ignorable files or folders will be considered empty. Ignored
        folders will not have their contents examined. If a folder matches a
        `preserve` name, it will not be deleted even if it would be considered
        empty. Preserved folders will also not have their contents examined.
        Note the concept of `preserve` only applies to folders.

        If this option is not provided, the environment variable {}, if present,
        will be used, and failing that, a default config will be
        used.""".format(CONFIG_PATH_ENVIRONMENT_KEY)
    )

    p.add_argument("-d", "--delete",
        action="store_true",
        default=False,
        help="""Delete empty folders as they are discovered. This will include
        any ignored contents."""
    )

    p.add_argument("-v", "--verbose",
        action="count",
        help="""Prints the paths of empty folders as they are discovered. This
        is the default unless --delete/-d is specified. Specify twice to also
        print the ignored contents of empty folders, if any."""
    )

    p.add_argument("--debug",
        action="store_true",
        default=False,
        help="""Print debugging information to stderr."""
    )

    p.add_argument("-0", "--print0",
        action="store_true",
        default=False,
        help="""Use null characters (\\0) instead of newlines (\\n) when
        printing names via the -v/--verbose option."""
    )

    p.add_argument("--no-config",
        action="store_true",
        default=False,
        help="""Suppress configuration loading entirely. No files or folders
        will be ignored, and no folders will be preserved."""
    )

    p.add_argument("--no-env",
        action="store_true",
        default=False,
        help="""Do not read environment variables when searching for a config
        path."""
    )

    p.add_argument("--show-default-config",
        action="store_true",
        default=False,
        help="""Prints the default config to stdout."""
    )

    return p


def deleter(path_obj, is_dir):
    if is_dir:
        path_obj.rmdir()
    else:
        path_obj.unlink()


def scan(
    paths,
    ignore_func,
    preserve_func,
    delete=False,
    line_delimiter="\n",
    verbose=0,
    debug=False
):
    scanner = findempty.scanner.EmptyFolderScanner(ignore_func, preserve_func)

    def printer(*args):
        zero_or_one_arg = args[:1]
        print(*zero_or_one_arg, end=line_delimiter)

    def debug_printer(text):
        print(text, file=sys.stderr)

    if not delete and verbose < 1:
        verbose = 1

    if verbose >= 2:
        scanner.handle_empty_descendant.append(printer)
    elif verbose == 1:
        scanner.handle_empty_root.append(printer)

    if delete:
        scanner.handle_empty_descendant.append(deleter)

    if debug:
        scanner.log = debug_printer

    for p in paths:
        if not (os.path.isdir(p) or os.path.ismount(p)):
            print("Not a directory or mount: {}".format(p), file=sys.stderr)
        else:
            scanner.scan(p)


class CLIError(Exception):
    pass


def run(argv=None):
    args = get_arg_parser().parse_args(argv)

    if args.show_default_config:
        with open(findempty.config.get_default_path(), "r") as config_stream:
            sys.stdout.write(config_stream.read())
        return

    if len(args.paths) == 0:
        raise CLIError("No paths specified.")

    ignore_func = None
    preserve_func = None

    line_delimiter = "\n"
    if args.print0:
        line_delimiter = "\0"

    if args.no_config:
        if args.config:
            raise CLIError("Both --config and --no-config options given.")
    else:
        config_path = args.config

        if config_path is None and not args.no_env and CONFIG_PATH_ENVIRONMENT_KEY in os.environ:
            config_path = os.environ[CONFIG_PATH_ENVIRONMENT_KEY]

        if config_path is None or len(config_path) == 0:
            ignore_func, preserve_func = findempty.config.load_default()
        else:
            ignore_func, preserve_func = findempty.config.load(config_path)

    return scan(args.paths, ignore_func, preserve_func, args.delete, line_delimiter, args.verbose, args.debug)


def main():
    return run(sys.argv[1:])
