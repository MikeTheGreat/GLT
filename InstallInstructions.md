
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

## Dev In The Cloud: Microsoft Azure ##

* Remember that if you [teach using Azure you get a free, 1 year faculty pass that (as of this writing) gets you $250/month of Azure services](https://www.microsoftazurepass.com/azureu)
* Create a new VM, using the new model
* In the VM Depot **IGNORE** the GitLab image and instead use the Ubuntu one (again, use 14.04 since it's the most recent LTS that GitLab runs on)
* The easiest thing to do is to set up your SSH key file so that PuTTY (etc.) doesn't pester you for a password all the time
* By default the VM only has the SSH port open, so you'll need to **enable HTTP on the VM**
* You may need to connect the domain name to the machine
* You'll need to SSH into the VM, and then follow the directions below for installing GitLab-ce

## GitLab-ce ##

1. The 'Omnibus' edition is the pro version which you need to pay for
2. The 'CE' edition is free & open source
3. [GitLab download instructions](https://about.gitlab.com/downloads/#ubuntu1404)

