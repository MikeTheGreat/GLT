""" PrintUtils provides convenience routines for printing"""

import sys
from colorama import Fore, Style, init # Back,
init()

def print_error(msg, exc=None):
    """Print a message (in bold red) to standard error.
    Also print out information about the exception, if it's present"""
    print >> sys.stderr, Fore.RED + Style.BRIGHT
    print >> sys.stderr, msg
    print >> sys.stderr, Style.RESET_ALL

    if exc is not None:
        print >> sys.stderr, "\tError Message: " + exc.error_message
        print >> sys.stderr, "\tResponse code: " + str(exc.response_code)
        print >> sys.stderr, "\tResponse Body: " + exc.response_body
