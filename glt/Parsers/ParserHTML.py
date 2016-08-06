""" Code to parse the HTML files generated by the WA state 'Briefcase' app
This exists to exposer the read_student_list_html function
"""
from HTMLParser import HTMLParser
from glt.MyClasses.Student import Student
from glt.MyClasses.StudentCollection import StudentCollection

FIRST_NAME = 0
LAST_NAME = 1

def get_names(name_from_briefcase):
    """Given a string containing the 'name' cell, return the first
    and last name parts
    Middle initials are found at the end of the line & removed/ignored
    The first name is the last word on the line
    The last name is everything else, joined with underscores"""
    text = list()
    #print "get_names:", name_from_briefcase

    for part in str.split(name_from_briefcase):
        text.append(str.title(str.strip(part)))

    #print "parts: ", text

    # middle intials are placed at the end, which we want to ignore:
    if len(text[-1]) == 1:
        text.pop() # remove last item

    first_name = text.pop() # remove last item (the first name)
    last_name = "_".join(text)

    return [first_name, last_name]

# This enum lists off the state machine (SM) states
# that the parser will need to go through
SEARCHING_FOR_STUDENT_TABLE = 1
PASSING_HEADER_ROW = 2
PARSING_STUDENTS = 3
FINISHED = 4

#def read_student_list_html( filePath = "SampleInputs/HTMLT/class_roster.html"):
def read_student_list_html(myfile):
    """Read file of student info, return a StudentCollection object
    f: file object, already open for reading. Must be in  the
        WA state 'Course Roster' format from Instructor Briefcase"""
    parser = MyHTMLParser()
#    with open( filePath, 'r' ) as myfile:
    for line in myfile:
        if parser.state == FINISHED:
            break
        parser.feed(line)

    return StudentCollection(parser.students_with_email_address, \
        parser.students_without_email_address)

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    """SAX-based parser class"""

    # pylint: disable=too-many-instance-attributes
    # We need all these, and they're not excessive

    def __init__(self):
        """Create blank lists (for students with and without emails),
        and set all counters to zero"""


        HTMLParser.__init__(self)
        self.state = SEARCHING_FOR_STUDENT_TABLE
        self.count_table = 0
        self.count_row = 0
        self.count_cell = 0
        self.students_with_email_address = list()
        self.students_without_email_address = list()
        # accumulate the parts of the student as we parse each row in the table:
        self.name = ""
        self.email = ""

    def handle_starttag(self, tag, attrs):
        """callback for a tag starting """
        # 1) look for the table of students:
        if self.state == SEARCHING_FOR_STUDENT_TABLE:
            if tag == 'table':
                #print 'found a table!'
                self.count_table += 1
                if self.count_table == 3:
                    self.state = PASSING_HEADER_ROW
                    #print 'found third table, about to ignore header row'

    def handle_endtag(self, tag):
        """callback for a tag ending """
        # 2) Look for the end of the header row
        if self.state == PASSING_HEADER_ROW and tag == 'tr':
            #print 'reached end of header row'
            self.state = PARSING_STUDENTS
            #print 'Next student:'

        # 3) as we pass cells remember to count them
        elif self.state == PARSING_STUDENTS and tag == 'td':
            #print "tag: " + tag + " count_cell: " + str(self.count_cell)
            self.count_cell += 1

        # 6) Once we've finished a student row, pack info into an object
        elif self.state == PARSING_STUDENTS and tag == 'tr':
            names = get_names(self.name)
            student_obj = Student(names[FIRST_NAME], names[LAST_NAME], \
                self.email)

            # Note that we put the Student into the 'no errors yet'
            # pool even though we it won't work (GitLab won't create
            # accounts that lack an email address).  We'll handle
            # that in one central place (namely, the
            # create_student_accounts function)
            self.students_with_email_address.append(student_obj)

            #print "Next student: ", cur
            #print "Looking for next Student:"
            self.count_cell = 0
            # fields may be missing (especially the email field)
            self.name = ""
            self.email = ""

        elif self.state == PARSING_STUDENTS and tag == 'table':
            self.state = FINISHED


    def handle_data(self, data):
        """callback for data """
        # In general, ignore the extra, formatting tabs and spaces that litter the file
        if str.strip(data) == "":
            return

        # 4) Found the student's name!
        #print 'Data: ' + data + " count_cell: " + str(self.count_cell)
        elif self.state == PARSING_STUDENTS and self.count_cell == 2:
            #print "\tName:" + data
            self.name = data

        # 5) Found the student's email!
        elif self.state == PARSING_STUDENTS and self.count_cell == 6:
            #print "\tcount_cell: " + str(self.count_cell) + " Email:" + data
            self.email = data


#class MyHTMLParser(HTMLParser):
#    def handle_starttag(self, tag, attrs):
#        print "Encountered a start tag:", tag
#    def handle_endtag(self, tag):
#        print "Encountered an end tag :", tag
#    def handle_data(self, data):
#        print "Encountered some data  :", data, " len: ", len(data)
#        if data == '\t':
#            print "\t\tTHIS IS A TAB!!!"

# instantiate the parser and fed it some HTML
#data = ""
#parser = MyHTMLParser()
#with open( "SampleInputs/class_roster.html") as myfile:
#    #data = myfile.read()
#    for line in myfile:
#        #if parser.state != FINISHED:
#        #    print '============= About to parse: ' + line
#        parser.feed(line)
#
#    print "Got the following students:"
#    for student in parser.students:
#        print str(student)
#    # print "\n".join(parser.students)
#
#    print "The following students have no email address:"
#    for student in parser.students_without_email_address:
#        print str(student)