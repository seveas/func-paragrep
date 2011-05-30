# grep.py -- func module for paragrep
#
# Deploy this module to all your hosts you want to be able to query with
# paragrep. For more information about paragrep, see
# https://github.com/seveas/paragrep.
#
# (c) 2011 Dennis Kaarsemaker <dennis@kaarsemaker.net>
# License: GPL 3+

import func_module as fm
from func import logger
import glob
import os
import subprocess

def flatten(args):
    if not args:
        return []
    ret = args[0]
    for arg in args[1:]:
        ret += arg
    return ret

class Grep(fm.FuncModule):
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Grep logs"

    def grep(self, opts, regex, files):
        l = logger.Logger().logger
        l.info("Received grep request: %s %s" % (str(opts), str(files)))

        sanitize_opts(opts)
        sanitize_files(files)

        prog = '/bin/grep'
        if opts.pop('-z', False):
            prog = '/usr/bin/zgrep'
        elif opts.pop('-j', False):
            prog = '/usr/bin/bzgrep'
        files = flatten([glob.glob(x) for x in files])
        cmd = [prog] + [x for x in opts.keys() if opts[x] == 'None'] + flatten([list(x) for x in opts.items() if x[1] != 'None']) + [regex] + files
        sp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = sp.communicate()
        return (sp.returncode, out, err)

def sanitize_files(files):
    for f in files:
        while os.path.islink(f):
            f = os.path.readlink(f)
        if not f.startswith('/var/log'):
            raise ValueError("File not alllowed: %s" % f)

def sanitize_opts(opts):
    allowed_opts = ['-' + x for x in 'ABCEHLPcfhilnoqrsvwxz']
    with_int_args = ['-' + x for x in 'ABC']

    for opt in opts:
        if opt not in allowed_opts:
            raise ValueError("Option not allowed: %s" % opt)
    for opt in with_int_args:
        if opt in opts:
            try:
                opts[opt] = str(int(opts[opt]))
            except ValueError:
                raise ValueError("Invalid argument for %s: %s" % (opt, opts[opt]))
