"""
    glt.py: GitLab Tool
        Tool to do bulk-manipulation of git repos (using a GitLab server)
"""

import os
import subprocess
#from colorama import Fore, Style, init
#init()

from glt.MainUtils import main
#from glt.PrintUtils import get_logger
#logger = get_logger(__name__)


if __name__ == '__main__':
    #cur = os.getcwd()
    #os.chdir("E:\\Work\\Student_Work\\BIT_142_New\\PCE10_Git\\BIT142\\PCE_10\\Tran, Jack,PCE_10, FROM GIT\\bit142_pce_10")
    #p=subprocess.Popen(["git","show", "head"],\
    #            stderr=subprocess.PIPE,\
    #            stdout=subprocess.PIPE)
    #output = p.stderr.readline() 
    #output2 = p.stdout.readline()
    #p.terminate()
    #os.chdir(cur)

    main()

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


# 2016 Fall Extra Credit:
# addHomework BIT142 PCE_10 E:\Work\Website\Courses\BIT142\Lessons\Lesson_110_Git\PCEs\DO_NOT_UPLOAD\Using_Git
#       Note: above path leads to root dir of VS project, which contains the .git dir
#       Reminder: This will only commit whatever's stored in GIT (it will NOT) add whatever's
#           In the filesystem
#       TODO: Better error message when this does NOT work :)

# addStudents BIT142 E:\Work\Tech_Research\Git\SampleInputs\2016_Fall\StudentList_ExtraCredit_1.csv
# addStudents BIT142 E:\Pers\Dropbox\Work\Courses\BIT_142\2016Fall\class_roster.html
# download BIT142 PCE_10
# gitdo BIT142 PCE_10 E:\Work\Student_Work\BIT_142_New\GitGrading.bat
# gitdo BIT142 PCE_10 E:\Work\Student_Work\BIT_142_New\GitGradingCleanup.bat
# gt isn't putting the feedback in the repros unless I give it dir right above the students
# gitdo BIT142 PCE_10 E:\Work\Student_Work\BIT_142_New\GitMoveFeedbackDown.bat
# commitFeedback BIT142 PCE_10

# skip the next stuff: (This ommits the tag that we'll use to figure out if the repo has instructor feedback or not)
# gitdo BIT142 PCE_10 git add -A
# gitdo BIT142 PCE_10 git commit -m "INSTRUCTOR FEEDBACK"
# gitdo BIT142 PCE_10 git commit -m INSTRUCTOR_FEEDBACK

# Then do this:
# uploadFeedback BIT142 PCE_10