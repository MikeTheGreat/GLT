""" MainUtils contain functions,etc, that I want to use in main
but don't want to clutter up glt.py with"""

import argparse
import os.path

import rcfile
from colorama import Fore, Style, init, Back
init()

from glt.Parsers.ParserCSV import read_student_list_csv, CsvMode
from glt.Parsers.ParserHTML import read_student_list_html
from glt.Parsers.VerifyFileType import  verify_file_type, FileFormat

from glt.GitLabUtils import connect_to_gitlab, create_student_accounts,\
   list_projects, delete_accounts_in_class
from glt.MyClasses.StudentCollection import UserErrorDesc
from glt.MyClasses import CourseInfo
from glt.Constants import EnvOptions
from glt.PrintUtils import require_variable, require_env_option
from glt.GitDoUtils import generate_add_feedback, grade_list_collector

def parse_args():
    """Sets up the parse for the command line arguments, and parses them"""

    ################ Common options ################
    # Note: These must be listed (on the command line) before the subparser options
    common_parser = argparse.ArgumentParser(add_help=False)
    grp_server = common_parser.add_argument_group('Server Info', \
       "Options related to the server that you're using")
    grp_server.add_argument('-s', '--'+EnvOptions.SERVER.value, \
       help="URL for the GitLab server (e.g., http://10.0.0.17)")
    grp_server.add_argument('-u', '--'+EnvOptions.USERNAME.value, \
       help="Username to send to the GitLab server for authentication (e.g., root)")
    grp_server.add_argument('-p', '--'+EnvOptions.PASSWORD.value,\
       help="Password for the GitLab account")

    ### Set up the main parser, and it's subparsers
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest=EnvOptions.ACTION.value)

    ################ Add Homework ################
    add_students_parser = subparsers.add_parser(EnvOptions.NEW_HOMEWORK.value, \
              help="Add a homework assignment to GitLab; allow students to "\
              "fork it (but not issue pull requests back to it)", \
              parents=[common_parser])
    add_students_parser.add_argument(EnvOptions.SECTION.value, \
        help='Name of the course (e.g., bit142)')
    add_students_parser.add_argument(EnvOptions.HOMEWORK_NAME.value, \
        help='Name of the homework assignment (e.g., Assignment_1)')
    add_students_parser.add_argument(EnvOptions.HOMEWORK_DIR.value, \
        help="Specify a path to a directory that contains a Git repo "\
        "to seed the server with")

    ################ Add Students ################
    add_students_parser = subparsers.add_parser(\
        EnvOptions.CREATE_STUDENTS.value, \
              help="Read student info from a file and create accounts" \
             " in the GitLab server", parents=[common_parser])
    add_students_parser.add_argument(EnvOptions.SECTION.value,\
       help='Name of the course (e.g., bit142)')
    add_students_parser.add_argument(EnvOptions.INFILE.value,\
        type=argparse.FileType('r'), \
        help="Specify the file that contains the student info.  " \
                                     "File type is inferred from the extension")
    add_students_parser.add_argument('-t', '--'+EnvOptions.INFILE_TYPE.value, \
        help="Specify the file type, " \
        "overriding the file extension.  Currently recognized options are 'csv', 'txt' "\
        "(which is csv), 'html' or 'wa_html' (from the Instructor Briefcase" \
        " roster pages in WA state)")

    ################ Delete Class ################
    delete_class_parser = subparsers.add_parser(EnvOptions.DELETE_CLASS.value,\
              help="Remove all students accounts in the GitLab server" \
                " for a class/course (note that students' projects are "\
                "not removed)" \
               , parents=[common_parser])
    delete_class_parser.add_argument(EnvOptions.SECTION.value,\
        help='Name of the course (e.g., bit142)')

    ################ Download Homework ################
    download_parser = subparsers.add_parser(EnvOptions.DOWNLOAD_HOMEWORK.value, \
              help="Download student homework assignments (git projects)"\
              "from GitLab to a local directory", \
              parents=[common_parser])
    download_parser.add_argument(EnvOptions.SECTION.value, \
        help='Name of the course (e.g., bit142)')
    download_parser.add_argument(EnvOptions.HOMEWORK_NAME.value, \
        help='Name of the homework assignment (e.g., Assignment_1) OR '\
        '\'all\' to download all assignments')
    download_parser.add_argument('-w', '--'+(EnvOptions.STUDENT_WORK_DIR.value), \
        help="Specify a path to a directory to put the student work into."\
        "Each assignment will be placed in a subdirectory named after the "\
        "assignment, and each student's work will be placed in a "\
        "sub-subdirectory with the student's last and first name")

    ################ Commit Feedback ################
    upload_feedback = subparsers.add_parser(EnvOptions.COMMIT_FEEDBACK.value, \
              help="Commit feedback files that match a pattern, and tag the commit",
              parents=[common_parser])
    upload_feedback.add_argument(EnvOptions.SECTION.value, \
        help='Name of the course (e.g., bit142)')
    upload_feedback.add_argument(EnvOptions.HOMEWORK_NAME.value, \
        help='Name of the homework assignment (e.g., Assignment_1)')
    upload_feedback.add_argument('-a', '--'+(EnvOptions.FEEDBACK_PATTERN.value), \
        help="Specify a regex pattern to match for feedback files."\
        "If omitted the default is case-insensitive \""+\
        EnvOptions.FEEDBACK_PATTERN_DEFAULT +"\" (without " \
        "the quotes)" )
    upload_feedback.add_argument('-t', '--'+(EnvOptions.GIT_TAG.value), \
        help="Specify a string to use as a tag for this version (default is "
        "\""+EnvOptions.GIT_TAG_DEFAULT.value+"\")" )

    ################ Get Grading List ################
    grading_list = subparsers.add_parser(EnvOptions.GRADING_LIST.value, \
              help="Get lists indicating which assignments don't have feedback"\
              ", which have feedback but have been modified since then, and "\
              "which have been graded and are unchanged",
              parents=[common_parser])
    grading_list.add_argument(EnvOptions.SECTION.value, \
        help='Name of the course (e.g., bit142)')
    grading_list.add_argument(EnvOptions.HOMEWORK_NAME.value, \
        help='Name of the homework assignment (e.g., Assignment_1)')

    ################ Upload Feedback ################
    upload_feedback = subparsers.add_parser(EnvOptions.UPLOAD_FEEDBACK.value, \
              help="Upload student repo (including instructor feedback) " \
              " to the GitLab server",
              parents=[common_parser])
    upload_feedback.add_argument(EnvOptions.SECTION.value, \
        help='Name of the course (e.g., bit142)')
    upload_feedback.add_argument(EnvOptions.HOMEWORK_NAME.value, \
        help='Name of the homework assignment (e.g., Assignment_1)')
    upload_feedback.add_argument('-a', '--'+(EnvOptions.FEEDBACK_PATTERN.value), \
        help="Specify a regex pattern to match for feedback files."\
        "If omitted the default is case-insensitive \""+\
        EnvOptions.FEEDBACK_PATTERN_DEFAULT +"\" (without " \
        "the quotes)" )
    upload_feedback.add_argument('-t', '--'+(EnvOptions.GIT_TAG.value), \
        help="Specify a string to use as a tag for this version (default is "
        "\""+EnvOptions.GIT_TAG_DEFAULT.value+"\")" )

    ################ GitDo ################
    git_do = subparsers.add_parser(EnvOptions.GIT_DO.value, \
              help="Run a git command on every assignment (repo) in a directory"\
              "(Note the directory is specified by the "\
              + EnvOptions.STUDENT_WORK_DIR + \
              " variable in the .gltrc file)." \
              "  Example: \"glt gitdo BIT142 Assign_1 status\" "\
              "will run the 'git status' command on each repo in "\
              "BIT142's 'Assign_1' directory",
              parents=[common_parser])
    git_do.add_argument(EnvOptions.SECTION.value, \
        help='Name of the course (e.g., bit142)')
    git_do.add_argument(EnvOptions.HOMEWORK_NAME.value, \
        help='Name of the homework assignment (e.g., Assignment_1)')
    git_do.add_argument(EnvOptions.GIT_COMMAND.value, \
        nargs=argparse.REMAINDER, \
        help='The rest of the line is the git command to run')

    ################ List Projects ################
    subparsers.add_parser(EnvOptions.LIST_PROJECTS.value,\
       help='List all projects' \
        ' on the server', parents=[common_parser])

    ### Actually do the parsing:
    args = parser.parse_args()
    return args, parser

def load_environment():
    """This will load the command line arguments and .gltrc file variables into
    the 'env' return value.  It will also return the argparse parser (to print
    the help message, if needed) and it will load the course_info object
    if the 'section' and 'data_dir' variables are defined

    Returns: env, parser, known_good_accounts
    *    env: dictionary of all command-line args and .gltrc variables
    *    parser: argparse parser object
    *    course_info: either None, or the CourseInfo object for this section
            (including the roster, in a StudentCollection's 'good' list)
    """

    cmd_line_args, parser = parse_args()
    env = rcfile.rcfile("glt", args=vars(cmd_line_args), module_name="defaults")
    # Note that we've merged the command-line args into the rcfile info,
    # even though we use the cmd_line_args to check for command line args
    # (this allows us to override rcfile info but still get Python to
    # check cmd_line_args.X for typos in X)

    if EnvOptions.SECTION in env and \
        env[EnvOptions.SECTION] is not None:
        # Get the course-specific config info
        course = env[EnvOptions.SECTION].lower()
        env_course = rcfile.rcfile("glt", module_name=course)

        # the args override config info, so we'll have to merge
        # things here so that course stuff overrides defaults
        env = rcfile.merge(env_course, env)

    # known good accounts should be specified for each course, so
    # this list probably won't be available until after we load
    # the section-specific stuff
    #known_good_accounts = None
    #if EnvOptions.KNOWN_GOOD_ACCOUNTS in env and \
    #    env[EnvOptions.KNOWN_GOOD_ACCOUNTS] is not None:
    #    # load existing student account info:
    #    # (if it doesn't exist that's fine - just ignore it)
    #    if os.path.isfile(env[EnvOptions.KNOWN_GOOD_ACCOUNTS]):
    #        kga_file = open(env[EnvOptions.KNOWN_GOOD_ACCOUNTS], "r")
    #        known_good_accounts = read_student_list_csv(kga_file, CsvMode.Internal)

    course_info = None

    # Course info is stored in the data dir, in a file named <section>.txt
    if EnvOptions.DATA_DIR in env and \
        env[EnvOptions.DATA_DIR] is not None and \
        EnvOptions.SECTION in env and \
        env[EnvOptions.SECTION] is not None:

        # load existing course info (including the list of student accounts)
        # (if it doesn't exist that's fine - just ignore it)
        info_path = get_data_file_path(env)

        if os.path.isfile(info_path):
            info_file = open(info_path, "r")
            course_info = CourseInfo.CourseInfo(env[EnvOptions.SECTION], \
                info_file)
        else:
            course_info = CourseInfo.CourseInfo(env[EnvOptions.SECTION])

    # 'synthesize' useful variables from existing ones:
    if (EnvOptions.SERVER not in env or \
        env[EnvOptions.SERVER] is None) and \
        EnvOptions.SERVER_IP_ADDR in env and \
        env[EnvOptions.SERVER_IP_ADDR] is not None:
        env[EnvOptions.SERVER] = "http://"+env[EnvOptions.SERVER_IP_ADDR]


    return env, parser, course_info

def get_data_file_path(env):
    """Assumes that DATA_DIR and SECTION are defined,
    returns data file for this section"""
    return os.path.join( env[EnvOptions.DATA_DIR], \
        env[EnvOptions.SECTION] + ".txt")

def load_student_list(env):
    """Loads student account information into a StudentCollection's
    'no errors' list and returns that object.
    If use_known_good is True then the 'known good list'
        (listed in the env) is used instead.

    This is a UI function: it may print to the user, and/or exit the program
    """
    infile = None
    file_type = None

    # Earlier version of this function had an option to load roster
    #   (now part of course info file).  Extra params:
    # , use_known_good=False
    #if use_known_good is True:
    #    if EnvOptions.KNOWN_GOOD_ACCOUNTS not in env or \
    #        env[EnvOptions.KNOWN_GOOD_ACCOUNTS] is None:
    #        print Fore.RED + Style.BRIGHT
    #        print "You need to specify a 'known good accounts'"\
    #            " file in your .gltrc file"
    #        print Style.RESET_ALL
    #        exit()
    #    infile = open(env[EnvOptions.KNOWN_GOOD_ACCOUNTS], "r")
    #    file_type = FileFormat.FILE_TYPE_CSV_INTERNAL
    #else:
    if EnvOptions.INFILE not in env or \
        env[EnvOptions.INFILE] is None:
        print Fore.RED + Style.BRIGHT
        print "You need to specify an input file in order to " \
            "load student account information!"
        print Style.RESET_ALL
        exit()

    infile = env[EnvOptions.INFILE]

    # either use -t to specify filetype or else
    # infer from extension

    # if specified file type via command-line option
    if EnvOptions.INFILE_TYPE in env and \
        env[EnvOptions.INFILE_TYPE] is not None:
        file_type = verify_file_type(env[EnvOptions.INFILE_TYPE])
    else: # we should infer the file type from the extension
        extension = os.path.splitext(env[EnvOptions.INFILE].name)[1]
        # print "found extension: ", extension
        file_type = verify_file_type(extension)

    if file_type is None:
        # whatever file type was found, we don't recognize it
        if EnvOptions.INFILE_TYPE not in env and \
            env[EnvOptions.INFILE_TYPE] is not None:
            print 'Despite specifying ', env[EnvOptions.INFILE_TYPE], \
                " on the command line we don't recognize that format"
        else:
            print 'The file extension we found, ', extension, \
                " was not a recognized file format"
        exit()

    #print 'Verified file type: ', file_type

    # then read student list
    if file_type == FileFormat.FILE_TYPE_CSV:
        student_list = read_student_list_csv(infile, CsvMode.InstructorInput)
    elif file_type == FileFormat.FILE_TYPE_HTML:
        student_list = read_student_list_html(infile)
    # course roster used to be it's own file (now part of course info file)
    #elif file_type == FileFormat.FILE_TYPE_CSV_INTERNAL:
    #    student_list = read_student_list_csv(infile, CsvMode.Internal)

    return student_list

##### Main #####

def main():
    """ 'Main' function for glt.  Command-line tool just calls this
    to do everything"""
    #pylint: disable=too-many-statements,too-many-branches
    print Fore.WHITE + Style.BRIGHT + "GitLab Tool (glt)" + Style.RESET_ALL

    env, parser, course_info = load_environment()

    require_env_option(env, EnvOptions.ACTION, "Unrecognized action (or no action listed)")

    if env[EnvOptions.ACTION] == EnvOptions.CREATE_STUDENTS:

        print "\nAttempting to create student accounts for " + env[EnvOptions.SECTION] + "\n"

        require_env_option(env, EnvOptions.SECTION, \
            "You need to specify a section (course -e.g., bit142)"\
               " to create all the student accounts!")

        require_variable(course_info, \
            "Could not find the data file for this section " \
            "(expected to find it at " + get_data_file_path(env) + ")" )

        # load_environment already loaded up the known_good_accounts
        # next we need to load in the student list from the .CSV/.HTML/etc:
        student_list = load_student_list(env)

        # We want to remove already-existing accounts
        # instead of trying to add them again
        # (this way we can re-add the file for the entire class
        # and not worry about having to delete out individuals)

        if course_info.roster:
            for existing_student in course_info.roster.students_no_errors:
                if existing_student in student_list.students_no_errors:
                    student_list.students_no_errors.remove(existing_student)
                    student_list.students_with_errors.append(UserErrorDesc(\
                        existing_student, "Student's account is already"\
                        " listed in the roster for the section's data file (" + \
                        get_data_file_path(env)+")"))

        if not student_list.students_no_errors:
            print Fore.RED + Style.BRIGHT
            print "After removing existing accounts there "\
                "aren't any new accounts to add"
            print Style.RESET_ALL
            student_list.print_errors()
            exit()

        glc = connect_to_gitlab(env)
        create_student_accounts(glc, student_list)

        # any students' accounts that were successfully created
        # should be moved over to the course_info object:
        course_info.merge_students(student_list)

        # Tell the user about anything that didn't work:
        student_list.print_errors()

        # go back and add the new students to any existing projects
        # This probably won't happen much, but it will make it easier
        # to add students to a class late
        for assignment in course_info.assignments:
            project = glc.projects.get({'project_id':assignment.id})
            for student in course_info.roster.students_no_errors:
                if course_info.add_student_to_project(glc, project.project_id, student):
                    print 'Added ' + student.first_name + " " + student.last_name \
                        + " to existing project " + assignment.name

        # This will (re-)create the data file
        # It's worth noting that this will overwrite/replace
        # any existing files
        course_info.write_data_file(get_data_file_path(env))
        exit()

    if env[EnvOptions.ACTION] == EnvOptions.DELETE_CLASS:

        require_env_option(env, EnvOptions.SECTION, \
            "You need to specify a section (course -e.g., bit142)"\
               " to delete all the student accounts!")

        print "\nAttempting to delete student accounts in " + env[EnvOptions.SECTION] + "\n"

        require_variable( course_info, \
            "Could not find the data file for this section " \
            "(expected to find it at " + get_data_file_path(env) + ")" )

        glc = connect_to_gitlab(env)
        delete_accounts_in_class(glc, course_info)

        # This will (re-)create the 'known good accounts' file
        # It's worth noting that this will overwrite/replace
        # any existing files
        #write_student_list_csv(env[EnvOptions.KNOWN_GOOD_ACCOUNTS], student_list)
        course_info.write_data_file(get_data_file_path(env))

        # If any accounts weren't successfully deleted they'll still be listed
        # for another attempt
        course_info.roster.print_errors()
        exit()

    elif env[EnvOptions.ACTION] == EnvOptions.DOWNLOAD_HOMEWORK:

        require_env_option(env, EnvOptions.SECTION, \
        "You need to specify a section (course -e.g., bit142)"\
               " to create all the student accounts!")

        require_env_option(env, EnvOptions.HOMEWORK_NAME, \
            "You must specify the name of a homework assignment "\
            "(or 'all', to download all assignments for this class)")

        if env[EnvOptions.HOMEWORK_NAME] == 'all':
            print "\nAttempting to download all homework assignments for " \
                + env[EnvOptions.SECTION] + "\n"
        else:
            print "\nAttempting to download all homework assignment \"" +\
              env[EnvOptions.HOMEWORK_NAME] + "\" for " + \
              env[EnvOptions.SECTION] + "\n"

        require_env_option(env, EnvOptions.STUDENT_WORK_DIR, \
            "You must specify the directory to download the homework "\
            "assignment(s) to")

        require_variable( course_info, \
            "Could not find the data file for this section " \
            "(expected to find it at " + get_data_file_path(env) + ")" )

        glc = connect_to_gitlab(env)

        updated_projects = course_info.download_homework(glc, env)

        if not updated_projects:
            print "No projects have been updated/downloaded"
        else:
            print Fore.GREEN + Style.BRIGHT 
            print "Updated the following projects:"
            print Style.RESET_ALL
            for proj in updated_projects:
                print "\t" + proj.student_dest_dir \
                    .replace(env[EnvOptions.STUDENT_WORK_DIR], "")

            print "\nThese are all in the base directory of " + \
                env[EnvOptions.STUDENT_WORK_DIR]
            print "\n" + "="*20 + "\n"

        exit()

    elif env[EnvOptions.ACTION] == EnvOptions.GIT_DO:

        require_env_option(env, EnvOptions.SECTION, \
        "You need to specify a section (course -e.g., bit142)"\
               " to create all the student accounts!")

        require_env_option(env, EnvOptions.HOMEWORK_NAME, \
            "You must specify the name of a homework assignment "\
            "(or 'all', to download all assignments for this class)")

        require_env_option(env, EnvOptions.STUDENT_WORK_DIR, \
            "You must specify the directory containing the student projects")

        require_env_option(env, EnvOptions.GIT_COMMAND, \
            "You must specify a git command to execute")
        
        require_variable( course_info, \
            "Could not find the data file for this section " \
            "(expected to find it at " + get_data_file_path(env) + ")" )

        #glc = connect_to_gitlab(env)
                
        course_info.git_do(env)

        exit()

    elif env[EnvOptions.ACTION] == EnvOptions.LIST_PROJECTS:
        glc = connect_to_gitlab(env)
        print 'Listing projects:'
        list_projects(glc)

        exit()

    elif env[EnvOptions.ACTION] == EnvOptions.NEW_HOMEWORK:

        require_env_option(env, EnvOptions.SECTION, \
        "You need to specify a section (course -e.g., bit142)"\
               " to create all the student accounts!")

        print "\nAttempting to create homework assignment for " + env[EnvOptions.SECTION] + "\n"

        require_variable( course_info, \
            "Could not find the data file for this section " \
            "(expected to find it at " + get_data_file_path(env) + ")" )

        require_env_option(env, EnvOptions.HOMEWORK_NAME, \
        "You need to specify a name for the new homework assignment "\
                "(e.g., assignment_1)!")

        require_env_option(env, EnvOptions.HOMEWORK_DIR, \
        "You need to specify a directory containing an existing "\
                "Git repo to start the assignment with")

        require_env_option(env, EnvOptions.TEMP_DIR, \
        "You need to specify a temporary directory to read/write to")

        # Make sure the temp dir exists:
        if not os.path.isdir(env[EnvOptions.TEMP_DIR]):
            os.makedirs(env[EnvOptions.TEMP_DIR])

        require_env_option(env, EnvOptions.SERVER_IP_ADDR, \
        "You need to specify the IP address of the GitLab server")

        glc = connect_to_gitlab(env)

		# create the project on the server
        course_info.create_homework(glc, env)

        course_info.write_data_file(get_data_file_path(env))
        exit()
         
    elif env[EnvOptions.ACTION] == EnvOptions.COMMIT_FEEDBACK or\
         env[EnvOptions.ACTION] == EnvOptions.UPLOAD_FEEDBACK or\
         env[EnvOptions.ACTION] == EnvOptions.GRADING_LIST:

        require_env_option(env, EnvOptions.SECTION, \
        "You need to specify a section (course -e.g., bit142)"\
               " to create all the student accounts!")

        require_env_option(env, EnvOptions.HOMEWORK_NAME, \
            "You must specify the name of a homework assignment "\
            "(or 'all', to download all assignments for this class)")

        require_env_option(env, EnvOptions.STUDENT_WORK_DIR, \
            "You must specify the directory containing the student projects")

        require_variable( course_info, \
            "Could not find the data file for this section " \
            "(expected to find it at " + get_data_file_path(env) + ")" )

        pattern = None
        if EnvOptions.FEEDBACK_PATTERN in env and \
            env[EnvOptions.FEEDBACK_PATTERN] is not None:
            pattern = env[EnvOptions.FEEDBACK_PATTERN]
        else:
            pattern = EnvOptions.FEEDBACK_PATTERN_DEFAULT.value

		#Tag the commit so we can look it up again later if needed.
        tag = None
        if EnvOptions.GIT_TAG in env and \
            env[EnvOptions.GIT_TAG] is not None:
            tag = env[EnvOptions.GIT_TAG]
        else:
            tag = EnvOptions.GIT_TAG_DEFAULT

        commands = list()
        assign_dir = os.path.join(env[EnvOptions.STUDENT_WORK_DIR], \
            env[EnvOptions.SECTION],
            env[EnvOptions.HOMEWORK_NAME])

        if env[EnvOptions.ACTION] == EnvOptions.COMMIT_FEEDBACK:
            # First, add the instructor's feedback (based on the 
            # provided pattern, or the default is no pattern is given)
            # and then commit it to the local repo
            commands.append(generate_add_feedback(pattern, assign_dir))

            commands.append("git tag -a " + tag + " -m INSTRUCTOR_FEEDBACK_ADDED")

        elif env[EnvOptions.ACTION] == EnvOptions.UPLOAD_FEEDBACK:
            # upload the results back to the server 
            # unless DONT_UPLOAD is defined 
            # (in which case, skip this step)
            commands.append( "git push" )
            # the tags don't automatically upload, so push them separately:
            commands.append ("git push origin --tags")

        elif env[EnvOptions.ACTION] == EnvOptions.GRADING_LIST:

            grading_list = grade_list_collector ()
            grading_list_collector = grading_list.generate_grading_list_collector(tag)
            commands.append(grading_list_collector)

        course_info.git_do_core(assign_dir, commands )

        if env[EnvOptions.ACTION] == EnvOptions.GRADING_LIST:
            if grading_list.new_student_work_since_grading:
                print Fore.YELLOW + Style.BRIGHT
                print "The following items have been re-submitted by students since grading:\n"
                print Style.RESET_ALL

                for item in grading_list.new_student_work_since_grading:
                    print "\t" + item.replace(assign_dir, "")
                print "\n" + "="*20 + "\n"

            if grading_list.ungraded:
                print Fore.GREEN + Style.BRIGHT
                print "The following items haven't been graded yet:\n"
                print Style.RESET_ALL

                for item in grading_list.ungraded:
                    print "\t" + item.replace(assign_dir, "")
                print "\n" + "="*20 + "\n"

            if grading_list.graded:
                print Fore.WHITE + Style.BRIGHT
                print "The following items have been graded:\n"
                print Style.RESET_ALL

                for item in grading_list.graded:
                    print "\t" + item.replace(assign_dir, "")
                print "\n" + "="*20 + "\n"

        exit()

    else:
        print Fore.RED + Style.BRIGHT + "\nNo recognized arguments!\n"+ Style.RESET_ALL
        parser.print_help()
        exit()
