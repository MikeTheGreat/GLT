"""Contains the CourseInfo object"""
import datetime
import collections
import csv
import os
import shutil
#import git
import subprocess
import gitlab

from glt.MyClasses.Student import Student
from glt.MyClasses.StudentCollection import StudentCollection
from glt.Parsers.ParserCSV import read_student_list_csv, CsvMode
from glt.Constants import EnvOptions
from glt.PrintUtils import print_error

# """This exists to hold an assignment & it's GitLab ID"""
HomeworkDesc = collections.namedtuple('HomeworkDesc', \
    ['name', 'internal_name', 'id'])

# """This exists to hold the info relevant to a recently 
# downloaded/updated student project"""
StudentHomeworkUpdateDesc = collections.namedtuple('StudentHomeworkUpdateDesc', \
    ['student', 'student_dest_dir', 'project', 'timestamp'])

def call_git(cmd):
    """Invokes git in a command-line shell"""
    print '\nAbout to do:\n\t' + cmd + '\n'
    ret = subprocess.call(cmd.split(), shell=True)
    if ret != 0:
        print_error("Problem executing '"+cmd+"'\n\tReturn code:"+str(ret))
        exit()
    else:
        print '\nGit Command:\n\t' + cmd + ' - SUCCEEDED\n'

def git_clone_repo(ip_addr, project, dest_dir):
    # NOTE: I'm testing GLT with a VM (VirtualBox+Ubuntu server)
    # The VM thinks it's servername is "ubuntu".  By using
    # the environment's server IP addr setting we can get around this.

    ssh_str = "git@" + ip_addr +":"+ project.path_with_namespace+".git"
        
    cwd_prev = os.getcwd()
    os.chdir(dest_dir)
        
    # clone the newly-created project locally using 
    # normal command-line git tools
    call_git("git clone " + ssh_str)
        
    os.chdir(cwd_prev)

def rmtree_remove_readonly_files(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=rmtree_remove_readonly_files)``

    This code was copied from
    http://stackoverflow.com/questions/2656322/shutil-rmtree-fails-on-windows-with-access-is-denied
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
                    i = 0
                    while i < len(chunks):
                        self.assignments.append( \
                            HomeworkDesc(chunks[i],chunks[i+1],int(chunks[i+2])))
                        i += 3

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
                f_out.write(assign.name+","+assign.internal_name+","+str(assign.id))
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

        user_permission = {'project_id': project_id, \
            'access_level': 20, \
            'user_id': student.glid}
        # access_level:
        # 10 = guest, 20 = reporter, 30 = developer, 40 = master
        # Anything else causes an error (e.g., 31 != developer)

        try:
            #membership = glc.project_members.create(user_permission)
            glc.project_members.create(user_permission)
        except gitlab.exceptions.GitlabCreateError as exc:
            print_error("ERROR: unable to add " + student.first_name + " " \
                + student.last_name + " to the project!")
            print_error(str(exc.response_code)+": "+ exc.error_message)
            return False
        return True

    def homework_to_project_name(self, hw_name):
        """Given hw_name (e.g., "Assign_1"), produce the GitLab project name.
        Project name is {section_name}_{hw_name.lower()}"""
        proj_name = hw_name.replace(" ", "").lower()
        proj_name = self.section + "_" + proj_name
        return proj_name

    def create_homework(self, glc, env):
        """ Attempt to create a homework assignment for a course
        by creating a project in the GitLab server,
        adding a record of the assignment to the course data file,
        and giving all current students access to the project"""
        proj_name = self.homework_to_project_name( \
            env[EnvOptions.HOMEWORK_NAME])

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
            }

        # print(project_data)

        # If the user's account already we'll get an error here:
        try:
            project = glc.projects.create(project_data)
            print "Created : " + project.name_with_namespace

            # Remember that we created the assignment
            # This will be serialized to disk (in the section's data file)
            # at the end of this command
            self.assignments.append(HomeworkDesc(env[EnvOptions.HOMEWORK_NAME], \
                proj_name, project.id))
            self.assignments.sort()

        except gitlab.exceptions.GitlabCreateError as exc:

            # If the project already exists, look up it's info
            # and then proceed to add students to it
            if exc.error_message['name'][0].find("already been taken") >= 0:
                proj_path = env[EnvOptions.USERNAME]+"/"+ proj_name
                project = glc.projects.get(proj_path)
                print "Found existing project " + project.name_with_namespace
            else:
                # For anything else, just exit here
                print_error("Unable to create project " + proj_name)
                print_error(str(exc.response_code)+": "+ str(exc.error_message))
                exit()

        #print project

        # add each student to the project as a reporter
        for student in self.roster.students_no_errors:

            if self.add_student_to_project(glc, project.id, student):
                print 'Added ' + student.first_name + " " + student.last_name
            else:
                print_error('ERROR: Unable to add ' + student.first_name + \
                            " " + student.last_name)

        cwd_prev = os.getcwd()
        dest_dir = os.path.join(env[EnvOptions.TEMP_DIR], project.name)
        try:
            # This is the part where we add the local, 'starter' repo to the
            # GitLab repo.
            # This should be idempotent:
            # If you already have a GitLab repo, and...
            # 1)    If the local, starter repo and the GitLab repo are the
            #       same then no changes will be made to the GitLab repo
            # 2)    If the local, starter repo is different from the GitLab
            #       repo  then we'll update the existing GitLab repo

            git_clone_repo(env[EnvOptions.SERVER_IP_ADDR],\
                project, env[EnvOptions.TEMP_DIR])

            starter_project_name = "STARTER"

            # next, move into the directory
            # (so that subsequent commands affect the new repo)            
            os.chdir(dest_dir)
            # TODO: Above line should be os.path.join
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

        finally:
            # Clear the temporary directory
            os.chdir(cwd_prev)
            shutil.rmtree(dest_dir, onerror=rmtree_remove_readonly_files)

    def download_homework(self, glc, env):

        if not self.assignments:
            print_error( self.section + " doesn't have any assignments "\
               " to download")
            exit()

        updated_student_projects = list()

        # After this, one of three things is true:
        #   1) hw_to_download is a list of all the homework project
        #   2) hw_to_download is a list of exactly one homework project
        #   3) EnvOptions.HOMEWORK_NAME didn't match anything and we exit
        #
        # 'homework project' is a copy of the HomeworkDesc named tuple (name,id)
        
        if env[EnvOptions.HOMEWORK_NAME].lower() == 'all':
            # we're going to make a new list with all the projects
            hw_name = 'all'
            hw_to_download = list(self.assignments)
        else:
            # we're going to make a new list that should match just one
            # homework assignment
            hw_name = self.homework_to_project_name(env[EnvOptions.HOMEWORK_NAME])
            hw_to_download = [item for item in self.assignments if item.name == hw_name]

        if not hw_to_download:# if list is empty
            print_error( env[EnvOptions.HOMEWORK_NAME] + " (internal name: " +\
                hw_name + " ) doesn't match any of the have any assignments"\
               " in section " + env[EnvOptions.SECTION])
            exit()
        
        # First make sure that we can at least create the 'root'
        # directory for saving all the homework projects:
        dest_dir = os.path.join(env[EnvOptions.STUDENT_WORK_DIR], \
            env[EnvOptions.SECTION])
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir) # throws an exception on fail

        # Next, go through all the projects and see which
        # (if any) were forked from the target project
        projects = glc.projects.all()
        if not projects:
            print "There are no projects present on the GitLab server"
            return

        print "Found the following projects:\n"
        for project in projects:
            print project.name_with_namespace + " ID: " + str(project.id)

            # See if the project matches any of the
            # 1/many projects that we're trying to download
            forked_project = None
            if hasattr(project, 'forked_from_project'):
                for hw in hw_to_download:
                    if project.forked_from_project['id'] == hw.id:
                        forked_project = hw
                        break

            if forked_project is None:
                print "\tNOT a forked project\n"
                continue

            print "\tProject was forked from " + forked_project.name \
                + " (ID:"+str(forked_project.id)+")"

            #project.pretty_print(1)
            #print "="*20
            #print

            owner_name = project.path_with_namespace.split('/')[0]
            student = Student(username=owner_name, id=project.owner.id)

            # make a dir for this particular project
            student_dest_dir = os.path.join(dest_dir, \
                forked_project.name, \
                student.get_dir_name())
            if not os.path.isdir(student_dest_dir):
                os.makedirs(student_dest_dir)
            else:
                # if there's already a .git repo there then refresh (pull) it 
                # instead of cloning it

                repo_exists = False
                for root, dirs, files in os.walk(student_dest_dir):
                    for dir in dirs:
                        if dir == '.git':
                            git_dir = os.path.join( root, dir)
                            print "Found an existing repo at " + git_dir
                            cwd_prev = os.getcwd()
                            os.chdir(root)
            
                            # Update the repo
                            call_git("git pull")

                            os.chdir(cwd_prev)
                        
                            repo_exists = True
                        if repo_exists: break
                    if repo_exists: break

                if repo_exists:
                    continue # don't try to clone it again
            
            # clone the repo into the project
            # The ssh connection string should look like:
            #   git@ubuntu:root/bit142_assign_1.git
            git_clone_repo(env[EnvOptions.SERVER_IP_ADDR], \
                project, student_dest_dir)

            # add the repo into the list of updated projects
            updated_student_projects.append( \
                StudentHomeworkUpdateDesc(student, \
                          student_dest_dir, project, \
                          datetime.datetime.now()) )

        # return the list of updated projects
        return updated_student_projects