#!/usr/bin/env python
import sys
from collections import namedtuple
import subprocess
import re
import operator

Cmds = namedtuple('Cmds', ['build', 'clean'])

def usage(app):
    print("usage:")
    print(("    %s -- build-command [-whatever] --weverything.py" +
        "[-whatever] -- clean-command") % app)
    print("    %s -- make CFLAGS='-O2 --weverything.py' -- make clean" % app)
    sys.exit(1)

def run(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(("$ %s") % ' '.join(cmd))
        print(e.output)
        raise

def parse(args):
    if len(args) < 4 or args[1] != '--' or not '--' in args[2:]:
        usage(args[0])
    second_split = args[3:].index('--') + 3
    return Cmds(build=args[2:second_split], clean=args[second_split+1:])

def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def build_with(cmds, opts):
    cmd = [x.replace('--weverything.py', opts) for x in cmds.build]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    i = 0
    err = ''
    warnings = {}
    warning_re = re.compile('^(?P<loc>(?P<file>.+?):(?P<line>\d+):(?P<pos>\d+)): ' +
            'warning: .*\[(?P<flag>-W.*?)\]$')
    current_warn = None
    slurp_count = 0
    slurp = ''
    for line in p.stdout:
        if i % 10 == 0:
            write('.')
        i=i+1
        err += line

        if slurp_count:
            slurp_count -= 1
            slurp += line
            if not slurp_count:
                warnings[current_warn.group('loc')] = (slurp, current_warn)
                flag = current_warn.group('flag')
                path = flag.replace('-W', '') + '.weverything'
                with open(path, 'a') as f:
                    f.write(slurp
                            .replace(' [' + flag + ']', '')
                            .replace('warning', '\033[93mwarning\033[0m'))
            continue

        res = warning_re.match(line)
        if not res:
            continue
        current_warn = res
        slurp_count = 5
        slurp = line
    ret = p.wait()
    if 0 != ret:
        print(("$ %s") % ' '.join(cmd))
        print(err)
        print('')
        print(('Build unexpectedly failed: %s') % cmd)
        sys.exit(2)
    print('.  Done.')

    return warnings
Cmds.build_with = build_with

if __name__ == "__main__":
    cmds = parse(sys.argv)
    write("Doing initial clean...")
    run(cmds.clean)
    print(".  Done.")
    write("Doing initial build...")
    warnings = cmds.build_with('-Weverything')
    scores = {}
    for warn in warnings.values():
        flag = warn[1].group('flag')
        if not flag in scores:
            scores[flag] = 0
        scores[flag] += 1
    for flag, score in sorted(scores.iteritems(), key=operator.itemgetter(1)):
        print(("%6d: %s") % (score, flag.replace('-W', '-Wno-')))
