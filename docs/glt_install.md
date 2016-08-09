* Webdriver setup for tests

* SSH key stuff
	Don't forget to add entries to ~/.ssh/config
 

DOCUMENT: How to connect to GitLab server via ssh
(This way no username/password is needed).
1.	Git for Windows includes all the unix tools you could possibly need (including vim :)  )
    2.	In C:\Program Files\Git\usr\bin
    3.	You can use ssh-keygen.exe here
        4.	I picked the filename GitLab.priv for my private key, and GitLab.pub for my public key
        5.	Add it to your GitLab account
            6.	Profile, then SSH Keys
    7.	You can use ssh.exe, and it'll use your $HOME env var
    8.	Add an environment variable to tell GitPython to use this ssh.exe:
        * GIT_SSH_COMMAND = "C:\Program Files\Git\usr\bin\ssh.exe" -i ~/.ssh/GitLab.priv
        				Note that the quotes around the path is needed b/c of the space in Program Files
        				Note that you'll need to choose your private key (instead of GitLab.priv)
    9. Test this out by setting up the env var, then cloning a test repo
        10. Create the repo
        11. Put a file (README.md) with a single line + commit
        12. Copy the line for 'ssh' off the project page
        13. find an empty directory
        14. git clone git@ubuntu:root/bit142_assign_1.git
		     (if this doesn't work (WITHOUT A USERNAME/PASSWORD!!!) then something went wrong)
             (if this does work then (hopefully) GitPython should work fine)

* Quick note about git-credentials?
	Credentials appears to be for HTTPS, while keys can replace username/pw for ssh
	https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage
