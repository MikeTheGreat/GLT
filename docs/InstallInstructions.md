
# Installation Instructions #

## Local Dev: Using a Virtual Machine ##
### VirtualBox ###

1. Get [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
2. Then install it

### Ubuntu Server ###

1. Get [Ubuntu Server](http://www.ubuntu.com/download/server/install-ubuntu-server)
2. GitLab runs on Ubuntu 14.04 (the most recent LTS - Long Term Service - release), so get that version
3. Create a VirtualBox virtual machine (VM) that'll run Ubuntu
4. Change the VM's networking to ['Bridged'](http://askubuntu.com/questions/196118/how-to-access-localhost-on-virtualbox-host-machine) so that the host can access the web server on the VM
5. Run ifconfig to get the IP address of the VM, then type that into your browser

### GitLab-ce ##

1. The 'Omnibus' edition is the pro version which you need to pay for
2. The 'CE' edition is free & open source
3. [GitLab download instructions](https://about.gitlab.com/downloads/#ubuntu1404)

## Working In The Cloud: Microsoft Azure ##

You'll need to find a server that's on the Internet in order to actually enable students to access GitLab on their own.

- Remember that if you [teach using Azure you get a free, 1 year faculty pass that (as of this writing) gets you $250/month of Azure services](https://www.microsoftazurepass.com/azureu)
  - This service was discontinued

1. Create a new VM, using the new model (not the 'Classic' model)
    - In the 'find your vm image' panel, look for GitLab CE, by GitLab (ignore the older ones by Bitnami / Drone)
2. The easiest thing to do is to set up your SSH key file so that PuTTY (etc.) doesn't pester you for a password all the time
    - Using PuTTYGen you can create & save the public & private key
        - This is the SSH key if you want to SSH into the Azure server itself 
		(we'll create another one for git to use to talk to GitLab later) so including 'Azure' in the name may
		help keep things straight
    - PuTTYgen will save the public key into a text file, but it's not the correct format for pasting into Azure
    - Instead, copy the text that PuTTYGen displays (and allows you to copy) and paste that into Azure
3. The GitLabCE image will enable SSH, HTTP, and HTTPS By default
    - If you go with another image then you'll need to check that these are open and/or open them
4. You may need to connect the domain name to the machine's IP address in Azure
5. Go to the web page in your browser
    - It'll ask you for the root password
    - Set it to something
    - You can then log in as root / <your password>
6. Go to your profile settings and change the email address so it sends email to you
    - <server address - http://etc>/profile
7. Go to profile's 'SSH Keys' panel
    - <server address>/profile/keys
    - You'll need to generate another key (using PuTTYgen/ssh-keygen again)
8. At this point the GitLab server is set up. Next we need to configure git (the command-line tool). That's covered in the [GLT install document](glt_install.md)
	
#  <a name="Azure_SSH"></a> How to connect to Azure server via ssh
1. In PuTTY (not PuTTYGen), in the 'Configuration' panel that appears when you start up, copy the URL of the server (the public IP address URL) into the 'Host Name' field
2. Under Connection -> SSH --> Auth, fill in the 'Private Key for authentication' field
3. (You can also change the unreadable ANSI Blue color via Window -> Colours.  Select a colour to adjust then click 'Modify')
4. Back in 'Session', save the session for later use
5. Click on 'Open'
6. For the login name try 'root', but it'll tell you want it wants to use once you've logged in
   - It shouldn't ask for a password, since you set up the public/private RSA keys

## To update external URL
([More detailed instructions](http://stackoverflow.com/questions/19456129/how-to-change-url-of-a-working-gitlab-install/28005168#28005168))

1. [Log in to Azure server via SSH](#Azure_ssh)
2. In /etc/gitlab/gitlab.rb, change external_url 'http://gitlab.example.com'
   - Note that the '' are required (to tell Ruby that's a string), and make sure to include the http://
3. Back in bash run:
   `sudo gitlab-ctl reconfigure`
   `sudo gitlab-ctl restart`
4. You may need to wait a couple of minutes for the server to come back up (in the meantime you'll get 502 errors).

## Setting up Email ##

**TODO: This doesn't (yet) work on VirtualBox**
I've used SendGrid.com and it seems to work well.  After you create the account you're on probation for a while (maybe a couple of weeks?) and limited to 100 messages per day.  
Once you've sent a bunch of emails without problem then they give you the total of (100 messages/day * number of days in the month) at the start of each month.

1. Create an account with [SendGrid.com], or whoever you'd like.
2. [Log in to Azure server via SSH](#Azure_ssh)
3. I, personally, haven't been able to figure out how to use PostFix (the email server on Linux) with GitLab.  So instead I'm going to use SMTP.
4. Instructions for [configuring GitLab to use SMTP are here](https://gitlab.com/gitlab-org/omnibus-gitlab/blob/master/doc/settings/smtp.md).  
   Instructions for how to get your SMPT info from SendGrid [are here](https://sendgrid.com/docs/Integrate/index.html)
   http://stackoverflow.com/a/28369344/250610
5. Don't forget to do the `sudo gitlab-ctl reconfigure` and `sudo gitlab-ctl restart` once you've editted /etc/gitlab/gitlab.rb


