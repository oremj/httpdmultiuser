from functools import wraps
from optparse import OptionParser, make_option

from . import apache


commands = {}
def command(options=None):
    if not options:
        options = []
    def wrapper(f):
        parser = OptionParser()
        for o in options:
            parser.add_option(o)

        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            opts, args = parser.parse_args(args=list(args))
            return f(opts, *args)

        commands[f.__name__] = inner_wrapper
        return inner_wrapper

    return wrapper
    

@command
def restart(opts, *args):
    for a in apache.all_apaches():
        a.restart()

@command([make_option("-s", "--sort", default='name')])
def report(opts, *args):
    apache.print_report(apache.all_apaches(), sort=opts.sort)
