"""StudentCollection is a struct that contains two lists"""
import collections
from glt.PrintUtils import print_error

#StudentCollection = collections.namedtuple('StudentCollection', \
#    ['students_no_errors', 'students_with_errors'])

"""This exists to hold a user & the string that describes
why we couldn't create the account"""
UserErrorDesc = collections.namedtuple('UserErrorDesc', \
    ['student', 'error_desc'])

class StudentCollection(object):
    """This holds a pile of student account information that
    doesn't yet have any errors, and a pile that have errors.
    the 'with errors' pile are all UserErrorDesc tuples"""

    def __init__(self, thoseWithEmailAddresses=None, thoseWithoutEmailAddresses=None):
        """Constructor: optionally stores the list of those with,
        and without, email addresses"""
        if thoseWithEmailAddresses is None:
            thoseWithEmailAddresses = list()
        if thoseWithoutEmailAddresses is None:
            thoseWithoutEmailAddresses = list()
        self.students_no_errors = thoseWithEmailAddresses
        self.students_with_errors = thoseWithoutEmailAddresses

    def print_errors(self):
        """If there are any UserErrorDescs in the students_with_errors list
        then print them out.
        Otherwise print nothing"""
        if self.students_with_errors:
            print "The following student accounts had problems:"
            for error in self.students_with_errors:
                print_error(str(error.student) + "\n\tERROR:" + error.error_desc)
