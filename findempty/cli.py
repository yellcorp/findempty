import findempty.config

import functools


CONFIG_PATH_ENVIRONMENT_KEY = "FINDEMPTY_CONFIG"


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
        scanner.scan(p)


class CLIError(Exception):
    pass


def run(argv=None):
    args = get_arg_parser().parse_args(argv)

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
