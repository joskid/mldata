#!/usr/bin/env python
"""
Convert from and to HDF5
"""

import sys, os, getopt
# adjust if you move this file elsewhere
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../utils'))
import h5conv

def usage():
    print """Usage: """ + sys.argv[0] + """ [options]

Options:

-s, --seperator
    Seperator to use to seperate variables in examples. Default is ','


<in-filename> <in format> <out-filename> <out format>
    Supported conversions are:

        libsvm -> h5
        arff -> h5
        uci -> h5

        h5 -> arff
        h5 -> csv
"""

class Options:
    """Option.

    Should not be instantiated.

    @cvar seperator: seperator to seperate variables in examples
    @type output: string
    """
    seperator = None



def parse_options():
    """Parse given options."""
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:', ['seperator='])
    except getopt.GetoptError, err: # print help information and exit
        print str(err) + "\n"
        usage()
        sys.exit(1)

    for o, a in opts:
        if o in ('-s', '--seperator'):
            Options.seperator = a
            sys.argv.remove(o+a)
        else:
            print 'Unhandled option: ' + o
            sys.exit(2)


if __name__ == "__main__":
    argc = len(sys.argv)
    if  argc < 5:
        usage()
        sys.exit(1)

    parse_options()
    h = h5conv.HDF5()

    if sys.argv[2] == 'h5':
        seperator = None
    elif Options.seperator:
        seperator = Options.seperator
    else:
        seperator = h.infer_seperator(sys.argv[1])

    h.convert(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], seperator)

