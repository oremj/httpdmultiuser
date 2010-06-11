from functools import wraps
from optparse import OptionParser, make_option

from . import apache


commands = {}
def command(f):
    parser = OptionParser()
    for o in getattr(f, 'options', []):
        parser.add_option(o)

    @wraps(f)
    def wrapper(*args, **kwargs):
        opts, args = parser.parse_args(args=list(args))
        return f(opts, *args)

    commands[f.__name__] = wrapper
    return wrapper
    

@command
def restart(opts, *args):
    for a in apache.all_apaches():
        a.restart()
