""" GitDoUtils contain functions for use in GitDo"""

from colorama import Fore
import datetime
import os
import os.path
import re
import subprocess

from colorama import init # Back,
init()

from glt.PrintUtils import print_error, print_list
from glt.PrintUtils import get_logger
logger = get_logger(__name__)

def run_command_capture_output(cmd, redirect_stderr_to_stdout = False):
    """Runs the given <cmd>, returns a string of
    string stdout, string stderr, int return code
    if <redirect_stderr_to_stdout> is True then stderr will be empty"""
    if redirect_stderr_to_stdout:
        stderr_is = subprocess.STDOUT
    else:
        stderr_is = subprocess.PIPE
    p=subprocess.Popen(cmd.split(), # shell=True,\
                bufsize = 1,\
                stderr=stderr_is,\
                stdout=subprocess.PIPE,
                universal_newlines=True)
    tuple = p.communicate()
    p.wait()
    logger.debug( "StdOut:\n" + tuple[0] )
    if stderr_is is subprocess.PIPE:
        logger.debug( "StdErr:\n" + tuple[1] )
    
    logger.debug("return code: " + str(p.returncode))
    return tuple[0], tuple[1], p.returncode

def call_shell(cmd, exit_on_fail = True):
    """Invokes git in a command-line shell"""
    logger.info( 'About to do:' + cmd)

    sz_stdout, sz_stderr, ret = run_command_capture_output(cmd)

    # git sometimes uses '1' to indicate that something didn't have
    # a problem, but didn't do anything, either
    if ret != 0 and ret != 1:
        print_error("Problem executing '"+cmd+"'\n\tIn: " + os.getcwd() +\
            "\n\tReturn code:"+str(ret))
        if exit_on_fail:
            exit()
    else:
        logger.debug('\nGit Command:\n\t' + cmd + ' - SUCCEEDED\n')

def git_clone_repo(ip_addr, project, dest_dir):
    # NOTE: I'm testing GLT with a VM (VirtualBox+Ubuntu server)
    # The VM thinks it's servername is "ubuntu".  By using
    # the environment's server IP addr setting we can get around this.

    ssh_str = "git@" + ip_addr +":"+ project.path_with_namespace+".git"
        
    cwd_prev = os.getcwd()
    os.chdir(dest_dir)
        
    # clone the newly-created project locally using 
    # normal command-line git tools
    # The '--progress' is important for actually capturing the output
    # http://stackoverflow.com/questions/39564455/pythons-popen-communicate-only-returning-the-first-line-of-stdout/39565119#39565119
    call_shell("git clone --progress " + ssh_str)
        
    os.chdir(cwd_prev)

# NOTES:
#
#   1) functions must leave the current working dir where it started
#       They can change it, they just have to change it back before
#       exiting

def upload_to_server():
    print 'upload_to_server'
    pass

class commit_feedback_collector(object):
    """A class to try and commit any files that match, and
    to collect up lists of results for the instructor"""
    def __init__(self):
        """Set up the empty lists"""
        self.ungraded = list()
        self.new_student_work_since_grading = list()
        self.graded = list()

def renumber_current_tag(target_tag):
    sz_stdout, sz_stderr, ret = run_command_capture_output(\
        "git for-each-ref refs/tags/"+target_tag)
    
    if sz_stdout:
        logger.debug( "Existing tag already found for " + target_tag \
            + " in " + os.getcwd() )
    
        # Get the SHA of the current tag (the one without the numbers)  
        # Remember that this is the SHA of the tag itself,
        # NOT the commit that it's attached to
        tags = sz_stdout.strip().split("\n")
        if len(tags) > 1:
            logger.error("Found more than 1 matching tag: " + sz_stdout)
    
        current_tag = tags[0] 
        loc = current_tag.find(" ")
        sha_tag = current_tag[:loc] 
    
        # already filtered list for the desired tag 
        # in the 'git for-each-ref' step
        sz_stdout, sz_stderr, ret = run_command_capture_output(\
        "git for-each-ref refs/tags/"+target_tag+"*")
    
        # get the highest number prior tag 
        # by going through all of them
        tags = sz_stdout.strip().split("\n")
        highest_suffix = 0
        for next_tag in tags:
            loc = next_tag.find(target_tag)
            sz_last_tag = next_tag[loc:] #get the whole tag, whatever it is
            suffix = next_tag[loc+len(target_tag):] #grab the number
    
            if suffix and int(suffix) > highest_suffix:
                    highest_suffix = int(suffix)
    
        new_prior_tag =  target_tag+ str( highest_suffix+1)
    
        p=subprocess.Popen(["git","show", sha_tag],\
            stderr=subprocess.PIPE,\
            stdout=subprocess.PIPE)
    
        sha_actual_commit, dt_tag = extract_commit_datetime(p)
        p.terminate()
    
        # rename the current commit to be the tag with the number
        # after it:
        git_cmd = "git tag -a -m INSTRUCTOR_FEEDBACK "+ \
        new_prior_tag +  " " + sha_actual_commit
        sz_stdout, sz_stderr, ret = run_command_capture_output( git_cmd )
    
        # remove existing tag:
        git_cmd = "git tag -d " + target_tag
        sz_stdout, sz_stderr, ret = run_command_capture_output( git_cmd )
    
        # now ready to tag the current commit
    else:
        logger.info( "Called renumber_current_tag, but no current tag")

class commit_feedback_collector:
    def __init__(self):
        self.no_feedback_ever = list()
        self.new_feedback = list()
        self.current_feedback_not_changed = list()
        self.current_feedback_updated = list()

    def generate_commit_feedback(self, pattern, tag, assign_dir):
        """ returns a closure that enables us to commit 
        instructor feedback """

        def commit_feedback():
            """ Go through all the directories and if we find
            a file that matches the pattern try to commit it and
            tag it. """

            # The expectation is that there's a single file that
            # matches and either it's already been committed & tagged,
            # or else that it's not yet in the repo (in which case,
            # commit and tag it)
            #
            # The full outline of what happens when is listed after
            # the code to determine if the tag exists and if any 
            # matching files still need to be committed
            #
            git_tag_cmd = "git tag -a -m INSTRUCTOR_FEEDBACK "+ tag
            path_to_repo = os.getcwd()
            regex = re.compile(pattern, flags=re.IGNORECASE)

            # First figure out if the tag already exists:
            logger.debug("Looking for tag \"" + tag + "\" in " + os.getcwd() )
            git_cmd = "git tag -l " + tag
            sz_stdout, sz_stderr, ret = run_command_capture_output(git_cmd, True)
            if sz_stdout == "":
                tagged = False
            else:
                tagged = True

            # Next, figure out if any matching files need to be committed:
            logger.debug("Looking for untracked and/or committed, modified files")
            git_cmd = "git status --porcelain"
            sz_stdout, sz_stderr, ret = run_command_capture_output(git_cmd, True)

            modified_staged = list()
            modified_not_staged = list()
            untracked = list()
            untracked_subdirs = list()

            for line in sz_stdout.splitlines():
                # line format: file:///C:/Program%20Files/Git/mingw64/share/doc/git-doc/git-status.html#_short_format
                # [index][working tree]<space>filename
                # examples of lines:
                # M File.txt            # present in repo, but not staged
                #M  NewFile.txt         # modified, added to index
                #A  SubDir/FooFile.txt  # added to index
                #?? ExtraFile.txt       # untracked
                #
                # Note that git does NOT include the contents of untracked
                # subdirs in this output, so if a new file is put into a new
                # subdir (say, SubDir2\Grade.txt) git status will list
                #?? SubDir2             # note that Grade.txt is NOT listed
                # Thus, we actually do need to traverse the file system to
                # find new files

                # does this line's file match the pattern?
                both_codes = line[0:2]
                filename = line[3:]
                match = re.search(regex, filename) 

                # If there's a new, untracked subdir
                # then we'll need to os.walk it to find
                # any matching files
                # (otherwise we can skip that)
                if both_codes == "??" and \
                    filename[len(filename)-1:] == '/':
                    untracked_subdirs.append(os.path.join(path_to_repo, filename) )

                if match:
                    code_index = line[0]
                    code_working = line[1]

                    if both_codes == "??":
                        untracked.append(filename)
                        continue
                    if both_codes == "!!":
                        print_error(filename + " (in "+os.getcwd()+"):"\
                            "\n\tWARNIG: This matched the pattern but it"\
                            " also matches something in .gitignore\n"\
                            "(This will NOT be committed now)\n")
                        continue

                    codes_changed = "M ARC"

                    if codes_changed.find(code_index) != -1:
                        # changed in the index
                        if code_working == " ":
                            modified_staged.append(filename)
                            # code_working & _index will never both be blank
                            # (that would mean no changes)
                        elif code_working == "M":
                            modified_not_staged.append(filename)

            # find matching file(s) in untracked subdirs:
            # Skip this unless there's an untracked directory
            # (these can contain more stuff, and git doesn't scan through
            # the untracked dir)
            if untracked_subdirs:
                for subdir in untracked_subdirs:
                    # walk through the subdir
                    # (starting the walk here avoids any of the
                    # files that git told us about)
                    for root, dirs, files in os.walk(subdir):
                        for name in files:

                            match = re.search(regex, name) 
                            if match:
                                path = os.path.join(root, name)
                                local_dir = path.replace(path_to_repo, "")
                                # remove the leading /
                                if local_dir[0] == os.sep: 
                                    local_dir = local_dir[1:]
                                logger.debug( "found a match at " + local_dir )
                                untracked.append( local_dir )

            #print_list(path_to_repo, modified_staged, Fore.CYAN, "modified, staged files:")
            #print_list(path_to_repo, modified_not_staged, Fore.YELLOW, "modified, unstaged files:")
            #print_list(path_to_repo, untracked, Fore.RED, "untracked files:")
            if modified_staged:
                need_commit = True
            else:
                need_commit = False

            files_to_add = modified_not_staged + untracked
            # The two 'expected' cases are listed at the top
            # Here's the full  outline:
            # if not tagged:
            #   if file absent:
            #       note and skip
            #   if file present but untracked:
            #       add, commit, tag, done
            #   if file committed and unchanged:
            #       tag it?  <ERROR>
            #
            # if tagged:
            #   file should be in repo (else error)
            #   if file not updated:
            #       note and skip
            #   if file has been updated:
            #       update existing tag to have number after it
            #       commit changes
            #       tag the current commit with the desired tag

            if not tagged:
            #   if file absent:
                if not need_commit and not files_to_add:
            #       note and skip
                    self.no_feedback_ever.append(os.getcwd() )
                    return
            #   if file present but untracked:
                else:
            #       add, commit, tag, done
                    git_cmd = "git add " + " ".join(files_to_add)
                    call_shell(git_cmd)

                    call_shell("git commit -m Adding_Instructor_Feedback")
                    sz_stdout, sz_stderr, ret = run_command_capture_output( git_tag_cmd )

                    self.new_feedback.append(os.getcwd())
                    return

            #   if file committed and unchanged:
            #       tag it?  <ERROR>
            #   we're not checking for previously committed files
            #   so we don't handle this case
            #   It *shouldn't* happen, anyways, so hopefully it won't
            #       (It might happen if the teacher commits their
            #       feedback manually)

            if tagged:
            #   file should be in repo (else error)
            #   if file not updated:
                if not need_commit and not files_to_add:
            #       note and skip
                    self.current_feedback_not_changed.append(os.getcwd() )
            #   if file has been updated:
                else:
            #       update existing tag to have number after its
                    renumber_current_tag(tag)

                    git_cmd = "git add " + " ".join(files_to_add)
                    call_shell(git_cmd)

            #       commit changes
                    call_shell("git commit -m Adding_Instructor_Feedback")

            #       tag the current commit with the desired tag:
                    sz_stdout, sz_stderr, ret = run_command_capture_output( git_tag_cmd )

                    self.current_feedback_updated.append(os.getcwd())

            #if files_to_add:
            #    # modified_staged are already in the index, ready to be committed
            #    files_to_add = modified_not_staged + untracked
            #    git_cmd = "git add " + " ".join(files_to_add)
            #    call_shell(git_cmd)
            #    call_shell("git commit -m Adding_Instructor_Feedback")
            #    # TODO: we can use a string with spaces for the -m message,
            #    # but only if we pass it as a single string object in the list
            #    # of strings (i.e., call_shell can't just call .split() )
            #    call_shell("git tag -a " + tag + " -m INSTRUCTOR_FEEDBACK_ADDED")
            #    logger.debug( "Added " + " ".join(files_to_add) )
            #    return True
            #else:
            #    print_error( "Found NO feedback to add in " + \
            #        path_to_repo.replace(assign_dir, ""))
            #    return False

        # to test:
        # run the following in a repo, then run this code
        # E:\Work\Tech_Research\Git\Tests\Batch_Files\commitFeedback.bat

        return commit_feedback

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
        logger.error( "Fatal error - found 'fatal' in tag/commit message" )
        return None, None

    output = p.stdout.readline()

    while output:
        logger.debug("LINE:" + output.strip() )
    
        if state == 1: # looking for the commit
            loc = output.lower().find("commit")
            if loc != -1:
                loc = len("commit") + loc + 1 #+1 for blank space
                SHA_commit = output[loc:].strip()
                logger.debug( 'Found commit, SHA-1=' + SHA_commit )
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
    
                logger.debug('Found date for commit:' + date_str)
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

            sha_head, dt_head = extract_commit_datetime(p)
            p.terminate()

            if sha_tag is None:
                logger.debug( "This assignment hasn't been graded yet" )
                self.ungraded.append(os.getcwd())
            elif sha_head == sha_tag:
                logger.debug( "SHA's for commits matched\n\tGRADED MOST RECENT SUBMISSION" )
                self.graded.append(os.getcwd())
            elif dt_tag < dt_head:
                logger.debug( "Instructor feedback was tagged then more work was submitted")
                self.new_student_work_since_grading.append(os.getcwd())
            else:
                print_error("This directory has graded feedback, "\
                    "but the most recent commit is prior to the instructor's"\
                    " feedback commit & tag.  This might indicate a problem"\
                    " with a timezone on the server\n\t"+\
                    os.getcwd())
            return True

        return grading_list_collector

class upload_list_collector(object):
    """A class to collect up the info about which projects were uploaded
    for the instructor"""
    def __init__(self):
        """Set up the empty lists"""
        self.unchanged = list()
        self.uploaded = list()

    def generate_upload_list_collector(self):
        def upload_list_collector():
       
            p=subprocess.Popen("git push --progress".split(),\
                stderr=subprocess.STDOUT,\
                stdout=subprocess.PIPE,
                universal_newlines=True)
            sz_stdout, sz_stderr = p.communicate()
            p.wait()

            logger.debug("In response to 'git push', got: " + sz_stdout)

            if sz_stdout.find("Everything up-to-date") != -1:
                self.unchanged.append(os.getcwd() )
            else:
                if sz_stdout.find("To git@") == -1:
                    logger.error("Expected to find \"Writing objects:\" in output but didn't")
                self.uploaded.append(os.getcwd() )

            # the tags don't automatically upload, 
            # so push them separately:
            p=subprocess.Popen("git push origin --tags --progress".split(),\
                stderr=subprocess.STDOUT,\
                stdout=subprocess.PIPE,
                universal_newlines=True)
            sz_stdout, sz_stderr = p.communicate()
            p.wait()

            logger.debug("In response to 'git push origin --tags', got: " + sz_stdout)
            return True

        return upload_list_collector