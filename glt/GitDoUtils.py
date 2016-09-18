""" GitDoUtils contain functions for use in GitDo"""

import datetime
import os
import os.path
import re
import subprocess

from colorama import init # Back,
init()

from glt.MyClasses.CourseInfo import call_shell
from glt.PrintUtils import print_error

# NOTES:
#
#   1) functions must leave the current working dir where it started
#       They can change it, they just have to change it back before
#       exiting

def upload_to_server():
    print 'upload_to_server'
    pass

def generate_add_feedback(pattern, assign_dir):
    def add_feedback():
        print "looking for " + pattern
        files_to_add = list()
        regex = re.compile(pattern, flags=re.IGNORECASE)

        path_to_repo = os.getcwd()

        for root, dirs, files in os.walk(os.getcwd()):
            for name in files:
                match = re.search(regex, name) 
                if match:
                    path = os.path.join(root, name)
                    local_dir = path.replace(path_to_repo, "")
                    # remove the leading /
                    if local_dir[0] == os.sep: 
                        local_dir = local_dir[1:]
                    print "found a match at " + local_dir
                    files_to_add.append( local_dir )

        if files_to_add:
            git_cmd = "git add " + " ".join(files_to_add)
            call_shell(git_cmd)
            call_shell("git commit -m Adding_Instructor_Feedback")
            print "Added " + " ".join(files_to_add)
            return True
        else:
            print_error( "Found NO feedback to add in " + \
                path_to_repo.replace(assign_dir, ""))
            return False

    return add_feedback

def print_dir():
    print "print_dir called in " + os.getcwd()


def extract_commit_datetime(p):
    """Given a Git stdout message for a tag or commit, extract
    the SHA-1 ID for the commit and the date of the underlying commit"""
    state = 1 # looking for the commit
    # get output from process "Something to print"

    # Did git report a fatal error?
    output = p.stderr.readline() # returns empty string if no error
    loc = output.lower().find("fatal")
    if loc != -1:
        #print "Fatal error"
        return None, None

    output = p.stdout.readline()

    while output:
        # print "LINE:" + output.strip()
    
        if state == 1: # looking for the commit
            loc = output.lower().find("commit")
            if loc != -1:
                loc = len("commit") + loc + 1 #+1 for blank space
                SHA_commit = output[loc:]
                # print 'Found commit, SHA-1=' + SHA_commit
                state = 2 # looking for the date of the commit
        if state == 2: # looking for the date of the commit
            loc = output.lower().find("date:")
            if loc != -1:
                loc = len("date:") + loc + 1
                date_str = output[loc:].strip()
    
                # Lop off the 'Wed' at the start:
                loc = date_str.find(' ')
                date_str = date_str[loc:].strip()
    
                # Lop off the '-0700' at the end:
                loc = date_str.rfind(' ')
                date_str = date_str[:loc].strip()
    
                # print 'Found date for commit:' + date_str
                # Thu Sep 15 22:18:40 2016 -0700
                dt = datetime.datetime.strptime(date_str, "%b %d %H:%M:%S %Y")
    
                state = 3 # done!
        if state == 3: # done!
            # print "Finished!"
            return SHA_commit, dt
    
        output = p.stdout.readline()

    # We should exit the loop via state 3
    # If we don't then we didn't find one or more of the things
    # we were looking for then send back nothing
    return None, None


class grade_list_collector(object):
    """A class to collect up the 'what needs to be graded' info 
    for the instructor"""
    def __init__(self):
        """Set up the empty lists"""
        self.ungraded = list()
        self.new_student_work_since_grading = list()
        self.graded = list()

    def generate_grading_list_collector(self, tag):
        def grading_list_collector():
#            print "Looking for tag: " + tag            
            p=subprocess.Popen(["git","show", tag],\
                stderr=subprocess.PIPE,\
                stdout=subprocess.PIPE)
            # write 'a line\n' to the process
            #p.stdin.write('a line\n')

            sha_tag, dt_tag = extract_commit_datetime(p)
            p.terminate()

            p=subprocess.Popen(["git","show", "head"],\
                stderr=subprocess.PIPE,\
                stdout=subprocess.PIPE)
            # write 'a line\n' to the process
            #p.stdin.write('a line\n')

            sha_head, dt_head = extract_commit_datetime(p)
            p.terminate()

            if sha_tag is None:
                #print "This assignment hasn't been graded yet"
                self.ungraded.append(os.getcwd())
            elif sha_head == sha_tag:
                #print "SHA's for commits matched\n\tGRADED MOST RECENT SUBMISSION"
                self.graded.append(os.getcwd())
            elif dt_tag < dt_head:
                #print "Instructor feedback was tagged then more work was submitted"
                self.new_student_work_since_grading.append(os.getcwd())
            else:
                print_error("This directory has graded feedback, "\
                    "but the most recent commit is prior to the instructor's"\
                    " feedback commit & tag.  This might indicate a problem"\
                    " with a timezone on the server\n\t"+\
                    os.getcwd())
            #TODO: SHA's don't match, but dt_tag >= dt_head?
            return True

        return grading_list_collector
