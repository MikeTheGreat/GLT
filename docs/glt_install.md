# How to set up GLT to connect to the GitLab server via ssh #
This way no username/password is needed.
Git for Windows includes all the unix tools you could possibly need (including vim :), so start by installing that

2.	In C:\Program Files\Git\usr\bin
3.	You can use ssh-keygen.exe here
    -	I picked the filename GitLab.priv for my private key, and GitLab.pub for my public key
    -	Add it to your GitLab account
        -	Click on Profile, then SSH Keys
7.	You can use ssh.exe, and it'll use your $HOME env var
8.	Add an environment variable to tell GLT to use this ssh.exe:
    - GIT_SSH_COMMAND = "C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/GitLab.priv.  
	Note that the quotes around the path is needed b/c of the space in Program Files
	Note that you'll need to choose your private key (instead of GitLab.priv)
    - If you're curious, this is actually telling git (not GLT) to use this as the SSH command :)
1. Test this out by setting up the env var, then cloning a test repo
   1. Create the repo
   2. Put a file (README.md) with a single line + commit
	  - There's no 'Files' option in the left column until you create a file.  
		You can do this by clicking on the 'Project' option (left column), then clicking on the 
		Plus sign to the right of the textbox containing the ssh string (in the middle of the page)
			
   3. Copy the line for 'ssh' off the project page
   4. find an empty directory
   5. git clone git@ubuntu:root/bit142_assign_1.git
	  - MAY NEED TO ADJUST HOST NAME!!!
	  - If you get a message about
		    The authenticity of host 'ccc-git-lab-server.westus.cloudapp.azure.com (52.160.111.113)' can't be established.
			ECDSA key fingerprint is SHA256:TZ94k8irfpJTkCoUdTDj6xfNSnorx1pAWH6ZSjWoKkw.
			Are you sure you want to continue connecting (yes/no)? yes
		Just type 'yes'.  You should then see:
			Warning: Permanently added 'ccc-git-lab-server.westus.cloudapp.azure.com,52.160.111.113' (ECDSA) to the list of known hosts.
		    (if this doesn't work (WITHOUT A USERNAME/PASSWORD!!!) then something went wrong)
            (if this does work then (hopefully) GLT  should work fine)

-------------------------------------------------------------------------------
## Stuff that's not finished :)

* Add a quick note about git-credentials?
	Credentials appears to be for HTTPS, while keys can replace username/pw for ssh
	https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage

* Webdriver setup for tests

* SSH key stuff
	Don't forget to add entries to ~/.ssh/config
