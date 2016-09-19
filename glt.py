"""
    glt.py: GitLab Tool
        Tool to do bulk-manipulation of git repos (using a GitLab server)
"""

from colorama import Fore, Style, init
init()

from glt.MainUtils import main

from glt.PrintUtils import get_logger
logger = get_logger(__name__)

import os
import subprocess

if __name__ == '__main__':
    main()

    #dir = "E:\\Work\\Tech_Research\\Git\\Misc\\StudentDownloads\\BIT142\\Assign_2\\VonP, Mike\\"
    #os.chdir(dir)
    #git_cmd = "git clone --progress git@192.168.56.101:Mike_VonP/bit142_assign_2.git"

    #print "SUBPROCESS.CALL" + "="*20
    #ret = subprocess.call(git_cmd.split(), shell=True)

    #print "SUBPROCESS.POPEN" + "="*20
    #p=subprocess.Popen(git_cmd.split(), shell=True)
    #p.wait()

    #print "SUBPROCESS.POPEN, COMMUNICATE" + "="*20
    #p=subprocess.Popen(git_cmd.split(), # shell=True,\
    #            bufsize = 1,\
    #            stderr=subprocess.PIPE,\
    #            stdout=subprocess.PIPE,
    #            universal_newlines=True)
    #tuple = p.communicate()
    #p.wait()
    #logger.debug( "StdOut:\n" + tuple[0] )
    #logger.debug( "StdErr:\n" + tuple[1] )


# test with:
# listProjects
# addStudents BIT142 E:\Work\Tech_Research\Git\SampleInputs\Text\StudentList_Short_AllGood.csv
# deleteClass BIT142
# addHomework BIT142 Assign_1 E:\Work\Tech_Research\Git\SampleInputs\Git_Repos\A1
# download BIT142 Assign_1
# addHomework BIT142 Assign_2 E:\Work\Tech_Research\Git\SampleInputs\Git_Repos\A2
# download BIT142 all
# <add a YOUR_GRADE.txt file to a repo>
# commitFeedback BIT142 Assign_1
# uploadFeedback BIT142 Assign_1


#SUBPROCESS.CALL====================
#Cloning into 'bit142_assign_2'...
#remote: Counting objects: 9, done.
#remote: Compressing objects: 100% (4/4), done.
#remote: Total 9 (delta 0), reused 0 (delta 0)
#Receiving objects: 100% (9/9), done.
#Checking connectivity... done.
#
#SUBPROCESS.POPEN====================
#Cloning into 'bit142_assign_2'...
#remote: Counting objects: 9, done.
#remote: Compressing objects: 100% (4/4), done.
#remote: Total 9 (delta 0), reused 0 (delta 0)
#Receiving objects: 100% (9/9), done.
#Checking connectivity... done.
#
