# Typical Usage #

## An easy way to check your connection to your GitLab server ##
set up your .gltrc so it includes the server_ip, username and (optionally) password
Then run
`glt.py listProjects`
This will connect to the server and list off all the projects.  
You'll get an error if stuff isn't configured correctly

## Creating a class ##

1. create on server
    * Note about .gltrc file
        * Location(s) of the file
        * Intention that it's editted by the user
2. stash info into data file for section
    * Note about data file - for internal use only
    * Should be human-readable, but GLT will overwrite this repeatedly and without warning		

#### Sidebar: idempotent ops, adding to existing homework assignments ####

* When you create a class & there are already accounts for some students nothing (bad) happens
* When you add students to a class this way GLT will check if there are any homework projects, and if so add the new students to those projects

## Creating a homework assignment ##

1. create a project in the GitLab server
2. add a record of the assignment to the course data file
3. giving all current students access to the project
4. Add starter project to the server
    * By cloning the server's project, merging the (local) starter project in, then pushing it back to the server
 

