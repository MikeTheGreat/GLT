"""Contains the CourseInfo object"""
import collections
import csv
import gitlab
import os
import shutil
#import git
import subprocess

from glt.MyClasses.StudentCollection import StudentCollection
from glt.Parsers.ParserCSV import read_student_list_csv, CsvMode
from glt.Constants import EnvOptions
from glt.PrintUtils import print_error

"""This exists to hold an assignment & it's GitLab ID"""
HomeworkDesc = collections.namedtuple('HomeworkDesc', \
    ['name', 'id'])

def call_git(cmd):
    print '\nAbout to do:\n\t' + cmd + '\n'
    ret = subprocess.call(cmd.split(), shell=True)
    if ret < 0:
        print_error("Could not execute '"+cmd+"'")
        exit()


def rmtree_remove_readonly_files(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=rmtree_remove_readonly_files)``

    This code was copied from http://stackoverflow.com/questions/2656322/shutil-rmtree-fails-on-windows-with-access-is-denied
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

class CourseInfo(object):
    """Contains information about the course, and (de)serialize to a file
    Information includes:
    * a StudentCollection for the roster (in the 'no errors' pile)
    * a list of assignments
    """

    def __init__(self, section, input_file=None):
        """ Copy the information into this object
        section: string e.g., "bit142".  Will be lower-cased"""
        # init all instance vars:
        self.section = section.lower()
        self.roster = StudentCollection()
        self.assignments = []

        if input_file is not None:
            self.read_course_info_file(input_file)

    def merge_students(self, student_list):
        """ Copies all students from the 'no error' pile into our roster"""
        # It's weird to have a method to do this one line
        # It's also weird to have other code manipulating the internal
        #      fields of an object
        self.roster.students_no_errors.extend(student_list.students_no_errors)

    def read_course_info_file(self, input_file):
        """Read file of course info, return a CourseInfo object
        input_file: file object, already open for reading
        == Basic file format: ==
        Assignments
        <A1>,<A2>,<A3><or blank line>
        Roster
        <CSV file of info>
        """

        next_line = input_file.readline()
        while next_line != "":
            next_line = next_line.strip()

            if next_line == "Assignments":
                sz_assignment = input_file.readline().strip()
                if sz_assignment != "":
                    chunks = sz_assignment.split(",")
                    i = 0;
                    while i < len(chunks)/2:                        
                        self.assignments.append( \
                            HomeworkDesc(chunks[i], chunks[i+1]))
                        i += 2

            elif next_line == "Roster":
                self.roster = read_student_list_csv(input_file, \
                    CsvMode.Internal)
                break # read_student_list_csv will read to end of file

            next_line = input_file.readline()

    def write_data_file(self, output_file_path):
        """Write our course info file information out
        output_file_path: path to file file"""
        with open(output_file_path, "w") as f_out:
            f_out.write("Assignments\n")

            for assign in self.assignments:
                f_out.write(assign.name+","+str(assign.id) )
            f_out.write("\n")

            f_out.write("Roster\n")
            csvwriter = csv.writer(f_out, quoting=csv.QUOTE_MINIMAL)
            for student in self.roster.students_no_errors:
                csvwriter.writerow([student.first_name,\
                    student.last_name,\
                    student.email,\
                    student.glid])

    def add_student_to_project(self, glc, project_id, student):
        """Tells the GitLab server to give the student 'reporter'
        level permissions on the project"""

        user_permission = { 'project_id': project_id, \
            'access_level': 20, \
            'user_id': student.glid }
        # access_level:
        # 10 = guest, 20 = reporter, 30 = developer, 40 = master
        # Anything else causes an error (e.g., 31 != developer)
        
        try:
            membership = glc.project_members.create(user_permission)
        except gitlab.exceptions.GitlabCreateError as exc:
            print_error("ERROR: unable to add " + student.first_name + " " \
                + student.last_name + " to the project!")
            print_error( str(exc.response_code)+": "+ exc.error_message)
            return False
        return True

    def create_homework(self, glc, env):
        """ Attempt to create a homework assignment for a course
        by creating a project in the GitLab server, 
        adding a record of the assignment to the course data file, 
        and giving all current students access to the project"""

        proj_name = env[EnvOptions.HOMEWORK_NAME].replace(" ", "").lower()
        proj_name = self.section + "_" + proj_name

        project_data = {'name': proj_name, \
            'issues_enabled': False, \
            'wall_enabled': False, \
            'merge_requests_enabled': False, \
            'wiki_enabled': False, \
            'snippets_enabled': False, \
            'visibility_level': False, \
            'builds_enabled': False, \
            'public_builds': False, \
            'public': False, \
            'visibility_level': 0, \
            }

        # print(project_data)

        # If the user's account already we'll get an error here:
        try:
            project = glc.projects.create(project_data)          
            #project = glc.projects.get(37) 
        except gitlab.exceptions.GitlabCreateError as exc:
            print_error("unable to create project " + proj_name)
            print_error( str(exc.response_code)+": "+ str(exc.error_message))

        print "Created : " + project.name_with_namespace
        #print project

        # Remember that we created the assignment
        # This will be serialized to disk (in the section's data file)
        # at the end of this command
        self.assignments.append( HomeworkDesc( proj_name, project.id ) )
        self.assignments.sort()

        # add each student to the project as a reporter
        for student in self.roster.students_no_errors:

            if self.add_student_to_project(glc, project.id, student):
                print 'Added ' + student.first_name + " " + student.last_name
            else:
                print_error('ERROR: Unable to add ' + student.first_name + \
                            " " + student.last_name)
                
        # The ssh connection string should look like:
        #   git@ubuntu:root/bit142_assign_1.git
        sshStr = "git@" + env[EnvOptions.SERVER_IP_ADDR] +":"+ project.path_with_namespace+".git"
        # NOTE: I'm testing GLT with a VM (VirtualBox+Ubuntu server)
        # The VM thinks it's servername is "ubuntu".  By using
        # the environment's server IP addr setting we can get around this.
        print "About to clone from: " + sshStr

        cwd_prev = os.getcwd()
        os.chdir(env[EnvOptions.TEMP_DIR])
        starter_project_name = "STARTER"

        # clone the newly-created project locally
        # so that we can use normal command-line git tools here
        #
        call_git("git clone " + sshStr)

        # next, move into the directory 
        # (so that subsequent commands affect the new repo)
        os.chdir(env[EnvOptions.TEMP_DIR]+os.path.sep+project.name)

		# Next, add a 'remote' reference in the newly-cloned repo
		#       to the starter project on our local machine:
        call_git("git remote add "+starter_project_name+" "\
            +env[EnvOptions.HOMEWORK_DIR])

        # Get all the files from the starter project:
        call_git("git fetch " + starter_project_name)

        # Merge the starter files into our new project:
        call_git("git merge "+starter_project_name+"/master")

        # Clean up (remove) the remove reference
        # TODO: Do we actually need to do this? Refs don't get pushed,
        #       and we delete the whole thing in the next step...
        call_git("git remote remove "+starter_project_name)

        # Push the changes back up to GitLab
        call_git("git push")

        # Clear the temporary directory
        os.chdir(cwd_prev)
        shutil.rmtree(env[EnvOptions.TEMP_DIR]+project.name, onerror=rmtree_remove_readonly_files)


