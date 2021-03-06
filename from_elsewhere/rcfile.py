# This was borrowed from https://github.com/aequitas/rcfile
# and then modified slightly
# I added a 'section_list' entry to the dictionary
# so that we've got a concise list of all the sections
# (so the gradeList function can iterate over the courses)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function
from os.path import join, expanduser
import os
import logging

__version__ = "0.1.4"
__author__ = "Johan Bloemberg"
__license__ = "MIT"

log = logging.getLogger(__name__)

try:  # Python 2
    import ConfigParser
except ImportError:  # Python 3
    import configparser as ConfigParser


def merge(dict_1, dict_2):
    """Merge two dictionaries.
    Values that evaluate to true take priority over falsy values.
    `dict_1` takes priority over `dict_2`.
    """
    return dict((str(key), dict_1.get(key) or dict_2.get(key))
                for key in set(dict_2) | set(dict_1))


def get_environment(appname):
    prefix = '%s_' % appname.upper()
    vars = ([(k, v) for k, v in os.environ.items() if k.startswith(prefix)])

    return dict([(k.replace(prefix, '').lower(), v) for k, v in vars])


def get_config(appname, module_name, config_file):
    home = expanduser('~')
    files = [
        join('/etc', appname, 'config'),
        join('/etc', '%src' % appname),
        join(home, '.config', appname, 'config'),
        join(home, '.config', appname),
        join(home, '.%s' % appname, 'config'),
        join(home, '.%src' % appname),
        '.%src' % appname,
        config_file or ''
    ]

    config = ConfigParser.ConfigParser()
    read = config.read(files)
    log.debug('files read: %s' % read)

    if not config.has_section(module_name):
        return {}

    data = dict(config.items(module_name))
    data['section_list'] = config.sections()
    return data


def rcfile(appname, args={}, strip_dashes=True, module_name=None):
    """
        Read environment variables and config files and return them merged with predefined list of arguments.
        Arguments:
            appname - application name, used for config files and environemnt variable names.
            args - arguments from command line (optparse, docopt, etc).
            strip_dashes - strip dashes prefixing key names from args dict.
        Returns:
            dict containing the merged variables of environment variables, config files and args.
        Environment variables are read if they start with appname in uppercase with underscore, for example:
            TEST_VAR=1
        Config files compatible with ConfigParser are read and the section name appname is read, example:
            [appname]
            var=1
        Files are read from: /etc/appname/config, /etc/appfilerc, ~/.config/appname/config, ~/.config/appname,
            ~/.appname/config, ~/.appnamerc, .appnamerc, file provided by config variable in args.
        Example usage with docopt:
            args = rcfile(__name__, docopt(__doc__, version=__version__))
    """
    if strip_dashes:
        for k in args.keys():
            args[k.lstrip('-')] = args.pop(k)

    environ = get_environment(appname)

    if not module_name:
        module_name = appname

    config = get_config(appname, module_name, args.get('config', ''))

    return merge(merge(args, config), environ)