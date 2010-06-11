from functools import wraps
from optparse import OptionParser, make_option

from . import apache


commands = {}
def command(options=None, usage=''):
    if not options:
        options = []
    def wrapper(f):
        parser = OptionParser(usage=usage % {'f': f.__name__})
        for o in options:
            parser.add_option(o)

        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            opts, args = parser.parse_args(args=list(args))
            return f(opts, *args)

        commands[f.__name__] = inner_wrapper
        return inner_wrapper

    return wrapper
    

@command(usage='usage: %%prog %(f)s {all|appname appname}')
def restart(opts, *args):
    for a in apache.all_apaches():
        if 'all' in args or a.name in args:
            a.restart()


@command([make_option("-s", "--sort", default='name')])
def report(opts, *args):
    apache.print_report(apache.all_apaches(), sort=opts.sort)


@command(usage='usage: %%prog %(f)s {all|appname appname}')
def reload(opts, *args):
    for a in apache.all_apaches():
        if 'all' in args or a.name in args:
            a.restart()

@command()
def show_commands(*args):
    for c in commands:
        print c
