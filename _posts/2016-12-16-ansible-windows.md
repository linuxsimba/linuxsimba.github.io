---
title: Creating Ansible Windows Modules
tags: ['ansible','windows']
---

This is an example of how to create a Ansible Windows Module.
This example how to add an AD User to a AD Group on a Windows 2012 Server in an idempotent way.

## Requirements

#### Ansible Version
Modules work from version 2.0  to version 2.2

#### WinRM Authentication
Like SSH for Linux, WinRM allows you log into a Microsoft Windows Server host. Read the [Ansible Windows Support page](http://docs.ansible.com/ansible/intro_windows.html) for more details on how to set this up. One thing though that
WinRM ansible support doesn't cover is using Certificate based Authentication instead
of password based authentication. I would like to experiment with this and possibly
blog about this in the future.

#### PowerShell
Ansible uses PowerShell to program the server, much in the same way Python is used to program a Linux host. Windows Server 2012 and higher have PowerShell enabled by default. Only thing you  need to be sure is that the user running PowerShell scripts has permission to do so. Checkout the [Ansible Windows Support page](http://docs.ansible.com/ansible/intro_windows.html) for more details.

## Create the Module

#### Powershell Part

Begin with this simple example to get you started. This Gist shows the ".ps1" part.
{% gist linuxsimba/58b4c03531ef6efcbe860455c1218a79 %}


#### Documentation Part
Next create a sister document that is a ".py". It will contain the Ansible documentation part of the module.

{% gist linuxsimba/791f308e6d7831d31c6ce6f056922772 %}

For more examples, check out [ the Linuxsimba Windows Ansible Modules repo](https://github.com/linuxsimba/ansible-window-modules).
