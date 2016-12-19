""" GitLabUtils contains functions useful for interacting with the GitLabServer"""

from colorama import Fore, Style, init
init()
import gitlab
from glt.MyClasses.StudentCollection import UserErrorDesc
from glt.Constants import EnvOptions
from glt.PrintUtils import print_error

def connect_to_gitlab(env):
    """make an API request to create the glc.user object. This is mandatory
        if you use the username/password authentication."""
    glc = gitlab.Gitlab(env[EnvOptions.SERVER], \
        email=env[EnvOptions.USERNAME], \
        password=env[EnvOptions.PASSWORD])

    # print 'Connecting to GitLab server'
    try:
        glc.auth()
    except gitlab.GitlabError as exc:
        print_error( 'Unable to connect to the GitLab server', exc )
        exit()
    return glc

def create_student_accounts(glc, student_list):
    """ Attempt to create accounts for all students in the
    'no errors yet' list of student_list"""

    # We can't modify the list we're iterating over, so make a copy
    # (just in case we remove any)
    remove_from_students_no_errors = []

    for student in student_list.students_no_errors:

        # We could pre-emptively remove any Student objects
        # that the GitLab server won't accept here
        # (GitLab requires a username, a password, a normal
        # name, and an email)
        # but instead we'll let GitLab validate stuff for us
        # It doesn't take too long to make the call to GitLab
        # We don't often do this operation
        # And it'll simplify the code here

        user_data = {'name': student.first_name + ' ' +  student.last_name, \
            'email': student.email, 'projects_limit':20, \
            'can_create_group':False, 'username': student.get_user_name(), \
            'password':'PASSWORD'}
        #logger.info(user_data)

        # If the user's account already we'll get an error here:
        try:
            user = glc.users.create(user_data)
        except gitlab.exceptions.GitlabCreateError as exc:
            remove_from_students_no_errors.append(student)
            student_list.students_with_errors.append(\
                UserErrorDesc(student,
                              str(exc.response_code)+": "+ exc.error_message))
            continue

        student.glid = user.id

        print "Created : " + student.first_name + " " + student.last_name

    # remove the students from the 'no errors' list:
    for student in remove_from_students_no_errors:
        student_list.students_no_errors.remove(student)

def delete_accounts_in_class(glc, course_info):
    """ Delete all accounts for students in student_list
     the Student objects MUST have an ID.  Any that don't get
     moved over to the 'errors' pile in student_list """

    didnt_remove = []
    student_list = course_info.roster

    # We can't modify the list we're iterating over, so make a copy
    # (just in case we remove any)
    for student in student_list.students_no_errors:

        try:
            glc.users.delete(student.glid)

        except Exception as exc:
            #print "Unable to remove " + str(student) + " because of:\n"\
            #    + str(exc.response_code)+": "+ exc.error_message

            didnt_remove.append(student)
            student_list.students_with_errors.append(\
                UserErrorDesc(student, \
                str(exc.response_code)+": "+ exc.error_message))
            continue

        print "Deleted: " + student.first_name + " " + student.last_name

    # students that weren't removed should be left in the class
    course_info.roster.students_no_errors = didnt_remove

def list_projects(glc):
    """ List all the projects in the GitLabServer """

    foundAny = False
    whichPage = 0

    projects = True
    while projects:
        print 'asking for page ' + str(whichPage)
        projects = glc.projects.all(page=whichPage, per_page=5)
        #projects = glc.projects.list(page=0, per_page=100)

        if projects: foundAny = True

        if not foundAny and not projects: # if projects list is empty
            print "No projects present"
            return

        print "Found the following projects:\n"
        for project in projects:
            print project.name_with_namespace + " ID: " + str(project.id)

        whichPage = whichPage + 1
    return

    print "Project Details:\n"
    for project in projects:
        print project.name_with_namespace + " ID: " + str(project.id)
        if hasattr(project, 'forked_from_project') and \
            project.forked_from_project['id'] == 44:
            print "THIS IS A FORKED PROJECT"

        #proj = project
        #owner = glc.users.get(project.creator_id)
        #print "\tcreated by " + owner.name
        #owner.pretty_print(3)
        #print "\tcreated on " + project.created_at
        project.pretty_print(1)
        print "="*20
        print

    #project2 = glc.projects.get({'id':19});
    #project2.pretty_print()

    #print glc.project_members.get({'project_id':15})
    #glc.project_members.create({'project_id':15, 'user_id':83, 'access_level':20})
    #project.pretty_print(1)


def list_groups(glc, student_list):
    """ DOES NOT WORK CURRENTLY
    Given a list of students then lists the groups that each student belongs to"""
    for student in student_list.students_no_errors:
        groups = glc.groups.search(student.get_group_name())
        print "for student " + student.get_user_name() + " found the following groups: "
        for group in groups:
            #group.display(True)
            #group.pretty_print(1)
            print str(group)
