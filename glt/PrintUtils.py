""" PrintUtils provides convenience routines for printing"""

import logging
import sys
from colorama import Back, Fore, Style, init
init()

def print_error(msg, exc=None):
    """Print a message (in bold red) to standard error so the user can see it.
    Also print out information about the exception, if it's present.
    Log the same, while we're at it"""
    print >> sys.stderr, Fore.RED + Style.BRIGHT
    print >> sys.stderr, msg
    print >> sys.stderr, Style.RESET_ALL
    logger.error(msg)

    if exc is not None:
        print >> sys.stderr, "\tError Message: " + exc.error_message
        print >> sys.stderr, "\tResponse code: " + str(exc.response_code)
        print >> sys.stderr, "\tResponse Body: " + str(exc.response_body)

def print_color(color, msg, color_bg=None):
    """msg is a string to print
    color is a member of Fore.*
    msg will be printed in color, BRIGHT, and then all styles will be reset"""
    print color + Style.BRIGHT
    if color_bg is not None:
        print color_bg
    print msg + Style.RESET_ALL

def get_logger(name):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    # https://docs.python.org/2/library/logging.html#logrecord-attributes
    formatter = logging.Formatter("[%(asctime)s - %(filename)s:%(lineno)s - %(levelname)-8s ] %(funcName)10s(): %(message)s" )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    #logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.CRITICAL)
    return logger
logger = get_logger(__name__)
            
def require_variable(var, msg):
    """Verify that <var> is not None
    Otherwise print out <msg> and exit the program"""
    if var is None:
        print_error(msg)
        exit()

def require_env_option(env, option, msg):
    """Verify that <option> is in <env>.
    Otherwise print out <msg> and exit the program"""
    if option not in env or \
    env[option] is None:
        print_error(msg)
        exit()

def print_list(assign_dir, the_list, color, msg, missing_msg = None):
    if not the_list and missing_msg is not None:
        print_color( color, missing_msg )
    if the_list:
        print_color( color, msg )
    
        for item in the_list:
            print "\t" + item.replace(assign_dir, "")
        print "\n" + "="*20 + "\n"
