---
title: "Ansible Windows Automation - Double Hop Issues"
tags: ["credssp", "ansible", "windows"]
---

I encountered the Microsoft [Double Hopping](https://blogs.msdn.microsoft.com/knowledgecast/2007/01/31/the-double-hop-problem)
 issue recently when attempting to automate a Remote Desktop Services deployment.


 I first used the `basic` login mechanism and ran a simple playbook to check the Remote Desktop Service

 ```
 - hosts: adserver
   gather_facts: no
   tasks:
     - win_shell: Get-rdserver
 ```

 The results were weird. It didn't error ou. Just said it could not find the RD Connection Broker. But the broker was the server I was connecting to??

 ```
 "stderr": "get-rdserver : The RD Connection Broker server is not available.
 Verify that you can connect to
 the RD Connection Broker server.
 At line:1 char:1
       get-rdserver
 ```

 If I run this same command from the Windows Server it works !??

 ```
  > get-rdserver
     Server                                             Roles
    ------                                             -----                                          
    LINUXSIMBAAD.LINUXSIMBA.LOCAL                      {RDS-RD-SERVER, RDS-CONNECTION-BROKER, RDS-W...",

 ```

 After some web searching, it became clear the issue was double hopping.

The [Ansible Windows  Automation documentation](http://docs.ansible.com/ansible/devel/user_guide/windows_winrm.html)  says the following about the issue.
> Set ansible\_winrm\_transport to credssp or kerberos (with ansible\_winrm\_kerberos\_delegation=true) to bypass the double hop issue and access network resources

I set the winrm transport protocol to credSSP,  after enabling credSSP WinRM support, using the [Ansible Winrm configuration script](https://github.com/ansible/ansible/blob/devel/examples/scripts/ConfigureRemotingForAnsible.ps1). I'm too lazy to setup kerberos on my Ansible server. Happy to report ... **IT WORKED**!

> *Note to self*:
 Always use Kerberos or CredSSP when doing Ansible Automation for Windows!
