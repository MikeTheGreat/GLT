"""
    glt.py: GitLab Tool
        Tool to do bulk-manipulation of git repos (using a GitLab server)
"""

from glt.MainUtils import main

if __name__ == '__main__':
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
