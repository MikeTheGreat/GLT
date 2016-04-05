# NEXT STEPS:
# Create students for a class / delete students from a class
#       (Delete students' projects, as well)
# Figure out how to roll up errors / success messages

# DONE: CLI cmd-line args
# DONE: Use the built-in Python map intead of the IterateOver____?  No - the improvement isn't immense, and what we've got works
# DONE: How to set up teacher project & student projects and/or have fork the teacher copy into the student groups?
# DONE: Figure out how to get the GitLab server to send email (SendGrid?)


import gitlab
import argparse
import os.path

class StudentsFromFile:
    def __init__(self, thoseWith = list(), thoseWithout = list()):
        self.studentsWithEmails = thoseWith
        self.studentsWithoutEmails = thoseWithout

class Student:
    def __init__(self, fName, lName, email):
        self.firstName = fName
        self.lastName = lName
        self.email = email

    def __str__(self):
        # Note that self.email may be empty.  This is ok - it'll make deserializing it easier.
        return self.lastName + ", " + self.firstName + ", " +  + self.email

    def __repr__(self):
        return self.__str__()

    def getUserName(self):
        return self.firstName+self.lastName;

    def getGroupName(self):
        return self.getUserName() + "_GROUP"

def ReadStudentList_CSV(f):
    """Read CSV file of student info, return a StudentsFromFile object
    f: file object, already open for reading"""
    students = list()
    theClass = StudentsFromFile()

    for line in f:
        line = line.strip()
        commentMarker = line.find('#')
        if commentMarker != -1:
            line = line[:commentMarker]
            if line == "":
                continue

        words = line.split(',')
        firstName = words[0].replace(" ", "").strip()
        lastName = words[1].replace(" ", "").strip()
        if len( words ) > 2 :
            email = words[2].replace(" ", "").strip()
        else:
            email = ""

        student = Student( firstName, lastName, email )
        if student.email != "":
            theClass.studentsWithEmails.append( student )
        else:
            theClass.studentsWithoutEmails.append( student )

    return theClass

def IterateOverStudents(iterFunc, **kwargs):
    studentList = ReadStudentList_CSV()
    for st in studentList:
        # print st
        iterFunc( student = st, **kwargs )

def PrintStudents(**kwargs):
    assert 'student' in kwargs, "NO STUDENT ARG WAS PROVIDED TO PrintStudents"
    print str( kwargs['student'] )

def CreateStudentAccountsInGitlab(**kwargs):
    assert 'gl' in kwargs,"NO gl (GitLab object) ARG WAS PROVIDED TO CreateStudentAccountsInGitlab"
    assert 'student' in kwargs, "NO STUDENT ARG WAS PROVIDED TO CreateStudentAccountsInGitlab"
    student = Student(kwargs['student'])
    gl = kwargs['gl']

    #print "create a new user for " + student.firstName + " " + student.lastName + " ========================="
    #print kwargs

    # TODO: Error handling
    # TODO: Prohibit creation of new groups
    user_data = {'name': student.firstName + ' ' +  student.lastName, 'email': student.email, 'projects_limit':20, 'can_create_group':False, 'username': student.getUserName(), 'password':'PASSWORD'}
    #print(user_data)

    # There doesn't appear to be an easy way to look up an account based on
    # username, etc.
    # If the user's account already we'll get an error here:
    try:
        user = gl.users.create(user_data)
    except gitlab.exceptions.GitlabCreateError as e:
        print "Couldn't create account for " + student.firstName + " " + student.lastName + "(email: " + student.email + ")\n\tError Message: " + e.error_message + "\n\tResponse code: " + str(e.response_code) + "\n\tResponse Body: " + e.response_body
        return

    # print( "\tCreate a new group, just for that user =====" )
    # TODO: limit access to the new group?
    user_group = {'name': student.getGroupName(), 'path':user_data['username']+'_GROUP' }
    try:
        group = gl.groups.create(user_group)
    except gitlab.exceptions.GitlabCreateError as e:
        print "Couldn't create individual group for " + student.firstName + " " + student.lastName + "(email: " + student.email + ")\n\tError Message: " + e.error_message + "\n\tResponse code: " + str(e.response_code) + "\n\tResponse Body: " + e.response_body
        return
        # TODO: At this point the student's account exists but the group doesn't - what to do?

    # print "\tAdd the user to the group"
    add_user_to_group = { 'user_id':user.id, 'group_id':group.id, 'access_level':gitlab.objects.Group.DEVELOPER_ACCESS}
    try:
        enrolled = gl.group_members.create( add_user_to_group )
    except gitlab.exceptions.GitlabCreateError as e:
        print "Couldn't add " + student.firstName + " " + student.lastName + "(email: " + student.email + ") to the group that was just created for them\n\tError Message: " + e.error_message + "\n\tResponse code: " + str(e.response_code) + "\n\tResponse Body: " + e.response_body
        return
    print "SUCCESS: " + student.firstName + " " + student.lastName

def ListGroups(**kwargs):
    """ Function that is given a 'student' object and then lists the groups that this student belongs to"""
    assert 'gl' in kwargs,"NO gl (GitLab object) ARG WAS PROVIDED TO CreateStudentAccountsInGitlab"
    assert 'student' in kwargs, "NO STUDENT ARG WAS PROVIDED TO CreateStudentAccountsInGitlab"
    student = kwargs['student']
    gl = kwargs['gl']

    groups = gl.groups.search(student.getGroupName())
    print "for student " + student.getUserName() + " found the following groups: "
    for group in groups:
        #group.display(True)
        #group.pretty_print(1)
        print str(group)

def ListProjects(**kwargs):
    assert 'gl' in kwargs,"NO gl (GitLab object) ARG WAS PROVIDED TO CreateStudentAccountsInGitlab"
#   assert 'student' in kwargs, "NO STUDENT ARG WAS PROVIDED TO CreateStudentAccountsInGitlab"
#   student = kwargs['student']
    gl = kwargs['gl']

    #projects = gl.projects.search( "PrivacyTestProject" )
    projects = gl.projects.all()
    print "Found the following projects: "
    for project in projects:
        #if not project.name == 'PrivacyTestProject':
        #   continue

        #group.display(True)
        project.pretty_print(1)
        #print str(project)
        print project.creator_id
        print
        owner = gl.users.get(project.creator_id )
        print 'owner: ' #+ str(owner)
        owner.pretty_print(3)
        print
        print "="*20
        print

FIRST_NAME = 0
LAST_NAME = 1

def GetNames(nameFromBriefcase):
    text = list()
    #print "GetNames:", nameFromBriefcase

    for part in str.split(nameFromBriefcase):
        text.append( str.title(str.strip(part) ) )

    #print "parts: ", text

    # middle intials are placed at the end, which we want to ignore:
    if len(text[-1]) == 1:
        text.pop() # remove last item

    fName = text.pop() # remove last item (the first name)
    lName = "_".join(text)

    return [fName, lName]

from HTMLParser import HTMLParser

# This enum lists off the state machine (SM) states
# that the parser will need to go through
SEARCHING_FOR_STUDENT_TABLE = 1
PASSING_HEADER_ROW = 2
PARSING_STUDENTS = 3
FINISHED = 4;

#def ReadStudentList_HTML( filePath = "StudentList.txt"):
def ReadStudentList_HTML( myfile):
    """Read file of student info, return a StudentsFromFile object
    f: file object, already open for reading. Must be in  the WA state 'Course Roster' format from Instructor Briefcase"""
    parser = MyHTMLParser()
    with open( filePath ) as myfile:
        for line in myfile:
            if parser.state == FINISHED:
                break
            parser.feed(line)

    return StudentsFromFile(parser.studentsWithEmailAddress, parser.studentsWithoutEmailAddress)

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.state = SEARCHING_FOR_STUDENT_TABLE
        self.cTable = 0
        self.cRow = 0
        self.cCell = 0
        self.studentsWithEmailAddress = list()
        self.studentsWithoutEmailAddress = list()
        # accumulate the parts of the student as we parse each row in the table:
        self.name = ""
        self.email = ""

    def handle_starttag(self, tag, attrs):
        # 1) look for the table of students:
        if self.state == SEARCHING_FOR_STUDENT_TABLE:
            if tag == 'table':
                #print 'found a table!'
                self.cTable += 1
                if self.cTable == 3:
                    self.state = PASSING_HEADER_ROW
                    #print 'found third table, about to ignore header row'

    def handle_endtag(self, tag):
        # 2) Look for the end of the header row
        if self.state == PASSING_HEADER_ROW and tag == 'tr':
            #print 'reached end of header row'
            self.state = PARSING_STUDENTS
            #print 'Next student:'

        # 3) as we pass cells remember to count them
        elif self.state == PARSING_STUDENTS and tag == 'td':
            #print "tag: " + tag + " cCell: " + str(self.cCell)
            self.cCell += 1

        # 6) Once we've finished a student row, pack info into an object
        elif self.state == PARSING_STUDENTS and tag == 'tr':
            names = GetNames(self.name)
            studentObj =Student(names[FIRST_NAME], names[LAST_NAME], self.email)
            if self.email == "":
                self.studentsWithoutEmailAddress.append( studentObj )
            else:
                self.studentsWithEmailAddress.append( studentObj )
            #print "Next student: ", cur
            #print "Looking for next Student:"
            self.cCell = 0
            # fields may be missing (especially the email field)
            self.name = ""
            self.email = ""

        elif self.state == PARSING_STUDENTS and tag == 'table':
            self.state = FINISHED


    def handle_data(self, data):
        # In general, ignore the extra, formatting tabs and spaces that litter the file
        if str.strip(data) == "":
            return

        # 4) Found the student's name!
        #print 'Data: ' + data + " cCell: " + str(self.cCell)
        elif self.state == PARSING_STUDENTS and self.cCell == 2:
            #print "\tName:" + data
            self.name = data

        # 5) Found the student's email!
        elif self.state == PARSING_STUDENTS and self.cCell == 6:
            #print "\tcCell: " + str(self.cCell) + " Email:" + data
            self.email = data

FILETYPE_CSV = "csv"
FILETYPE_HTML = "wa_html"
def VerifyType( fileType ):
    """fileType is something like CSV or .CSV, returns a FILETYPE_ string if matched (and None if nothing matches)"""
    """Supported file types: CSV, TXT (assumed to be CSV), HTML or WA_HTML"""

    # just in case someone specifies 'CSV' instead of csv, etc:
    fileType = fileType.translate(None, '\'". ').lower()

    print "\tVerifyType without dot:"+ fileType+"<<<"

    if fileType == 'csv' or \
       fileType == 'txt':
        print '\tFound "csv"'
        return FILETYPE_CSV
    elif fileType == 'html' or \
         fileType == 'wa_html':
        print "\tFound 'HTML'"
        return FILETYPE_HTML
    else:
        return None

print "GitLab Tool (glt)"

parser = argparse.ArgumentParser()
grpCreateStudents = parser.add_argument_group('New student accounts', "This will create new student accounts from the provided info")
grpCreateStudents.add_argument('-s', '--create_students', action="store_true", help="Read student info from a file and create accounts in the GitLab server")
grpCreateStudents.add_argument('-i', '--infile', type=argparse.FileType('r'), help="Specify the file that contains the student info.  File type is inferred from the extension")
grpCreateStudents.add_argument('-t', '--infile_type', help="Specify the file type, overriding the file extension.  Currently recognized options are 'csv', 'txt' (which is csv), 'html' or 'wa_html' (from the Instructor Briefcase roster pages in WA state)" )
args = parser.parse_args()


if args.create_students:
    if args.infile == None:
        print "You need to specify an input file in order to create all the student accounts!"
        exit()

    # either use -t to specify filetype or else
    # infer from extension
    if args.infile_type != None: # specified file type via command-line option
        fileType = VerifyType(args.infile_type)
    else: # we should infer the file type from the extension
        extension = os.path.splitext(args.infile.name)[1]
        print "found extension: ", extension
        fileType = VerifyType( extension )

    if fileType == None:
        # whatever file type was found, we don't recognize it
        if args.infile_type != None:
            print 'Despite specifying ',args.infile_type, " on the command line we don't recognize that format"
        else:
            print 'The file extension we found, ', extension, " was not a recognized file format"
        exit()

    print 'Verified file type: ', fileType
    if fileType == FILETYPE_CSV:
        studentList = ReadStudentList_CSV(args.infile)
    elif fileType == FILETYPE_HTML:
        studentList = ReadStudentList_HTML( args.infile )
    # then read student list
    #       print warnings to screen & ignore
    #       print errors to screen AND print to CSV file
    # TODO: modify CSV reader to ignore '#....' comments, so we can put error messages into them
    exit()
    print 'Creating student accounts'

print args
exit()

#theClass = ReadStudentList_CSV("StudentList.txt")
theClass = ReadStudentList_HTML("SampleInputs/class_roster.html")
print "The following students have email addresses:"
for student in theClass.studentsWithEmails:
    print student

print "The following students DO NOT have email addresses:"
for student in theClass.studentsWithoutEmails:
    print student


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
#    for student in parser.studentsWithoutEmailAddress:
#        print str(student)





###############################################################################
############################### 'Main' ########################################
###############################################################################

# or username/password authentication
# gl = gitlab.Gitlab('http://10.0.0.14', email='root', password='YetAn0therPassw0rd!')
#gl = gitlab.Gitlab('http://cccgitlab.westus.cloudapp.azure.com/', email='root', password='FuckThis!1')

# make an API request to create the gl.user object. This is mandatory if you
# use the username/password authentication.
#print 'Connecting to GitLab server'
#gl.auth()

#print 'Creating student accounts in the GitLab server'
# IterateOverStudents( CreateStudentAccountsInGitlab, gl = gl )

#print 'Listing projects:'
#IterateOverStudents( ListProjects,  gl = gl )
#ListProjects(gl=gl)
#exit()




#print( 'list all the projects')
#projects = gl.projects.list()
#for project in projects:
#   print(project)
#   print( " " )
#   print( ' ' )




#The GitLab API is rather good and you could use it for all of your repo setup with permissions and whatnot. Here is what I think you'd want to do.
#
#Create a script that will create a group in GitLab for homework assignment. The script could then pull in the users from the class that this assignment is for. It would then create a privite repository in this group for each student from the class. It could then also email them the link to the newly created git repository for their assignment.
#
#If you wanted to include instructions within the repo about the assignment, create a base git repo with a README.md file explaining the details for each assignment. Then for repository creation, create a fork of this repository for each student as a private repository (basically like above except we are forking instead of creating an empty repository).
#
#For being able to grade offline, I'd say you'd want to write a script that would check out every git repository in a given group. That would give you each students submissions for the homework assignment with one script.
#
#Further down the road ...
#You could also turn on GitLab CI for automatic evualuation of the assignment. This would essentially build the code into a live environment to run tests against and return the results. Going this route would also be beneficial to do the forking method as the jobs in CI are all controlled by a '.gitlab-ci.yml' file. Forking the base repo with this file will automatically add CI jobs for the newly created fork'd repository.
#
#If you had a long running project that went the length of a class (ie a webapp, start with a home page, add shopping cart, add this, add that), then you could also automaticlaly assign new assignments by creating an issue in the project for each repository in the group (through the API). So maybe the base repo everyone forks from is an empty Rails project or something. Then you could add an issue against everyone's forks to add a model that creates these tables in the database. Add another issue to setup user login, etc.

### Setup for each HW assignment:
# Load this up using a config file.
#       Each line should have: GROUP_NAME, PROJECT_NAME, [LOCAL_GIT_REPO_TO_MERGE_AND_PUSH - optional]
#           The idea is that a line might look like BIT_142, Assignment_1_BIT_142, E:\work\starter projects\BIT 142\Assign1
#           The last, optional argument can be used to auto-load stuff into GitLab
# If the group doesn't exist already then create it  (all items private to the world by default)
# Allow each student access to the new group
# Create private project in group
#       Uncheck 'merge requests', so students can't submit pull requests (which would be visible to other students)
#       Leave the main branch protected, so that students can't change the instructor's copy (which others can see)
#       Allow each student access to the new project
# If a local git repo is specified:
#       Download the project to a local git folder
#       Merge the optional repo in (this should always work since the GitLab project is empty)
#       Push the changes back to GitLab
#       TODO: Remember to set up a .gitignore file that'll filter out the cruft (bin, obj, etc)

### Student workflow:
# Log in to GitLab
# Find the project for their assignment
# Fork the assignment
#       When student forks the project it'll be private by default (b/c it inherits from origin)
#               TODO: Tell students they must keep the project private!!
#       These projects keep the origin project's name by default.
#               Renaming it is hidden in the settings page, and has  warning next to it
#               TODO: Tell students they can't change the name
#       New, forked project is put under the student's namespace (so we can't look for projects within the group)
#       If the student attempts to fork a second time in the GitHub website they will instead go to their already-created fork
# Clone to their local machine
# Do the work
# Add & commit locally
# Push back to the server
#
### Grading (Retrieve Student Work) workflow:
# Use the API to get a list of all projects, filter that list for only items that match the project name
#       (use Python's filter function?)
# For each student project on GitLab:
#       Allow the administrator account access to the project (so we can push to it later)(TODO: Do we need to do this?)
#       Within the assignment sub-dir, create a local sub-sub-dir for that student student (ST-style)
#       Do a local clone into that dir (or if it exists then pull in order to 'freshen' it)
#           Build a list of things that need to be updated based on whether the student last committed to it or I did
#
### Grading (Send Feedback To Students) workflow:
# As I grade, leave feedback files in the local repos
# Run a script which will iterate through all the local repos:
#       Add all files there (i.e., the feedback file) and commit
#       Tag the commit as the "initial version"
#       Push the commit to the server
# Post an announcement through ST/Canvas telling everyone to go get their feedback
#
### Revising Student Work workflow:
# Student keeps working in the same repo
# Student commits work locally, then pushes to GitLab
# Re-use Retrieve Student Work workflow to mass-pull changes
# Instructor grades
# Re-use Send Feedback To Students to send feedback & tag revision
#
### Backups for later workflow:
# Foreach local, student repo:
#       Get the 'current commit' (head?)
#       checkout the appropriate tag
#       Copy the dirs to the backup location
#           Remove/avoid the .git directory
#       Restore the 'current commit'
#
### End of quarter clean-up
# TODO: Finish filling this out
# Remove student accounts
#       Remove all their projects
# Remove groups
#       Including any starter projects in the groups
