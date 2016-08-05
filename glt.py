"""
    glt.py: GitLab Tool
        Tool to do bulk-manipulation of git repos (using a GitLab server)
"""

import subprocess
from glt.MainUtils import main

#from git import Repo
import git

if __name__ == '__main__':
    #main()
    #retVal = subprocess.call(['git','help'], shell=True)
    #retVal = subprocess.call(['ls', '-l'], shell=True, cwd='e:\pers')
    #print '='*20
    
    #print retVal
    # "http://192.168.56.101/root/bit142_assign_1.git/", 
    repo = git.Repo.clone_from( r"git@192.168.56.101:root/bit142_assign_1.git", r"E:\Work\Tech_Research\DELETEME_Git")
    
    #git clone http://192.168.56.101/root/bit142_assign_1.git

#cd existing_folder
#git init
#git remote add origin http://ubuntu/root/bit142_assign_1.git
#git add .
#git commit
#git push -u origin master
