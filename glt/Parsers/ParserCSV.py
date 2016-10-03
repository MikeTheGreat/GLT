""" Code to parse the csv files.
This exists to exposer the read_student_list_csv function
File format:
first name, last name, [optional email address]

Note that this reads each line as a student,
copies any information that it finds into a Student object,
leaves any missing information as empty strings,
and puts all those objects into the 'no errors yet' pile
in the student collection
"""
from enum import Enum
from glt.MyClasses.Student import Student
from glt.MyClasses.StudentCollection import StudentCollection

class CsvMode(Enum):
    """Enumeration for instructor-supplied, or GLT-internal CSV file"""
    InstructorInput = 1
    Internal = 2

def read_student_list_csv(input_file, mode):
    """Read CSV file of student info, return a StudentCollection object
    input_file: file object, already open for reading
    mode: a member of CsvMode.
        InstructorInput has 3 columns (Last name, first name,
            email) and email may be missing
        Internal always has 4 columns (last, first, email, GitLab
            ID).  Function raises an exception if
            InternalMode doesn't have 4, full columns on
            any row.
    """
    #students = list()
    the_class = StudentCollection(list(), list())

    for line in input_file:
        # Start by removing comments
        comment_marker = line.find('#')
        if comment_marker != -1:
            line = line[:comment_marker]

        # Then trim leading/trailing whitespace
        line = line.strip()

        # If there's nothing left then ignore this line
        if line == "":
            continue

        # If there's a trailing comma (but nothing after it)
        # remove it
        if line[-1] == ",":
            line = line[:-1]

        words = line.split(',')
        first_name = words[0].replace(" ", "").strip()
        last_name = words[1].replace(" ", "").strip()
        if len(words) > 2:
            email = words[2].replace(" ", "").strip()
        else:
            email = ""
        if len(words) > 3 and words[3]:
            glid = int(words[3].replace(" ", "").strip())
        else:
            glid = -1

        if mode is CsvMode.Internal and \
            (email == "" or glid == -1):
            raise ValueError("ERROR: Reading internal file, but "\
                "missing email and/or GitLab ID on row" + line)

        # Note that we put the Student into the 'no errors yet'
        # pool even though we it won't work (GitLab won't create
        # accounts that lack an email address).  We'll handle
        # that in one central place (namely, the
        # create_student_accounts function)
        the_class.students_no_errors.append(\
            Student(first_name, last_name, email, glid))

    return the_class
