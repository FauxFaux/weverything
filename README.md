weverything
===========

Work out what warnings you need to disable to build nicely with -Weverything:

    % rm -f -- *.weverything
    % ./weverything.py -- make WARNINGOPTS='--weverything.py -Wno-sign-conversion' -- make clean
    Doing initial clean....  Done.
    Doing initial build..................  Done.
         1: -Wno-bad-function-cast
         1: -Wno-missing-field-initializers
         2: -Wno-switch-enum
       264: -Wno-shorten-64-to-32

You can just add the `-Wno` flags after `--weverything.py` in the command line.

Usage
=====
    ./weverything.py -- build-command [-whatever] --weverything.py [-whatever] -- clean-command
    ./weverything.py -- make CFLAGS='-O2 --weverything.py' -- make clean

It additionally creates a `.weverything` file for each class of warning, for easy review:

    % cat unreachable-code.weverything
    ./../cmdgen.c:736:6: warning: will never be executed
                int ret;
                ^~~~~~~~
    ./../re_lib/regexp.c:531:3: warning: will never be executed
                    break;
                    ^~~~~

And, right now, that's all it does.
